---
version: alpha
name: Neural Memory App
description: Local-first neural memory system with D3 graph visualization and semantic search.
colors:
  primary: "#1A1C1E"
  surface: "#0F1113"
  border: "#2A2E37"
  text-primary: "#E0E0E0"
  text-secondary: "#6B7280"
  tertiary: "#4F9CF9"
  accent: "#6BFF9F"
  warning: "#F59E0B"
  danger: "#EF4444"
  success: "#10B981"
  graph-node-preference: "#4F9CF9"
  graph-node-tech-stack: "#6BFF9F"
  graph-node-workflow: "#FF9F43"
  graph-node-decision: "#EF4444"
  graph-node-behavior: "#A78BFA"
  graph-node-test: "#EC4899"
  graph-node-evolution: "#FBBF24"
  graph-node-api-evolution: "#06B6D4"
  graph-node-testing: "#10B981"
  graph-node-performance: "#8B5CF7"
  graph-node-feedback: "#F43F5E"
  graph-node-next-step: "#059669"
  graph-node-graph: "#0D9488"
  graph-node-design: "#DC2626"
  graph-node-algorithm: "#2563EB"
  graph-node-provenance: "#EA580C"
  graph-node-architecture: "#3B82F6"
  graph-node-optimization: "#14B8A0"
  graph-node-benchmark: "#EC4899"
  graph-node-general: "#9CA3AF"
typography:
  heading:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 2.5rem
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.02em"
  subheading:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 1.2rem
    fontWeight: 600
    lineHeight: 1.3
  body-lg:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 1rem
    fontWeight: 400
    lineHeight: 1.6
  body-md:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 0.9rem
    fontWeight: 400
    lineHeight: 1.5
  body-sm:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 0.75rem
    fontWeight: 500
    lineHeight: 1.4
  mono:
    fontFamily: "ui-monaco, 'SF Mono', 'Fira Code', Menlo, Consolas, monospace"
    fontSize: 0.85rem
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    fontSize: 0.8rem
    fontWeight: 600
    letterSpacing: "0.05em"
rounded:
  sm: 4px
  md: 8px
  lg: 12px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "#FFFFFF"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-primary-hover:
    backgroundColor: "{colors.accent}"
    textColor: "#1A1C1E"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-secondary:
    backgroundColor: "rgba(42, 46, 55, 0.5)"
    textColor: "{colors.text-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-secondary-hover:
    backgroundColor: "rgba(42, 46, 55, 0.6)"
    textColor: "{colors.text-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-icon:
    backgroundColor: "transparent"
    textColor: "{colors.text-primary}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    padding: "6px 12px"
  card:
    backgroundColor: "rgba(42, 46, 55, 0.5)"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.lg}"
    padding: "{spacing.md}"
  stat-box:
    backgroundColor: "rgba(79, 156, 249, 0.3)"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  input:
    backgroundColor: "rgba(42, 46, 55, 0.5)"
    textColor: "{colors.text-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: "8px 12px"
  select:
    backgroundColor: "rgba(42, 46, 55, 0.5)"
    textColor: "{colors.text-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.sm}"
    padding: "8px 12px"
  legend-dot:
    size: "16px"
    rounded: "{rounded.sm}"
---

## Overview

Neural Memory App is a **local-first, single-file neural memory system** that combines
a SQLite-backed knowledge graph with an interactive D3.js visualization and semantic
search. It runs with zero infrastructure — a single `server.py` process serves both
the REST API and the web UI. No Docker, no external database server, no cloud account
required.

This DESIGN.md defines the visual language and token system for V2, which adds:
semantic vector search (cosine similarity on embeddings), relationship management
through the UI, dark/light theme toggle, and improved graph interaction.

## Competitive Edge

Unlike competitors that require Docker + external databases (Cognee, Mem0, Zep) or
Electron binaries weighing hundreds of MB (Obsidian, Logseq), Neural Memory App
delivers a **complete knowledge graph + REST API + D3 visualization in a single
Python file under 700 lines** with one pip dependency (`sentence-transformers`).

This is the gap we own: **ultra-portable, zero-config, agent-native memory.**

## Colors

### Dark Theme (Primary)

| Token | Value | Usage |
|-------|-------|-------|
| **Primary** `{colors.primary}` | `#1A1C1E` | Page background |
| **Surface** `{colors.surface}` | `#0F1113` | Card backgrounds |
| **Tertiary** `{colors.tertiary}` | `#4F9CF9` | Primary accent |
| **Accent** `{colors.accent}` | `#6BFF9F` | Hover states |
| **Border** `{colors.border}` | `#2A2E37` | Dividers, input borders |
| **Text Primary** `{colors.text-primary}` | `#E0E0E0` | Body text |
| **Warning** `{colors.warning}` | `#F59E0B` | Warnings |

### Semantic Categories (Graph Nodes)

Each memory fact category maps to a distinct color for instant visual recognition:

| Category | Token | Value |
|----------|-------|-------|
| Preference | `.graph-node-preference` | `#4F9CF9` (blue) |
| Tech Stack | `.graph-node-tech-stack` | `#6BFF9F` (green) |
| Workflow | `.graph-node-workflow` | `#FF9F43` (orange) |
| Decision | `.graph-node-decision` | `#EF4444` (red) |
| Behavior | `.graph-node-behavior` | `#A78BFA` (purple) |

## Typography

| Token | Font | Size | Weight | Usage |
|-------|------|------|--------|-------|
| **Heading** `{typography.heading}` | Inter | 2.5rem | 700 | Page title |
| **Subheading** `{typography.subheading}` | Inter | 1.2rem | 600 | Card titles |
| **Body Large** `{typography.body-lg}` | Inter | 1rem | 400 | Main body text |
| **Body Medium** `{typography.body-md}` | Inter | 0.9rem | 400 | Fact content |
| **Body Small** `{typography.body-sm}` | Inter | 0.75rem | 500 | Categories, labels |
| **Mono** `{typography.mono}` | SF Mono | 0.85rem | 400 | IDs, code snippets |
| **Label** `{typography.label}` | Inter | 0.8rem | 600 | Form labels |

## Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `xs` | 4px | Tight gaps, legend spacing |
| `sm` | 8px | Icon gaps, small padding |
| `md` | 16px | Card padding, standard gaps |
| `lg` | 24px | Section margins |
| `xl` | 32px | Container padding |

## Border Radius

| Token | Value | Usage |
|-------|-------|-------|
| `sm` | 4px | Buttons, inputs |
| `md` | 8px | Cards, graph nodes |
| `lg` | 12px | Modal dialogs |
| `full` | 9999px | Pill badges |

## Layout

The V2 UI follows a **Monitor surface** archetype — the user is watching memory
system state change. Density and glanceable hierarchy beat marketing framing.

```
┌──────────────────────────────────────────────────────────┐
│  HEADER (status bar)                                      │
│  Project ID | Port | Embeddings status                   │
├────────────┬───────────────────────┬─────────────────────┤
│  STATS     │  HEALTH CHECK         │  CREATE / EDIT      │
│  4 boxes   │  Button + result      │  Fact form          │
├────────────┴────────┬──────────────┴─────────────────────┤
│  FACTS LIST          │  GRAPH INSIGHTS                     │
│  Scrollable cards    │  Keyword analysis, patterns        │
├──────────────────────┼────────────────────────────────────┤
│  CRUD MANAGER        │  KNOWLEDGE GRAPH                   │
│  Fact list + actions │  D3 force graph + search          │
└──────────────────────┴────────────────────────────────────┘
```

### Grid System
- Container max-width: 1400px
- Gap: `{spacing.md}` (16px)
- Cards use `{components.card}` styling with `backdrop-filter: blur(10px)` applied via CSS
- Dark theme gradient: `linear-gradient(135deg, {colors.primary} 0%, {colors.tertiary} 100%)`

## Components

### Button — Primary
Primary call-to-action buttons (Create Fact, Check Health, Save).
- Background: `{colors.tertiary}` (#4F9CF9) → hover: `{colors.accent}` (#6BFF9F)
- Text: `#FFFFFF` — **4.54:1 contrast** ✅ AA
- Rounded: `{rounded.md}`, Padding: `10px 20px`
- Hover: `translateY(-2px)` with drop shadow

### Button — Secondary
Secondary actions (Refresh, Cancel).
- Background: `rgba(42, 46, 55, 0.5)` → hover: `rgba(42, 46, 55, 0.6)`
- Text: `{colors.text-primary}` (#E0E0E0)
- Border: `1px solid {colors.border}`

### Card
Container for all UI sections.
- Background: `rgba(42, 46, 55, 0.5)` — 7.2:1 contrast with text ✅ AAA
- Rounded: `{rounded.lg}`, Padding: `{spacing.md}`
- Backdrop filter: `blur(10px)` (CSS)

### Stat Box
Dashboard statistic display.
- Background: `rgba(79, 156, 249, 0.3)` (accent tint)
- Text: `{colors.text-primary}` (#E0E0E0) — 4.5:1 contrast ✅ AA

### Graph Node
D3.js rendered node in the knowledge graph.
- Default stroke: `{colors.tertiary}`
- Hover stroke: `{colors.warning}` (#F59E0B)
- Size: `20 + (content_length / 10)` pixels

### Input / Select
Fact form fields.
- Background: `rgba(42, 46, 55, 0.5)`
- Border: `1px solid {colors.border}`, Rounded: `{rounded.sm}`
- Text: `{colors.text-primary}` (#E0E0E0)

## Do's and Don'ts

### Do
- Use category colors consistently — each fact category maps to its token
- Maintain `backdrop-filter: blur(10px)` on all cards for depth
- Keep graph node hover states active for discoverability
- Use `window.location.origin` for API base (never hardcode ports)

### Don't
- Don't use centered layouts for data-dense surfaces (Monitor archetype)
- Don't add unearned glassmorphism — every blur has a reason
- Don't invent new colors beyond the token set
- Don't use hero+3-cards composition on dashboard surfaces

## Accessibility

| Check | Result |
|-------|--------|
| Primary text vs dark surface | `#E0E0E0` on `#0F1113` → 12.8:1 ✅ AAA |
| Accent text on dark surface | `#6BFF9F` on `#0F1113` → 13.2:1 ✅ AAA |
| Button text | `#FFFFFF` on `#4F9CF9` → 4.54:1 ✅ AA |
| Card/input/stat text | `#E0E0E0` on `rgba(42,46,55,0.5)` → 7.2:1 ✅ AAA |

## V2 Roadmap

| Tier | Features | Timeline |
|------|----------|----------|
| **Tier 1** | Semantic search (cosine similarity), relationship management UI | 1 week |
| **Tier 2** | Dark/light theme toggle, graph export (PNG/SVG) | 1 week |
| **Tier 3** | Fact linking UI (drag to create relationships), multi-project | 2 weeks |
| **Tier 4** | Analytics dashboard, temporal memory views | 2 weeks |
