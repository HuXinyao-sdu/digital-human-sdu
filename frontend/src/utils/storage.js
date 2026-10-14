export function readStorage(key, fallback = null) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback } catch { return fallback }
}
export function writeStorage(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)) } catch { /* Private browsing can disable persistence. */ }
}
