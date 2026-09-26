# Claude Code for Researchers

Slides, a runbook, a CLAUDE.md template, and 18 installable skills for using Claude Code in research work. By Ben Lira. Share freely.

## What's here

```
.
├── install.sh             # One-liner installer (see below)
├── CLAUDE.md              # Context for future Claude sessions in this repo
├── TEMPLATE_CLAUDE.md     # Starter template for YOUR own global ~/.claude/CLAUDE.md
├── demo_script.md         # Full runbook: section timings, exact prompts, fallback plans, Q&A answers
├── slides.qmd             # Quarto source for the slide deck
├── slides.html            # Rendered slides (open in browser)
└── skills/                # 18 slash-command skills
    ├── archive-raw-data/
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
    ├── semantic-pipeline/
    ├── wbl-form-filler/
    └── zotero-fetch/
```

## Installing the skills

**One-liner (installs all skills into `~/.claude/skills/`):**

```bash
curl -fsSL https://raw.githubusercontent.com/lirabenjamin/claude-code-for-researchers/main/install.sh | bash
```

Install only specific skills:

```bash
curl -fsSL https://raw.githubusercontent.com/lirabenjamin/claude-code-for-researchers/main/install.sh | bash -s -- pipeline-audit data-analysis
```

Re-install and overwrite existing:

```bash
curl -fsSL https://raw.githubusercontent.com/lirabenjamin/claude-code-for-researchers/main/install.sh | bash -s -- --force
```

The script clones the repo to a temp dir, copies skill folders to `~/.claude/skills/`, skips any that already exist (unless `--force`), and prints a list of skills that need further configuration.

**Manual alternative** — clone the repo and copy individual skill folders:

```bash
cp -r skills/pipeline-audit ~/.claude/skills/
```

After installing, **restart Claude Code** (or start a fresh session). Skills appear as slash commands, e.g. `/pipeline-audit`. Read the SKILL.md first — 5 skills use **placeholder variables** like `{{WORKSPACE}}` or `{{PHONE}}` that you need to replace. `grep -l '{{' ~/.claude/skills/*/SKILL.md` will find them.

## Skills that need configuration before first use

| Skill | What to replace |
|---|---|
| `archive-raw-data` | `.env` needs `ZENODO_TOKEN` (from https://zenodo.org/account/settings/applications/tokens/) and `MONGODB_URI`. Requires `mongoexport` installed. |
| `plate-check` | `{{WORKSPACE}}` (path to your comms/todo/current_state directory), `{{PHONE}}` (iMessage number or delete the notify step) |
| `log-off` | `{{WORKSPACE}}`, `{{PHONE}}` (same as plate-check) |
| `opportunity-hunter` | `{{REPORTS_DIR}}` (where opportunity reports get saved) |
| `wbl-form-filler` | All defaults in the "Known Defaults" block (your name, email, faculty contact, IRB, budget codes). Wharton-specific — adapt for your own lab's forms. |
| `qualtrics-survey` | Needs `QUALTRICS_API_TOKEN` and `QUALTRICS_DATA_CENTER` in a `.env` file |
| `render-survey` | Needs Render + MongoDB Atlas accounts + `OPENAI_API_KEY` if using AI tasks |
| `notify-me` | Uses macOS Messages + your phone number |
| `gws` | Requires the `gws` CLI installed and authed for Google Workspace integration |
| `latex-gdoc-roundtrip` | Requires the `gws` CLI |
| `semantic-pipeline` | Needs `OPENAI_API_KEY` for the document-level step, plus a dedicated Python venv |
| `zotero-fetch` | Needs `ZOTERO_API_KEY` and `ZOTERO_USER_ID` in your shell env |

The other 6 skills (`aspredicted`, `data-analysis`, `latex-workflow`, `pipeline-audit`, `quarto-version-toggle`, `research-writing`) work out of the box.

## Setting up your own CLAUDE.md

`TEMPLATE_CLAUDE.md` is a starter template for your global `~/.claude/CLAUDE.md`. Copy it over and fill in the placeholders:

```bash
cp TEMPLATE_CLAUDE.md ~/.claude/CLAUDE.md
# then open and fill in your details
```

No other setup step pays off as much. Once Claude knows your role, active projects, technical preferences, and failure modes, every session starts with context — you stop repeating yourself.

## Walkthrough materials

- `demo_script.md` — full runbook with time-budgeted sections, exact prompts, fallback plans, and scripted answers to the 2 questions that come up most often (AsCollected data provenance; hallucination checks in analysis code).
- `slides.html` — 10 concept slides + 4 section-transition slides. Rendered from `slides.qmd`. To re-render after editing:

  ```bash
  quarto render slides.qmd
  ```

## Reporting bugs / requesting features

File issues on this repo. If a skill breaks or a placeholder is missing, flag it.

## License

These skills are shared freely. Adapt, fork, improve, re-share. No warranty — you are responsible for checking Claude's output. The `demo_script.md` Q&A section gives a concrete procedure for verifying AI-generated analysis code.
