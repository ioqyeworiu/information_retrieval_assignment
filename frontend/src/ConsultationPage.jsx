import { useEffect, useState } from 'react'
import { authedFetch, clearAuthToken } from './auth'
import './ConsultationPage.css'

export function ConsultationPage({ onBack, onLogout }) {
    const [chatInput, setChatInput] = useState('')
    const [isHistoryOpen, setIsHistoryOpen] = useState(true)
    const [chatMessages, setChatMessages] = useState([
        {
            sender: 'assistant',
            text: 'Chào bạn, mình là trợ lý tư vấn. Bạn muốn hỏi về mục tiêu tập luyện, lịch tập hay dinh dưỡng?',
        },
    ])
    const [sessions, setSessions] = useState([])
    const [loadingSessions, setLoadingSessions] = useState(false)
    const [sessionsError, setSessionsError] = useState('')
    const [selectedSessionId, setSelectedSessionId] = useState('')
    const [loadingSessionChat, setLoadingSessionChat] = useState(false)
    const [sessionChatError, setSessionChatError] = useState('')
    const [sendingMessage, setSendingMessage] = useState(false)

    useEffect(() => {
        loadSessions()
    }, [])

    async function loadSessions() {
        setLoadingSessions(true)
        setSessionsError('')

        try {
            const response = await authedFetch('/api/public/v1/sessions', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            })

            const payload = await response.json().catch(() => ({}))

            if (!response.ok) {
                throw new Error(payload?.message || 'Lỗi khi lấy danh sách session')
            }

            const sessionsData = payload?.data || []
            setSessions(Array.isArray(sessionsData) ? sessionsData : [])
        } catch (error) {
            setSessionsError(error instanceof Error ? error.message : 'Lỗi không xác định')
        } finally {
            setLoadingSessions(false)
        }
    }

    function getSessionIdValue(session) {
        if (typeof session === 'string' || typeof session === 'number') {
            return String(session)
        }

        const rawId = session?.session_id ?? session?.sessionId ?? session?.id
        return rawId === undefined || rawId === null ? '' : String(rawId)
    }

    function parsePythonEscapedText(content) {
        return content
            .replace(/\\n/g, '\n')
            .replace(/\\r/g, '\r')
            .replace(/\\t/g, '\t')
            .replace(/\\"/g, '"')
            .replace(/\\'/g, "'")
            .replace(/\\\\/g, '\\')
            .trim()
    }

    function extractQuotedUserMessage(content) {
        const quotedMatch = content.match(/"([^"]+)"/)

        if (quotedMatch && quotedMatch[1]) {
            return quotedMatch[1].trim()
        }

        return content.split('\n')[0]?.trim() || content.trim()
    }

    function parseSessionDump(rawText) {
        const normalizedText = String(rawText)
        const pattern = /(HumanMessage|AIMessage)\(content=(['"])([\s\S]*?)(?<!\\)\2,/g
        const parsedMessages = []
        let match = pattern.exec(normalizedText)

        while (match) {
            const role = match[1] === 'HumanMessage' ? 'user' : 'assistant'
            const parsedContent = parsePythonEscapedText(match[3])
            const content = role === 'user'
                ? extractQuotedUserMessage(parsedContent)
                : parsedContent

            if (content) {
                parsedMessages.push({ sender: role, text: content })
            }

            match = pattern.exec(normalizedText)
        }

        return parsedMessages
    }

    function normalizeSessionMessages(data) {
        if (typeof data === 'string') {
            const parsed = parseSessionDump(data)
            return parsed.length > 0 ? parsed : [{ sender: 'assistant', text: data }]
        }

        if (!Array.isArray(data)) {
            return []
        }

        const normalized = data
            .map((item) => {
                if (typeof item === 'string') {
                    const parsedItem = parseSessionDump(item)
                    return parsedItem.length > 0 ? parsedItem : [{ sender: 'assistant', text: item }]
                }

                if (item && typeof item === 'object') {
                    const text = item.content ?? item.text ?? ''
                    const role = String(item.type || item.role || '').toLowerCase().includes('human')
                        ? 'user'
                        : String(item.type || item.role || '').toLowerCase().includes('ai')
                            ? 'assistant'
                            : 'assistant'

                    if (text) {
                        const parsedText = parsePythonEscapedText(String(text))
                        const normalizedText = role === 'user'
                            ? extractQuotedUserMessage(parsedText)
                            : parsedText

                        return [{ sender: role, text: normalizedText }]
                    }

                    const parsedObjectString = parseSessionDump(String(item))
                    return parsedObjectString.length > 0 ? parsedObjectString : []
                }

                const parsedGeneric = parseSessionDump(String(item))
                return parsedGeneric.length > 0 ? parsedGeneric : []
            })
            .flat()

        return normalized
    }

    function normalizeSessionPayload(rawPayload) {
        if (!rawPayload) {
            return { data: [] }
        }

        if (typeof rawPayload === 'object') {
            return rawPayload
        }

        const payloadText = String(rawPayload).trim()

        if (!payloadText) {
            return { data: [] }
        }

        try {
            return JSON.parse(payloadText)
        } catch {
            const dataArrayMatch = payloadText.match(/"data"\s*:\s*(\[[\s\S]*\])\s*\}/)

            if (dataArrayMatch && dataArrayMatch[1]) {
                return { data: dataArrayMatch[1] }
            }

            return { data: payloadText }
        }
    }

    function createUuidV4() {
        if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
            return crypto.randomUUID()
        }

        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (character) => {
            const randomValue = Math.random() * 16 | 0
            const resolvedValue = character === 'x' ? randomValue : (randomValue & 0x3) | 0x8
            return resolvedValue.toString(16)
        })
    }

    function upsertSessionId(sessionId) {
        if (!sessionId) {
            return
        }

        setSessions((prevSessions) => {
            const sessionExists = prevSessions.some((session) => getSessionIdValue(session) === sessionId)

            if (sessionExists) {
                return prevSessions
            }

            return [{ session_id: sessionId }, ...prevSessions]
        })
    }

    function startNewConversation() {
        const newSessionId = createUuidV4()

        setSelectedSessionId(newSessionId)
        setChatMessages([
            {
                sender: 'assistant',
                text: 'Chào bạn, mình là trợ lý tư vấn. Bạn muốn hỏi về mục tiêu tập luyện, lịch tập hay dinh dưỡng?',
            },
        ])
        setChatInput('')
        setSessionChatError('')
        upsertSessionId(newSessionId)
    }

    function renderMessageContent(text) {
        const lines = String(text).split('\n')
        const blocks = []
        let currentParagraph = []
        let currentList = null

        const flushParagraph = () => {
            if (currentParagraph.length > 0) {
                blocks.push({ type: 'paragraph', text: currentParagraph.join(' ').trim() })
                currentParagraph = []
            }
        }

        const flushList = () => {
            if (currentList && currentList.items.length > 0) {
                blocks.push({ type: currentList.type, items: currentList.items })
                currentList = null
            }
        }

        lines.forEach((line) => {
            const trimmedLine = line.trim()

            if (!trimmedLine) {
                flushParagraph()
                flushList()
                return
            }

            const numberedMatch = trimmedLine.match(/^\d+\.\s+(.*)$/)
            const bulletMatch = trimmedLine.match(/^[-*•]\s+(.*)$/)

            if (numberedMatch || bulletMatch) {
                flushParagraph()
                const listType = numberedMatch ? 'ol' : 'ul'
                const listItemText = (numberedMatch || bulletMatch)[1].trim()

                if (!currentList || currentList.type !== listType) {
                    flushList()
                    currentList = { type: listType, items: [] }
                }

                currentList.items.push(listItemText)
                return
            }

            flushList()
            currentParagraph.push(trimmedLine)
        })

        flushParagraph()
        flushList()

        if (blocks.length === 0) {
            blocks.push({ type: 'paragraph', text: String(text) })
        }

        return blocks.map((block, blockIndex) => {
            if (block.type === 'paragraph') {
                return (
                    <p key={`paragraph-${blockIndex}`} className="message-paragraph">
                        {block.text}
                    </p>
                )
            }

            const ListTag = block.type

            return (
                <ListTag key={`${block.type}-${blockIndex}`} className="message-list">
                    {block.items.map((item, itemIndex) => (
                        <li key={`${block.type}-${blockIndex}-${itemIndex}`} className="message-list-item">
                            {item}
                        </li>
                    ))}
                </ListTag>
            )
        })
    }

    async function loadSessionMessages(sessionId) {
        if (!sessionId) {
            return
        }

        setSelectedSessionId(sessionId)
        setLoadingSessionChat(true)
        setSessionChatError('')

        try {
            const response = await authedFetch(`/api/public/v1/sessions/${sessionId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            })

            const rawPayload = await response.text().catch(() => '')
            const payload = normalizeSessionPayload(rawPayload)

            if (!response.ok) {
                throw new Error(payload?.message || 'Lỗi khi lấy nội dung session')
            }

            const normalizedMessages = normalizeSessionMessages(payload?.data)

            if (normalizedMessages.length > 0) {
                setChatMessages(normalizedMessages)
            } else {
                setChatMessages([{ sender: 'assistant', text: 'Session này chưa có nội dung hội thoại.' }])
            }
        } catch (error) {
            setSessionChatError(error instanceof Error ? error.message : 'Lỗi không xác định')
        } finally {
            setLoadingSessionChat(false)
        }
    }

    async function handleConsultSubmit(event) {
        event.preventDefault()

        const trimmedQuestion = chatInput.trim()

        if (!trimmedQuestion) {
            return
        }

        const effectiveSessionId = selectedSessionId || createUuidV4()

        if (!selectedSessionId) {
            setSelectedSessionId(effectiveSessionId)
            upsertSessionId(effectiveSessionId)
        }

        setSendingMessage(true)
        setSessionChatError('')

        setChatMessages((prevMessages) => [...prevMessages, { sender: 'user', text: trimmedQuestion }])
        setChatInput('')

        try {
            const response = await authedFetch(`/api/public/v2/answers/${effectiveSessionId}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(trimmedQuestion),
            })

            const rawPayload = await response.text().catch(() => '')
            const payload = normalizeSessionPayload(rawPayload)

            if (!response.ok) {
                throw new Error(payload?.message || 'Lỗi khi gửi câu hỏi tới trợ lý')
            }

            await loadSessionMessages(effectiveSessionId)
        } catch (error) {
            setSessionChatError(error instanceof Error ? error.message : 'Lỗi không xác định')
        } finally {
            setSendingMessage(false)
        }
    }

    function handleLogout() {
        clearAuthToken()
        onLogout()
    }

    return (
        <main className="consult-shell">
            <header className="consult-header">
                <div className="consult-title-wrap">
                    <div className="brand-badge">FIT//PULSE</div>
                    <h2>Hỏi đáp - Tư vấn</h2>
                </div>

                <div className="consult-actions">
                    <button type="button" className="back-button" onClick={onBack}>
                        Quay lại thư viện
                    </button>
                    <button type="button" className="logout-button-header" onClick={handleLogout}>
                        Đăng xuất
                    </button>
                </div>
            </header>

            <section className={`consult-page-content ${isHistoryOpen ? 'history-open' : 'history-collapsed'}`}>
                <aside className="history-sidebar" aria-label="Đoạn hội thoại">
                    <button
                        type="button"
                        className="history-toggle"
                        onClick={() => setIsHistoryOpen((prev) => !prev)}
                        aria-expanded={isHistoryOpen}
                        aria-controls="history-list"
                    >
                        {isHistoryOpen ? 'Ẩn lịch sử' : 'Mở lịch sử'}
                    </button>

                    <button type="button" className="new-chat-button" onClick={startNewConversation}>
                        Đoạn hội thoại mới
                    </button>

                    {isHistoryOpen && (
                        <div className="history-content" id="history-list">
                            <h3>Các Session</h3>
                            {loadingSessions && <p className="loading">Đang tải...</p>}
                            {sessionsError && <p className="error">{sessionsError}</p>}
                            {!loadingSessions && sessions.length > 0 ? (
                                <ul>
                                    {sessions.map((session, index) => {
                                        const sessionId = getSessionIdValue(session)

                                        if (!sessionId) {
                                            return null
                                        }

                                        return (
                                            <li
                                                key={`${sessionId}-${index}`}
                                                title={sessionId}
                                                className={`session-item ${selectedSessionId === sessionId ? 'active' : ''}`}
                                                onClick={() => loadSessionMessages(sessionId)}
                                            >
                                                {sessionId}
                                            </li>
                                        )
                                    })}
                                </ul>
                            ) : !loadingSessions && !sessionsError ? (
                                <p>Bạn chưa có session nào.</p>
                            ) : null}
                        </div>
                    )}
                </aside>

                <div className="consult-chat-panel" aria-label="Trang hoi dap tu van">
                    <div className="consult-messages">
                        {loadingSessionChat && <p className="chat-state loading">Đang tải đoạn chat của session...</p>}
                        {sendingMessage && <p className="chat-state loading">Đang gửi câu hỏi...</p>}
                        {sessionChatError && <p className="chat-state error">{sessionChatError}</p>}
                        {chatMessages.map((message, index) => (
                            <div key={`${message.sender}-${index}`} className={`message-bubble ${message.sender}`}>
                                {renderMessageContent(message.text)}
                            </div>
                        ))}
                    </div>

                    <form className="consult-form" onSubmit={handleConsultSubmit}>
                        <input
                            type="text"
                            value={chatInput}
                            onChange={(event) => setChatInput(event.target.value)}
                            placeholder="Tôi có thể giúp gì cho bạn..."
                            disabled={sendingMessage}
                        />
                        <button type="submit" disabled={!chatInput.trim() || sendingMessage}>
                            {sendingMessage ? 'Đang gửi...' : 'Gửi'}
                        </button>
                    </form>
                </div>
            </section>
        </main>
    )
}
