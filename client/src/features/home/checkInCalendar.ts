/** Calendar dates use Beijing time, independently of the device's timezone. */
export function beijingDate(now: number): string {
  return new Date(now + 8 * 60 * 60 * 1000).toISOString().slice(0, 10)
}

export function emptyCheckInWeek(now: number) {
  const today = beijingDate(now)
  const day = new Date(today + 'T00:00:00Z')
  const monday = day.getTime() - ((day.getUTCDay() + 6) % 7) * 86400000
  return Array.from({ length: 7 }, (_, index) => ({
    date: new Date(monday + index * 86400000).toISOString().slice(0, 10), checked: false,
  }))
}
