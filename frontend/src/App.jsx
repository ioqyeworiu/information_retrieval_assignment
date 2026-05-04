import { useEffect, useState } from 'react'
import './App.css'
import { clearAuthToken, getAuthToken, loginWithPassword, setAuthToken } from './auth'
import { ExerciseDocs } from './ExerciseDocs'
import { ConsultationPage } from './ConsultationPage'

function App() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')
  const [successMessage, setSuccessMessage] = useState('')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [activePage, setActivePage] = useState('docs')

  useEffect(() => {
    const storedToken = getAuthToken()

    if (storedToken) {
      setIsAuthenticated(true)
      setActivePage('docs')
      setSuccessMessage('Đã khôi phục phiên đăng nhập trước đó')
    }
  }, [])

  async function handleSubmit(event) {
    event.preventDefault()

    const trimmedUsername = username.trim()

    if (!trimmedUsername || !password) {
      setErrorMessage('Vui lòng nhập username và password.')
      setSuccessMessage('')
      return
    }

    setIsLoading(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const token = await loginWithPassword(trimmedUsername, password)

      setAuthToken(token)
      setIsAuthenticated(true)
      setActivePage('docs')
      setSuccessMessage('Đăng nhập thành công')
      setPassword('')
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Đăng nhập thất bại')
    } finally {
      setIsLoading(false)
    }
  }

  function handleLogout() {
    clearAuthToken()
    setIsAuthenticated(false)
    setUsername('')
    setSuccessMessage('Đã đăng xuất.')
    setErrorMessage('')
    setPassword('')
    setActivePage('docs')
  }

  if (isAuthenticated) {
    if (activePage === 'consultation') {
      return <ConsultationPage onBack={() => setActivePage('docs')} onLogout={handleLogout} />
    }

    return (
      <ExerciseDocs
        onLogout={handleLogout}
        onOpenConsultation={() => setActivePage('consultation')}
      />
    )
  }

  return (
    <main className="auth-shell">
      <section className="login-panel" aria-label="Login form">
        <div className="brand-badge">FIT//PULSE</div>

        <form className="login-card" onSubmit={handleSubmit}>
          <div className="card-header">
            <p className="eyebrow">Member login</p>
            <h1>Đăng nhập</h1>
          </div>

          <label className="field">
            <span>Username</span>
            <input
              type="text"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="member01"
              autoComplete="username"
            />
          </label>

          <label className="field">
            <span>Mật khẩu</span>
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="Nhập mật khẩu của bạn"
              autoComplete="current-password"
            />
          </label>

          <div className="form-meta">
            <label className="remember">
              <input type="checkbox" />
              <span>Ghi nhớ đăng nhập</span>
            </label>
            <a href="/">Quên mật khẩu?</a>
          </div>

          <button className="login-button" type="submit" disabled={isLoading}>
            {isLoading ? 'Đang xác thực...' : 'Đăng nhập'}
          </button>

          <div className="divider">
            <span>hoặc</span>
          </div>

          <button className="secondary-button" type="button">
            Tiếp tục với Google
          </button>

          <p className="card-footer">
            Chưa có tài khoản? <a href="/">Tạo membership</a>
          </p>

          {errorMessage ? <p className="status-message error">{errorMessage}</p> : null}

          {successMessage ? (
            <p className="status-message success">{successMessage}</p>
          ) : null}
        </form>

        <div className="login-footnote">
          <span>24/7 access</span>
          <span>Personal training</span>
          <span>Recovery tracking</span>
        </div>
      </section>
    </main>
  )
}

export default App
