const AUTH_TOKEN_KEY = 'fitpulse_auth_token'

export function getAuthToken() {
    return window.localStorage.getItem(AUTH_TOKEN_KEY)
}

export function setAuthToken(token) {
    window.localStorage.setItem(AUTH_TOKEN_KEY, token)
}

export function clearAuthToken() {
    window.localStorage.removeItem(AUTH_TOKEN_KEY)
}

function getAuthBaseUrl() {
    return (import.meta.env.VITE_API_BASE_URL || '').replace(
        /\/$/,
        '',
    )
}

function getLoginPath() {
    return import.meta.env.VITE_LOGIN_PATH || '/api/public/v1/users/login'
}

export async function loginWithPassword(username, password) {
    const authBaseUrl = getAuthBaseUrl()
    const loginPath = getLoginPath()
    const loginUrl = authBaseUrl ? `${authBaseUrl}${loginPath}` : loginPath

    const response = await fetch(loginUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
    })

    const payload = await response.json().catch(() => ({}))

    if (!response.ok) {
        throw new Error(payload?.message || 'Đăng nhập thất bại')
    }

    const token = payload?.token || payload?.accessToken || payload?.jwt

    if (!token) {
        throw new Error('Server không trả về JWT')
    }

    return token
}

export async function authedFetch(input, init = {}) {
    const token = getAuthToken()
    const headers = new Headers(init.headers)

    if (token) {
        headers.set('Authorization', `Bearer ${token}`)
    }

    return fetch(input, {
        ...init,
        headers,
    })
}