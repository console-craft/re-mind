import type { Reminder } from "@/features/reminders/types"

/**
 * Loads scheduled reminders from the backend API.
 *
 * @param apiBaseUrl - Backend API base URL without a trailing slash.
 * @param signal - Abort signal for cancelling the request.
 * @returns A list of scheduled reminders.
 */
export async function fetchReminders(apiBaseUrl: string, signal: AbortSignal): Promise<Reminder[]> {
  const response = await fetch(`${apiBaseUrl}/reminders`, { signal })

  if (!response.ok) {
    throw new Error(`Failed to load reminders: ${response.status}`)
  }

  return (await response.json()) as Reminder[]
}
