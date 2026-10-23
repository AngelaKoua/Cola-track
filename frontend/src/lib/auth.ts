// Helpers for calling protected backend routes with the JWT stored at login (see AuthContext).

const SESSION_KEYS = ['token', 'role', 'username', 'user_id']

/** Authorization header for the current session (empty when logged out). */
export function authHeaders(): Record<string, string> {
    if (typeof window === 'undefined') return {}
    const token = localStorage.getItem('token')
    return token ? { Authorization: `Bearer ${token}` } : {}
}

/** On 401 (expired or invalid token), clear the session and send the user back to the login page. */
export function redirectIfUnauthorized(response: Response): void {
    if (response.status === 401 && typeof window !== 'undefined') {
        SESSION_KEYS.forEach((key) => localStorage.removeItem(key))
        window.location.href = '/'
    }
}
