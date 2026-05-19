// @ts-check

import starlight from "@astrojs/starlight"
import { defineConfig } from "astro/config"
import { gruvcraftDarkCodeTheme, gruvcraftLightCodeTheme } from "./src/code-themes.mjs"

const REPO_NAME = "re-mind"
const isGitHubActions = process.env.GITHUB_ACTIONS === "true"
const basePath = isGitHubActions ? `/${REPO_NAME}` : ""

// https://astro.build/config
export default defineConfig({
  site: "https://console-craft.github.io",
  base: isGitHubActions ? `/${REPO_NAME}` : "/",
  integrations: [
    starlight({
      title: "re-mind",
      description: "Voice-first reminders with a phone-friendly React SPA, FastAPI backend, SQLite storage, and Vapi integration.",
      tagline: "Voice-first reminders with a phone-friendly React SPA, FastAPI backend, SQLite storage, and Vapi integration.",
      logo: { src: "./public/favicon.png", alt: "re-mind logo" },
      social: [{ icon: "github", label: "GitHub", href: "https://github.com/console-craft/re-mind" }],
      editLink: {
        baseUrl: "https://github.com/console-craft/re-mind/edit/main/docs-site/",
      },
      head: [
        { tag: "link", attrs: { rel: "icon", type: "image/png", href: `${basePath}/favicon.png` } },
        { tag: "link", attrs: { rel: "preconnect", href: "https://fonts.googleapis.com" } },
        {
          tag: "link",
          attrs: { rel: "preconnect", href: "https://fonts.gstatic.com", crossorigin: "anonymous" },
        },
        {
          tag: "link",
          attrs: {
            rel: "stylesheet",
            href: "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap",
          },
        },
        { tag: "script", attrs: { src: `${basePath}/lightbox.js`, defer: true } },
      ],
      customCss: [
        "./src/styles/gruvbox.css",
        "./src/styles/docs-components.css",
        "./src/styles/docs-home.css",
        "./src/styles/lightbox.css",
      ],
      expressiveCode: {
        themes: [gruvcraftDarkCodeTheme, gruvcraftLightCodeTheme],
        styleOverrides: {
          codePaddingBlock: "0.1rem",
          codePaddingInline: "0.5rem",
          codeFontSize: "0.82rem",
        },
        useStarlightUiThemeColors: false,
      },
      components: {
        Hero: "./src/components/Hero.astro",
      },
      sidebar: [
        {
          label: "Start Here",
          items: [
            { label: "Getting Started", slug: "getting-started" },
            { label: "System Architecture", slug: "architecture" },
          ],
        },
        {
          label: "Architecture",
          items: [
            { label: "Frontend", slug: "frontend" },
            { label: "Backend", slug: "backend" },
            { label: "Voice Assistant", slug: "voice-assistant" },
            { label: "Realtime Updates", slug: "realtime" },
          ],
        },
        {
          label: "Reference",
          items: [
            { label: "API Reference", slug: "reference/api" },
            { label: "Environment", slug: "reference/environment" },
          ],
        },
        {
          label: "Operations",
          items: [
            { label: "Local Development", slug: "operations/local-development" },
          ],
        },
      ],
    }),
  ],
})
