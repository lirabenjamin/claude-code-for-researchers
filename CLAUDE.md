# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this directory is

Prep workspace for Ben Lira's one-hour live Claude Code demo at the Wharton marketing department, 2026-04-16. Audience is about 40 faculty and grad students across several top marketing programs. Lyle Ungar moderates chat; audience muted; no live Q&A until the final 10 min.

This repo is public so the audience can clone the skills and materials. Don't commit personal details here.

## Running example

Everything in the demo uses the **agency paper** as the single running example: `/Users/blira/Library/CloudStorage/OneDrive-PennO365/01 research/ai_agency/`.

Real files to reference/demo against:
- `analysis/report.qmd` — Quarto analysis (cleaning + analysis demo)
- `paper/main.tex` + `paper/sections/` — LaTeX paper (writing demo, `/pipeline-audit`)
- `data/raw/`, `data/processed/` — data for cleaning demo
- `agency6-experiment/` — the custom web-app study (render-survey demo)
- `CLAUDE.md`, `comms.md`, `todo.md` — to show the markdown-files workflow on a real project

The agency paper is a good running example because Study 2 requires a custom web app (shows why Qualtrics isn't enough), has real mediation analysis (lavaan per Ben's convention), and is a real in-prep paper so the audience sees production code, not a toy.

## Agenda

1. Preliminaries (10 min) — slides + meta-demo
2. Survey Design (10 min) — Qualtrics skill + render-survey skill
3. Data Analysis (10 min) — QMD cleaning + analysis
4. Writing methods and results (10 min) — pipeline-audit, latex-workflow, latex-gdoc-roundtrip, research-writing
5. Q&A (10 min) — including Katie's two questions (see `demo_script.md`)

## Files in this directory

- `demo_script.md` — Ben's runbook. Exact prompts to speak, time checkpoints, fallback plans, Q&A prep. **Read this first when helping prep.**
- `slides.qmd` + `slides.css` — Quarto revealjs slides. Renders to `slides.html`. Includes terminal-styled scrollable excerpts of `SKILL.md`, `CLAUDE.md`, and `comms.md` so Ben does not need to open files live during the demo.
- `todo.md` — prep tracker, tied to the two practice sessions.
- `comms.md` — async channel between Ben and Claude for prep questions/decisions.
- `README.md` — public-facing onboarding for people cloning this repo after the demo.
- `TEMPLATE_CLAUDE.md` — starter template for the audience's own global `~/.claude/CLAUDE.md`.
- `skills/` — 15 skills packaged for copy-paste install. Clean skills are verbatim from `~/.claude/skills/`. Four skills (`plate-check`, `log-off`, `opportunity-hunter`, `wbl-form-filler`) are sanitized with `{{PLACEHOLDER}}` variables for privacy since this repo is public.
- `CLAUDE.md` — this file.

## Critical decisions already made (don't relitigate)

- **Repo is public.** Nothing in the repo should contain Ben's personal info (wife/child/visa/phone/real email beyond @wharton public address). Sanitization uses `{{WORKSPACE}}`, `{{PHONE}}`, `{{USER_EMAIL}}`, `{{REPORTS_DIR}}`, etc.
- **Running example is the joke task, not the agency paper directly.** Joke task = login → joke with/without AI → process agency → randomized feedback → outcome agency → meaning. The web-app extension swaps randomized feedback for real peer ratings with AI backfill.
- **No live file opening during demo.** Slide excerpts replace live `open ~/.claude/CLAUDE.md` etc. This saves 2-3 min and avoids any risk of scrolling past something private.
- **No live new-skill creation.** Slides walk through the `SKILL.md` format; Ben verbally explains create + refine patterns; no live scaffolding.
- **AsCollected answer uses "tamper-evident" not "cryptographic teeth"** — Ben disliked the jargon. Underlying argument (git commit hash = uniquely identifies materials+code) is preserved.
- **Katie's two questions have pre-scripted answers** in `demo_script.md` §Q&A.

## Ground rules when working in this directory

- **Do not pre-build demo artifacts in `/01 research/ai_agency/`.** The demo is fully live. Pre-running things would defeat the point and risk stale state during the demo.
- **Mirror Ben's actual conventions when writing example prompts** — lavaan for mediation (not the mediation package), Quarto for analysis, terse prompts (no fluff), WisprFlow voice input. See global `~/.claude/CLAUDE.md` §3.3.
- **Slides are minimal.** Most of the hour is terminal. Slides exist only for concepts that can't be shown in a terminal (what is a markdown file, global vs project CLAUDE.md, skills/agents/MCP taxonomy) and for section transitions.
- **Time discipline matters more than completeness.** Each section is hard-capped at 10 min. `demo_script.md` marks which demos are cuttable if running long.

## Skills being demoed

Confirmed: `qualtrics-survey`, `render-survey`, `data-analysis`, `pipeline-audit`, `latex-workflow`, `latex-gdoc-roundtrip`, `research-writing`, `log-off`. Mentioned but not demoed: `plate-check`, `aspredicted`, `wbl-form-filler`.

All skills live in `~/.claude/skills/`. Ben will also show a `SKILL.md` file directly and have Claude write/edit a skill live (meta-demo).

## Rendering slides

```bash
cd "/Users/blira/Library/CloudStorage/OneDrive-PennO365/02 teaching/claude_code_tutorial"
quarto render slides.qmd
```

Output: `slides.html`. Open in browser, present full-screen.

## Two open questions Ben flagged from Katie

Both addressed in `demo_script.md` §Q&A prep:
1. **AsCollected integration for "as collected, not fabricated" data provenance** — Ben's answer uses Prolific pool + timestamped Mongo + GitHub commit hash as data ID.
2. **Checks against Claude hallucinations in analysis code** — automated tests + read the QMD line-by-line + claim that well-prompted AI code is likely cleaner than hand-written code.
