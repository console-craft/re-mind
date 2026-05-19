# re-mind docs-site

Astro Starlight site for developer-facing `re-mind` architecture and technical documentation.

## Local development

```bash
cd docs-site
bun install
bun run dev
```

## Build

```bash
cd docs-site
bun run build
bun run preview
```

## Deployment

Deployment is handled by `.github/workflows/docs-site.yml`:

- Trigger: push to `main` (and manual `workflow_dispatch`)
- Build output: `docs-site/dist`
- Target: GitHub Pages at `https://console-craft.github.io/re-mind/`

## Content layout

- Homepage: `src/content/docs/index.mdx`
- Technical docs: `src/content/docs/**`
- Custom Gruvbox styling: `src/styles/gruvbox.css`
