import type { ReactElement } from "react"
import { useEffect, useState } from "react"
import { fetchReminders } from "@/features/reminders/api"
import { formatReminderTime } from "@/features/reminders/helpers"
import type { Reminder } from "@/features/reminders/types"

interface RemindersListProps {
  apiBaseUrl: string
}

const REMINDER_EXIT_ANIMATION_MS = 560

interface DisplayedReminder {
  isExiting: boolean
  reminder: Reminder
}

/**
 * Merges fresh reminder data with cards that should stay mounted for exit animation.
 *
 * @param displayedReminders - Currently displayed reminder cards.
 * @param nextReminders - Fresh reminders from the API.
 * @returns Reminder cards to render, including exiting cards when needed.
 */
function mergeDisplayedReminders(
  displayedReminders: DisplayedReminder[],
  nextReminders: Reminder[],
): DisplayedReminder[] {
  const nextReminderIds = new Set(nextReminders.map((reminder) => reminder.id))
  const nextRemindersById = new Map(nextReminders.map((reminder) => [reminder.id, reminder]))
  const hasRemovedCards = displayedReminders.some(
    ({ isExiting, reminder }) => !isExiting && !nextReminderIds.has(reminder.id),
  )

  if (!hasRemovedCards) {
    return nextReminders.map((reminder) => ({ isExiting: false, reminder }))
  }

  const displayedReminderIds = new Set(displayedReminders.map(({ reminder }) => reminder.id))
  const mergedReminders = displayedReminders.map(({ isExiting, reminder }) => {
    const nextReminder = nextRemindersById.get(reminder.id)

    return {
      isExiting: isExiting || !nextReminder,
      reminder: nextReminder ?? reminder,
    }
  })
  const newReminders = nextReminders
    .filter((reminder) => !displayedReminderIds.has(reminder.id))
    .map((reminder) => ({ isExiting: false, reminder }))

  return [...mergedReminders, ...newReminders]
}

/**
 * Renders the upcoming reminders panel.
 *
 * @param props - Component props.
 * @param props.apiBaseUrl - Backend API base URL used for loading reminders.
 * @returns A read-only reminders list with loading, empty, and error states.
 */
export function RemindersList({ apiBaseUrl }: RemindersListProps): ReactElement {
  const [reminders, setReminders] = useState<Reminder[]>([])
  const [displayedReminders, setDisplayedReminders] = useState<DisplayedReminder[]>([])
  const [status, setStatus] = useState<"idle" | "loading" | "ready" | "error">("idle")
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  useEffect(() => {
    const controller = new AbortController()

    async function loadReminders(isInitialLoad: boolean): Promise<void> {
      if (isInitialLoad) {
        setStatus("loading")
      }

      try {
        setReminders(await fetchReminders(apiBaseUrl, controller.signal))
        setErrorMessage(null)
        setStatus("ready")
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return
        }

        setErrorMessage(error instanceof Error ? error.message : "Failed to load reminders")
        setStatus("error")
      }
    }

    const events = new EventSource(`${apiBaseUrl}/events`)

    events.addEventListener("reminders.changed", () => {
      void loadReminders(false)
    })

    void loadReminders(true)

    return () => {
      controller.abort()
      events.close()
    }
  }, [apiBaseUrl])

  useEffect(() => {
    setDisplayedReminders((currentReminders) => mergeDisplayedReminders(currentReminders, reminders))
  }, [reminders])

  useEffect(() => {
    if (!displayedReminders.some(({ isExiting }) => isExiting)) {
      return
    }

    const timeoutId = window.setTimeout(() => {
      setDisplayedReminders(reminders.map((reminder) => ({ isExiting: false, reminder })))
    }, REMINDER_EXIT_ANIMATION_MS)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [displayedReminders, reminders])

  return (
    <section className="reminders-panel" aria-labelledby="reminders-title">
      <div className="panel-heading">
        <p className="eyebrow">Upcoming</p>
        <h2 id="reminders-title">Reminders</h2>
      </div>
      {status === "loading" ? <p className="panel-message">Loading reminders...</p> : null}
      {status === "error" ? <p className="panel-message panel-message-error">{errorMessage}</p> : null}
      {status === "ready" && reminders.length === 0 && displayedReminders.length === 0 ? (
        <p className="panel-message">No reminders yet.</p>
      ) : null}
      {displayedReminders.length > 0 ? (
        <ul className="reminder-list">
          {displayedReminders.map(({ isExiting, reminder }) => (
            <li className={`reminder-card${isExiting ? " is-exiting" : ""}`} key={reminder.id}>
              <span>
                {formatReminderTime(reminder.starts_at, reminder.time_kind)}
                {reminder.time_kind === "date_only" && ", any time"}
                <span className="reminder-duration">
                  {reminder.duration_minutes ? <p>{reminder.duration_minutes} minutes</p> : null}
                </span>
              </span>
              <div>
                <strong>{reminder.title}</strong>
                {reminder.details ? <p>{reminder.details}</p> : null}
              </div>
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  )
}
