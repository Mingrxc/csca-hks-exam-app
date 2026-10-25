export function formatReleaseDate(value?: string | null): string {
  if (!value) return ''
  const timestamp = Date.parse(value)
  if (!Number.isFinite(timestamp)) return ''
  return new Date(timestamp + 8 * 60 * 60 * 1000).toISOString().slice(0, 10).replace(/-/g, '.')
}
