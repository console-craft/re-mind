import type { ReactElement } from "react"

import { AddReminder } from "@/components/AddReminder"
import { RemindersList } from "@/components/RemindersList"

import "./App.css"

const DEFAULT_API_URL = "http://localhost:8000"

/**
 * Resolves the backend API base URL for browser requests.
 *
 * @returns The configured API base URL without a trailing slash.
 */
function getApiBaseUrl(): string {
  return (import.meta.env.VITE_API_URL || DEFAULT_API_URL).replace(/\/$/, "")
}

/**
 * Renders the initial phone-first reminder app shell.
 *
 * @returns The local development placeholder UI.
 */
export function App(): ReactElement {
  const apiBaseUrl = getApiBaseUrl()

  return (
    <main className="app-shell">
      <AddReminder />
      <RemindersList apiBaseUrl={apiBaseUrl} />
    </main>
  )
}
