import type { ReactElement } from "react"

import { useVapiCall } from "@/features/voice/useVapiCall"

const STATUS_COPY = {
  connecting: "Starting voice call...",
  ending: "Ending voice call...",
  error: "Voice call is not ready.",
  idle: "Ready when you are.",
  live: "Listening now. Say your reminder naturally.",
} as const

/**
 * Creates the visible label for the voice call button.
 *
 * @param status - Current Vapi call status.
 * @returns Button label for the current call state.
 */
function getButtonLabel(status: keyof typeof STATUS_COPY): string {
  if (status === "connecting") {
    return "Connecting..."
  }

  if (status === "ending") {
    return "Ending..."
  }

  if (status === "live") {
    return "End call"
  }

  return "Remind me"
}

/**
 * Renders the voice-first reminder capture panel.
 *
 * @returns The Vapi-powered reminder capture panel.
 */
export function AddReminder(): ReactElement {
  const { errorMessage, isConfigured, status, toggleCall } = useVapiCall()
  const isBusy = status === "connecting" || status === "ending"
  const statusMessage = isConfigured
    ? (errorMessage ?? STATUS_COPY[status])
    : "Add VITE_VAPI_PUBLIC_KEY and VITE_VAPI_ASSISTANT_ID to enable voice calls."

  return (
    <section className="hero-panel" aria-labelledby="app-title">
      <p className="eyebrow">Voice reminder assistant</p>
      <h1 id="app-title">Re-mind</h1>
      <p className="hero-copy">Tap once, say the reminder, and let the AI agent schedule the useful bits.</p>
      <button
        aria-pressed={status === "live"}
        className="talk-button"
        disabled={!isConfigured || isBusy}
        onClick={() => void toggleCall()}
        type="button"
      >
        {getButtonLabel(status)}
      </button>
      <p className="status-note">{statusMessage}</p>
    </section>
  )
}
