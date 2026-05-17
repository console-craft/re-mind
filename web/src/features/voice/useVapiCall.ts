import VapiImport from "@vapi-ai/web"
import { useEffect, useRef, useState } from "react"
import { getCurrentCallVariables } from "@/features/voice/helpers"

type VoiceCallStatus = "idle" | "connecting" | "live" | "ending" | "error"
type VapiConstructor = typeof VapiImport
type VapiClient = InstanceType<VapiConstructor>
type VapiModule = VapiConstructor | { default: VapiConstructor }

interface VoiceConfig {
  assistantId: string
  publicKey: string
}

interface UseVapiCallResult {
  errorMessage: string | null
  isConfigured: boolean
  startCall: () => Promise<void>
  status: VoiceCallStatus
  stopCall: () => Promise<void>
  toggleCall: () => Promise<void>
}

/**
 * Reads Vapi browser credentials from Vite environment variables.
 *
 * @returns Vapi config, or null when credentials are missing.
 */
function getVoiceConfig(): VoiceConfig | null {
  const publicKey = import.meta.env.VITE_VAPI_PUBLIC_KEY
  const assistantId = import.meta.env.VITE_VAPI_ASSISTANT_ID

  if (!publicKey || !assistantId) {
    return null
  }

  return { assistantId, publicKey }
}

/**
 * Extracts a readable error message from unknown thrown values.
 *
 * @param error - Unknown error value.
 * @returns User-facing error message.
 */
function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }

  return "Voice call failed"
}

/**
 * Resolves the Vapi SDK constructor across CommonJS/ESM interop shapes.
 *
 * @returns Vapi client constructor.
 */
function getVapiConstructor(): VapiConstructor {
  const candidate = VapiImport as unknown as VapiModule

  if (typeof candidate === "function") {
    return candidate
  }

  return candidate.default
}

/**
 * Manages one Vapi web call lifecycle.
 *
 * @returns Call status and start/stop controls.
 */
export function useVapiCall(): UseVapiCallResult {
  const [status, setStatus] = useState<VoiceCallStatus>("idle")
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const vapiRef = useRef<VapiClient | null>(null)
  const config = getVoiceConfig()

  function getVapiClient(publicKey: string): VapiClient {
    if (vapiRef.current) {
      return vapiRef.current
    }

    const Vapi = getVapiConstructor()
    const vapi = new Vapi(publicKey)

    vapi.on("call-start", () => {
      setStatus("live")
      setErrorMessage(null)
    })
    vapi.on("call-end", () => {
      setStatus("idle")
    })
    vapi.on("call-start-failed", (event) => {
      setErrorMessage(event.error)
      setStatus("error")
    })
    vapi.on("error", (error) => {
      setErrorMessage(getErrorMessage(error))
      setStatus("error")
    })

    vapiRef.current = vapi

    return vapi
  }

  async function startCall(): Promise<void> {
    if (!config) {
      setErrorMessage("Missing VITE_VAPI_PUBLIC_KEY or VITE_VAPI_ASSISTANT_ID")
      setStatus("error")
      return
    }

    if (status === "connecting" || status === "live") {
      return
    }

    setErrorMessage(null)
    setStatus("connecting")

    try {
      await getVapiClient(config.publicKey).start(config.assistantId, {
        variableValues: getCurrentCallVariables(),
      })
      setStatus("live")
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
      setStatus("error")
    }
  }

  async function stopCall(): Promise<void> {
    if (!vapiRef.current || status === "idle") {
      setStatus("idle")
      return
    }

    setStatus("ending")

    try {
      await vapiRef.current.stop()
      setStatus("idle")
    } catch (error) {
      setErrorMessage(getErrorMessage(error))
      setStatus("error")
    }
  }

  async function toggleCall(): Promise<void> {
    if (status === "live") {
      await stopCall()
      return
    }

    await startCall()
  }

  useEffect(() => {
    return () => {
      vapiRef.current?.removeAllListeners()
      void vapiRef.current?.stop()
    }
  }, [])

  return {
    errorMessage,
    isConfigured: config !== null,
    startCall,
    status,
    stopCall,
    toggleCall,
  }
}
