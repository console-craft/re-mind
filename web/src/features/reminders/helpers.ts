/**
 * Formats a reminder start timestamp for the current locale.
 *
 * @param value - ISO 8601 datetime string.
 * @param timeKind - Whether the reminder time is exact or date-only.
 * @returns A compact date/time label.
 */
export function formatReminderTime(value: string, timeKind: "exact" | "date_only" = "exact"): string {
  if (timeKind === "date_only") {
    return new Intl.DateTimeFormat(undefined, {
      day: "numeric",
      month: "short",
    }).format(new Date(value))
  }

  return new Intl.DateTimeFormat(undefined, {
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
  }).format(new Date(value))
}
