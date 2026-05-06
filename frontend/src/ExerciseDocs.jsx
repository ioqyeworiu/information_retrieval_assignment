import { useEffect, useState } from 'react'
import { authedFetch, clearAuthToken } from './auth'
import './ExerciseDocs.css'

function parseDocumentString(rawDoc) {
    const idMatch = rawDoc.match(/id='([^']+)'/)
    const nameMatch = rawDoc.match(/name': '([^']+)'/)
    const imageMatch = rawDoc.match(/image': '([^']+)'/)
    const videoMatch = rawDoc.match(/video': '([^']+)'/)
    const gifUrlMatch = rawDoc.match(/gif_url': '([^']+)'/)
    const categoryMatch = rawDoc.match(/category': '([^']+)'/)
    const bodyPartMatch = rawDoc.match(/body_part': '([^']+)'/)
    const equipmentMatch = rawDoc.match(/equipment': '([^']+)'/)
    const muscleGroupMatch = rawDoc.match(/muscle_group': '([^']+)'/)
    const secondaryMusclesMatch = rawDoc.match(/secondary_muscles': \[([^\]]*)\]/)
    const pageContentMatch = rawDoc.match(/page_content='([\s\S]*)'\)$/)

    const secondaryMuscles = secondaryMusclesMatch?.[1]
        ? secondaryMusclesMatch[1]
            .split(',')
            .map((muscle) => muscle.trim().replace(/^'|'$/g, ''))
            .filter(Boolean)
        : []

    return {
        id: idMatch?.[1] || '',
        metadata: {
            id: idMatch?.[1] || '',
            name: nameMatch?.[1] || '',
            image: imageMatch?.[1] || '',
            video: videoMatch?.[1] || gifUrlMatch?.[1] || '',
            category: categoryMatch?.[1] || '',
            body_part: bodyPartMatch?.[1] || '',
            equipment: equipmentMatch?.[1] || '',
            muscle_group: muscleGroupMatch?.[1] || '',
            secondary_muscles: secondaryMuscles,
        },
        page_content: (pageContentMatch?.[1] || '').replace(/\\n/g, '\n'),
    }
}

function normalizeExerciseDoc(rawDoc) {
    const doc = typeof rawDoc === 'string' ? parseDocumentString(rawDoc) : rawDoc
    const metadata = doc?.metadata || {}

    return {
        id: metadata.id || doc?.id || '',
        name: metadata.name || doc?.name || doc?.title || '',
        image: metadata.image || doc?.image || doc?.image_url || '',
        video: metadata.video || metadata.gif_url || doc?.video || doc?.gif_url || '',
        category: metadata.category || doc?.category || '',
        bodyPart: metadata.body_part || metadata.bodyPart || doc?.body_part || '',
        equipment: metadata.equipment || doc?.equipment || '',
        muscleGroup: metadata.muscle_group || metadata.muscleGroup || doc?.muscle_group || '',
        secondaryMuscles: metadata.secondary_muscles || doc?.secondary_muscles || [],
        description: doc?.page_content || doc?.description || '',
    }
}

function getAssetUrl(assetPath) {
    if (!assetPath) {
        return ''
    }

    if (/^https?:\/\//i.test(assetPath)) {
        return assetPath
    }

    const mediaBase = (
        import.meta.env.VITE_MEDIA_BASE_URL ||
        import.meta.env.VITE_API_BASE_URL ||
        'http://localhost:8000'
    ).replace(/\/$/, '')
    const cleanPath = assetPath.replace(/^\/+/, '')
    const normalizedPath = cleanPath.startsWith('media/') ? `/${cleanPath}` : `/media/${cleanPath}`

    return new URL(normalizedPath, `${mediaBase}/`).toString()
}

function getMediaViewerUrl(assetUrl, exerciseName) {
    const query = new URLSearchParams({
        src: assetUrl,
        title: exerciseName || 'Video Demo',
    })

    return `/media-viewer.html?${query.toString()}`
}

function getInstructionSteps(description) {
    if (!description) {
        return []
    }

    return description
        .split('\n')
        .map((line) => line.trim())
        .filter(Boolean)
        .map((line, index) => {
            const match = line.match(/^step\s*(\d+)\s*:\s*(.*)$/i)

            if (match) {
                return {
                    order: Number(match[1]) || index + 1,
                    content: match[2],
                }
            }

            return {
                order: index + 1,
                content: line,
            }
        })
}

function formatExerciseName(name) {
    if (!name) {
        return ''
    }

    return name
        .trim()
        .replace(/[_-]+/g, ' ')
        .replace(/\s+/g, ' ')
        .toLowerCase()
        .replace(/\b\w/g, (char) => char.toUpperCase())
}

export function ExerciseDocs({ onLogout, onOpenConsultation }) {
    const [exercises, setExercises] = useState([])
    const [isLoading, setIsLoading] = useState(false)
    const [hasLoaded, setHasLoaded] = useState(false)
    const [errorMessage, setErrorMessage] = useState('')
    const [searchTerm, setSearchTerm] = useState('')
    const [activeQuery, setActiveQuery] = useState('')
    const [queryN, setQueryN] = useState('21')
    const [similarityType, setSimilarityType] = useState('embedding')

    useEffect(() => {
        loadExercises()
    }, [])

    async function loadExercises(searchQuery = '', options = {}) {
        const resolvedQueryN = String(options.queryN || queryN)
        const resolvedSimilarityType = options.similarityType || similarityType
        const trimmedQuery = searchQuery.trim()
        setIsLoading(true)
        setErrorMessage('')
        setActiveQuery(trimmedQuery)

        try {
            const queryString = new URLSearchParams({
                similarity_type: resolvedSimilarityType,
                query_n: resolvedQueryN,
            }).toString()
            const response = await authedFetch(`/api/public/v2/excercise_docs?${queryString}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(trimmedQuery),
            })

            const payload = await response.json().catch(() => ({}))

            if (!response.ok) {
                throw new Error(payload?.message || 'Lỗi khi lấy danh sách bài tập')
            }

            const docs = payload?.data || payload?.items || payload?.results || []
            const normalizedDocs = Array.isArray(docs)
                ? docs.map(normalizeExerciseDoc).filter((doc) => doc.name || doc.description)
                : []
            setExercises(normalizedDocs)
        } catch (error) {
            setErrorMessage(error instanceof Error ? error.message : 'Lỗi không xác định')
        } finally {
            setIsLoading(false)
            setHasLoaded(true)
        }
    }

    function handleSearchSubmit(event) {
        event.preventDefault()

        const trimmedSearch = searchTerm.trim()

        if (!trimmedSearch) {
            setErrorMessage('Vui lòng nhập từ khóa trước khi tìm.')
            return
        }

        loadExercises(trimmedSearch)
    }

    function handleLogout() {
        clearAuthToken()
        onLogout()
    }

    function handleResetSearch() {
        setSearchTerm('')
        const defaultQueryN = '21'
        const defaultSimilarityType = 'embedding'
        setQueryN(defaultQueryN)
        setSimilarityType(defaultSimilarityType)
        loadExercises('', { queryN: defaultQueryN, similarityType: defaultSimilarityType })
    }

    return (
        <main className="exercise-shell">
            <header className="exercise-header">
                <div className="header-brand">
                    <div className="brand-badge">FIT//PULSE</div>
                    <h2>Thư viện</h2>
                </div>

                <div className="header-actions">
                    <button className="consult-nav-button" onClick={onOpenConsultation}>
                        Hỏi đáp - Tư vấn
                    </button>
                    <button className="logout-button-header" onClick={handleLogout}>
                        Đăng xuất
                    </button>
                </div>
            </header>

            <section className="exercise-content">
                <form className="search-panel" onSubmit={handleSearchSubmit}>
                    <label className="search-field single-search">
                        <span>Tìm kiếm bài tập</span>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => {
                                setSearchTerm(e.target.value)
                                if (errorMessage) {
                                    setErrorMessage('')
                                }
                            }}
                            placeholder="Nhập từ khóa và nhấn Enter hoặc bấm Tìm"
                        />
                    </label>
                    <label className="search-field compact-search">
                        <span>Similarity</span>
                        <select
                            value={similarityType}
                            onChange={(e) => setSimilarityType(e.target.value)}
                        >
                            <option value="embedding">embedding</option>
                            <option value="bm25">bm25</option>
                            <option value="tf-idf">tf-idf</option>
                        </select>
                    </label>
                    <label className="search-field compact-search">
                        <span>Query N</span>
                        <select
                            value={queryN}
                            onChange={(e) => setQueryN(e.target.value)}
                        >
                            <option value="10">10</option>
                            <option value="21">21</option>
                            <option value="30">30</option>
                            <option value="50">50</option>
                        </select>
                    </label>
                    <button className="search-button" type="submit" disabled={!searchTerm.trim()}>
                        {isLoading ? 'Đang tìm...' : 'Tìm'}
                    </button>
                </form>

                <div className="results-toolbar">
                    <p className="results-summary">
                        {isLoading
                            ? 'Đang tải dữ liệu bài tập...'
                            : `${exercises.length} bài tập${activeQuery ? ` cho "${activeQuery}"` : ''} (${similarityType}, top ${queryN})`}
                    </p>
                    <button
                        className="reset-search-button"
                        type="button"
                        onClick={handleResetSearch}
                        disabled={isLoading || (!searchTerm && !activeQuery)}
                    >
                        Xóa lọc
                    </button>
                </div>

                {errorMessage && (
                    <div className="error-box">
                        <p>{errorMessage}</p>
                    </div>
                )}

                <div className="exercises-grid">
                    {isLoading ? (
                        Array.from({ length: 6 }).map((_, idx) => (
                            <article key={`exercise-skeleton-${idx}`} className="exercise-card skeleton-card">
                                <div className="skeleton-line skeleton-title" />
                                <div className="skeleton-line skeleton-chip" />
                                <div className="skeleton-line" />
                                <div className="skeleton-line" />
                                <div className="skeleton-line skeleton-short" />
                                <div className="skeleton-media" />
                            </article>
                        ))
                    ) : exercises.length > 0 ? (
                        exercises.map((exercise, idx) => (
                            <article key={exercise.id || idx} className="exercise-card">
                                <div className="exercise-header-card">
                                    <h3 className="exercise-name">{formatExerciseName(exercise.name) || `Exercise ${idx + 1}`}</h3>
                                    {exercise.category && (
                                        <span className="difficulty beginner">
                                            {exercise.category}
                                        </span>
                                    )}
                                </div>

                                {exercise.description && (
                                    <section className="exercise-instructions" aria-label="Hướng dẫn tập luyện">
                                        <p className="instructions-title">Hướng dẫn</p>
                                        <ol className="instructions-list">
                                            {getInstructionSteps(exercise.description).map((step) => (
                                                <li key={`${exercise.id}-${step.order}-${step.content}`}>
                                                    <span className="step-index">Bước {step.order}</span>
                                                    <p className="step-content">{step.content}</p>
                                                </li>
                                            ))}
                                        </ol>
                                    </section>
                                )}

                                {exercise.bodyPart && (
                                    <div className="exercise-meta">
                                        <span className="label">Body Part:</span>
                                        <span className="value">{exercise.bodyPart}</span>
                                    </div>
                                )}

                                {exercise.equipment && (
                                    <div className="exercise-meta">
                                        <span className="label">Equipment:</span>
                                        <span className="value">{exercise.equipment}</span>
                                    </div>
                                )}

                                {exercise.muscleGroup && (
                                    <div className="exercise-meta">
                                        <span className="label">Primary:</span>
                                        <span className="value">{exercise.muscleGroup}</span>
                                    </div>
                                )}

                                {Array.isArray(exercise.secondaryMuscles) &&
                                    exercise.secondaryMuscles.length > 0 && (
                                        <div className="exercise-meta">
                                            <span className="label">Secondary:</span>
                                            <span className="value">{exercise.secondaryMuscles.join(', ')}</span>
                                        </div>
                                    )}

                                {exercise.image && (
                                    <img
                                        src={getAssetUrl(exercise.image)}
                                        alt={exercise.name}
                                        className="exercise-image"
                                    />
                                )}

                                {exercise.video && (
                                    <section className="video-demo-block" aria-label="Video demo bài tập">
                                        <div className="exercise-meta">
                                            <span className="label">Video Demo:</span>
                                        </div>
                                        <a
                                            href={getMediaViewerUrl(
                                                getAssetUrl(exercise.video),
                                                formatExerciseName(exercise.name),
                                            )}
                                            className="video-launch-card"
                                            target="_blank"
                                            rel="noreferrer"
                                        >
                                            <span className="video-launch-title">Open Video Demo</span>
                                            {/* <span className="video-launch-hint">Nhan </span> */}
                                        </a>
                                    </section>
                                )}
                            </article>
                        ))
                    ) : hasLoaded ? (
                        <div className="no-results">
                            <p>Không có bài tập phù hợp từ kết quả API.</p>
                        </div>
                    ) : null}
                </div>
            </section>
        </main>
    )
}
