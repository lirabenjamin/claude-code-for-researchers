# Claude Code Demo — for Researchers

Resources from Ben Lira's one-hour Claude Code demo to the Wharton marketing department (2026-04-16). Share freely.

## What's here

```
.
├── CLAUDE.md              # Context for future Claude sessions in this repo (the demo prep)
├── TEMPLATE_CLAUDE.md     # Starter template for YOUR own global ~/.claude/CLAUDE.md
├── demo_script.md         # Full runbook: what was demoed, exact prompts used, Q&A answers
├── slides.qmd             # Quarto source for the slide deck
├── slides.html            # Rendered slides (open in browser)
└── skills/                # 15 slash-command skills, installable by copy-paste
    ├── aspredicted/
    ├── data-analysis/
    ├── gws/
    ├── latex-gdoc-roundtrip/
    ├── latex-workflow/
    ├── log-off/
    ├── notify-me/
    ├── opportunity-hunter/
    ├── pipeline-audit/
    ├── plate-check/
    ├── qualtrics-survey/
    ├── quarto-version-toggle/
    ├── render-survey/
    ├── research-writing/
    └── wbl-form-filler/
```

## Installing the skills

1. Copy any skill folder into `~/.claude/skills/`.

   ```bash
   cp -r skills/pipeline-audit ~/.claude/skills/
   ```

2. Restart Claude Code (or start a fresh session). The skill will appear as a slash command, e.g. `/pipeline-audit`.

3. Read the SKILL.md first — several skills use **placeholder variables** like `{{WORKSPACE}}` or `{{PHONE}}` that you need to replace with your own paths/numbers. Grep for `{{` in each SKILL.md you install.

## Skills that need configuration before first use

| Skill | What to replace |
|---|---|
| `plate-check` | `{{WORKSPACE}}` (path to your comms/todo/current_state directory), `{{PHONE}}` (iMessage number or delete the notify step) |
| `log-off` | `{{WORKSPACE}}`, `{{PHONE}}` (same as plate-check) |
| `opportunity-hunter` | `{{REPORTS_DIR}}` (where opportunity reports get saved) |
| `wbl-form-filler` | All defaults in the "Known Defaults" block (your name, email, faculty contact, IRB, budget codes). Wharton-specific — adapt for your own lab's forms. |
| `qualtrics-survey` | Needs `QUALTRICS_API_TOKEN` and `QUALTRICS_DATA_CENTER` in a `.env` file |
| `render-survey` | Needs Render + MongoDB Atlas accounts + `OPENAI_API_KEY` if using AI tasks |
| `notify-me` | Uses macOS Messages + your phone number |
| `gws` | Requires `gws` CLI installed for Google Workspace integration |

The other skills (`aspredicted`, `data-analysis`, `latex-gdoc-roundtrip`, `latex-workflow`, `pipeline-audit`, `quarto-version-toggle`, `research-writing`) work out of the box.

## Setting up your own CLAUDE.md

`TEMPLATE_CLAUDE.md` is a starter template for your global `~/.claude/CLAUDE.md`. Copy it over and fill in the placeholders:

```bash
cp TEMPLATE_CLAUDE.md ~/.claude/CLAUDE.md
# then open and fill in your details
```

This is the single highest-leverage thing you can do. Once Claude knows your role, active projects, technical preferences, and failure modes, every session starts with context — you stop repeating yourself.

## Demo materials

- `demo_script.md` — full runbook with time-budgeted sections, exact prompts, fallback plans, and scripted answers to the two audience questions (AsCollected data provenance; hallucination checks in analysis code).
- `slides.html` — 10 concept slides + 4 section-transition slides. Rendered from `slides.qmd`. To re-render after editing:

  ```bash
  quarto render slides.qmd
  ```

## Reporting bugs / requesting features

File issues on this repo or email Ben. If a skill breaks or a placeholder is missing, flag it.

## License

These skills are shared freely. Adapt, fork, improve, re-share. No warranty — you are responsible for checking what Claude produces. See `demo_script.md` Q&A section for Ben's specific answer on how to verify AI-generated analysis code.
