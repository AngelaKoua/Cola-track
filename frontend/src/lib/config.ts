// Backend base URL, without the /api suffix (e.g. https://colatrack-api.onrender.com).
// Set NEXT_PUBLIC_API_URL in production; defaults to the local dev server.
export const API_BASE = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000').replace(/\/+$/, '')

// WebSocket base URL, derived from API_BASE (http -> ws, https -> wss) unless overridden.
export const WS_BASE = (process.env.NEXT_PUBLIC_WS_URL || API_BASE.replace(/^http/, 'ws')).replace(/\/+$/, '')
