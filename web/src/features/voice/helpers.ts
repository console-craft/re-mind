/**
 * Pads a number for date/time formatting.
 *
 * @param value - Number to pad.
 * @returns A two-character date/time segment.
 */
function padDateSegment(value: number): string {
  return String(value).padStart(2, "0")
}

/**
 * Formats a date as a local calendar date.
 *
 * @param value - Date to format.
 * @returns Local date in YYYY-MM-DD format.
 */
export function formatLocalDate(value: Date): string {
  return [value.getFullYear(), padDateSegment(value.getMonth() + 1), padDateSegment(value.getDate())].join("-")
}

/**
 * Formats a date as a local ISO-like datetime with timezone offset.
 *
 * @param value - Date to format.
 * @returns Local datetime in YYYY-MM-DDTHH:mm:ss±HH:mm format.
 */
export function formatLocalDateTime(value: Date): string {
  const offsetMinutes = -value.getTimezoneOffset()
  const sign = offsetMinutes >= 0 ? "+" : "-"
  const absoluteOffset = Math.abs(offsetMinutes)
  const offsetHours = Math.floor(absoluteOffset / 60)
  const offsetRemainderMinutes = absoluteOffset % 60

  return `${formatLocalDate(value)}T${padDateSegment(value.getHours())}:${padDateSegment(
    value.getMinutes(),
  )}:${padDateSegment(value.getSeconds())}${sign}${padDateSegment(offsetHours)}:${padDateSegment(offsetRemainderMinutes)}`
}

interface CurrentCallVariables {
  current_date: string
  current_datetime: string
  timezone: string
}

/**
 * Builds Vapi assistant variables for resolving relative dates.
 *
 * @param value - Date to use as the current call time.
 * @returns Current date/time variables for Vapi assistant overrides.
 */
export function getCurrentCallVariables(value = new Date()): CurrentCallVariables {
  return {
    current_date: formatLocalDate(value),
    current_datetime: formatLocalDateTime(value),
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
  }
}
