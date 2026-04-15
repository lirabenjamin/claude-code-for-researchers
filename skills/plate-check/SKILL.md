---
name: plate-check
description: Weekly plate check — pulls from Gmail, Google Calendar, Reclaim, todo.md, and CLAUDE.md to give the user a comprehensive briefing, triage stale tasks, flag conflicts, and generate a visual dashboard. Use when the user wants a status update, weekly review, or says "what's on my plate".
---

# Plate Check

A comprehensive weekly review that pulls from all of the user's systems, asks clarifying questions, then updates `todo.md`, `comms.md`, and generates a visual `dashboard.html`.

> **Setup note:** Replace `{{WORKSPACE}}` below with your own workspace path (e.g., `~/notes/chat/` or `~/Documents/claude-workspace/`). Replace `{{PHONE}}` with your iMessage-capable phone number (or remove the notify step entirely).

---

## Step 1: Gather (parallel, read-only)

Collect data from all sources. Run these in parallel where possible.

### 1a. Local files
- Read `todo.md` at `{{WORKSPACE}}/todo.md`
- Read `comms.md` at `{{WORKSPACE}}/comms.md`
- Read the "CURRENT FOCUS" and "Active Projects" sections from `~/.claude/CLAUDE.md` to understand stated priorities and definition of progress

### 1b. Gmail
- Use `mcp__claude_ai_Gmail__gmail_search_messages` to search for emails from the last 7 days
- Filter for actionable messages: from collaborators, advisors, students, institutions
- Ignore: newsletters, automated notifications, marketing, receipts
- For important threads, use `gmail_read_thread` to get full context
- Surface emails that need replies, especially those 3+ days old

### 1c. Google Calendar
- Use `mcp__claude_ai_Google_Calendar__gcal_list_events` to fetch events for the next 14 days
- Note: meetings, deadlines, blocked time, recurring commitments
- Calculate total meeting hours per day

### 1d. Reclaim tasks
- Use `mcp__reclaim__get_tasks` to fetch all active Reclaim tasks
- Use `mcp__reclaim__get_events` to fetch scheduled task blocks for next 14 days

---

## Step 2: Analyze

Cross-reference all sources and produce findings:

### Conflicts & Overload
- **Double-bookings:** overlapping calendar events
- **Overloaded days:** days with 6+ hours of meetings (flag as "no deep work possible")
- **Deadline collisions:** multiple deliverables due the same day/week
- **Missing time blocks:** tasks with deadlines but no time scheduled in calendar or Reclaim
- **Meetings without prep:** important meetings (with advisors, collaborators) with nothing scheduled before them

### Task Health
- **Zombie tasks:** items on `todo.md` that have been sitting for 2+ weeks with no progress markers. These need triage — done? still relevant? blocked?
- **Orphan tasks:** Reclaim tasks not reflected in `todo.md`, or vice versa
- **Misaligned priorities:** tasks consuming time that don't align with the "CURRENT FOCUS" priorities from CLAUDE.md

### Email Triage
- **Needs reply:** emails from collaborators/advisors/students awaiting response, sorted by age
- **Action items:** emails containing requests, deadlines, or asks
- **FYI only:** important updates that don't need action

### Urgency Categorization
Categorize everything into:
1. **Hard deadlines** (red) — immovable dates, submissions, reviews due
2. **Time-sensitive** (orange) — should happen this week or risks slipping
3. **Important-not-urgent** (yellow) — matters but can be scheduled for later
4. **Can wait** (green) — nice to do, no pressure

### Alignment Check
- Compare actual task load against the "This Week's Definition of Progress" from CLAUDE.md
- Is the user spending time on what they said matters most?
- Are the top priorities (#1-4 from CURRENT FOCUS) actually getting calendar time?

---

## Step 3: Interactive Triage

**IMPORTANT: Do NOT update any files yet. Ask the user first.**

Present findings as a structured briefing, then ask targeted questions:

### Briefing format
```
## Plate Check — [DATE]

### Your stated priorities (from CLAUDE.md):
1. ...
2. ...

### This week's definition of progress:
> [quoted from CLAUDE.md]

### Reality check:
- [Calendar hours breakdown]
- [Number of pending tasks]
- [Emails awaiting reply]

### Flags:
- [Conflicts, overload, zombies, misalignments]

### Questions for you:
1. [Specific triage question about zombie task]
2. [Scope question about competing deadlines]
3. [Reality check about overcommitted day]
```

Wait for the user's answers before proceeding.

### Overload Protocol
If the user's CLAUDE.md includes guidance about overload handling, follow it. Otherwise default to:

If the plate is clearly overloaded:
- Explicitly say so
- Propose what to cut or defer
- Recommend a "just do this one thing" focus for the week
- Be direct — concise output beats hedging

### Time Awareness
- Respect any time constraints the user has documented in CLAUDE.md (family obligations, deep-work windows, bedtime norms, etc.)
- Factor these constraints into scheduling recommendations

---

## Step 4: Update Files

After the user confirms, update three files:

### 4a. `todo.md`
Path: `{{WORKSPACE}}/todo.md`

- Add a clear `## THIS WEEK` section at the top with 3-5 focus items
- Add new items surfaced from email or calendar (with source noted)
- Mark zombie tasks with `[STALE — 2+ weeks]` or archive per the user's answers
- Re-order by priority alignment
- Do NOT delete items without the user's approval — mark them for review instead

### 4b. `comms.md`
Path: `{{WORKSPACE}}/comms.md`

Prepend a dated briefing entry at the top:
```
## Plate Check — [DATE, TIME]

**Summary:** [1-2 sentence overview]

**Changes made to todo.md:**
- [List of additions, removals, reorderings]

**Key flags:**
- [Top 2-3 things the user should know]

**Next plate check:** [suggest when]
```

### 4c. `dashboard.html`
Path: `{{WORKSPACE}}/dashboard.html`

Generate a single self-contained HTML file (inline CSS/JS, zero external dependencies) with:

**Design principles:**
- Dark mode, monospace-accented aesthetic (JetBrains Mono for labels, Outfit/system for body)
- Noise texture overlay, subtle glows, smooth fade-in animations
- Responsive — works on laptop and phone
- No frameworks — vanilla HTML/CSS/JS only, but CAN use Google Fonts for JetBrains Mono + Outfit
- Color palette: red (#ff4d6a), orange (#ff8c42), yellow (#ffd166), green (#06d6a0), blue (#4ea8de), purple (#b388ff), cyan (#64dfdf) — each with dim variants at 20% opacity
- Cards with hover states, subtle borders, no heavy shadows — use glows sparingly for emphasis
- NEVER hardcode today's date — use JavaScript to derive it from `new Date()` with the user's timezone. The header date, "Today" badge in the timeline, and any relative labels (e.g., "today", "yesterday") must all be dynamic. Timeline day elements should use `data-date="YYYY-MM-DD"` attributes so JS can auto-highlight the current day.

**Panels to include:**

1. **Header** — Date, live clock, "Command Center" title with gradient text

2. **Blockers Banner** — Red-accented banner at top with pulsing glow. Shows active blockers and urgent items as chips. Only show truly blocking/urgent items.

3. **Horizon Calendar** — Monthly grid spanning ~6 months (current month through ~5 months out). Each month is a column. Show ONLY hard deadlines, conferences, talks, and key target dates — NOT daily meetings from Google Calendar. Color-code by type (deadline=red, conference=purple, talk=cyan, target=yellow, meeting=orange). Include a legend. This is a strategic view, not a daily schedule.

4. **Projects Grid** — 2-column grid of project cards grouped by category. Each card has: colored top border by priority, status dot, title, badge (JMP/Overdue/Waiting/Action/Handed Off), current status line, next action, and optionally a pipeline visualization (step → step → step with current highlighted).

5. **This Week + Next Timeline** — Sticky sidebar showing day-by-day events for the next ~2 weeks. Sourced from Google Calendar. Compact format: day label, bullet events with times. Mark today, flag overdue items. Include conference blocks.

6. **Task Kanban** — 4-column board: Overdue | This Week | Next Week | Later. Each task shows name, priority tag (P1/P2/P3), due date. Blocking tasks get red left border. Done tasks show strikethrough at reduced opacity.

7. **Email Queue** — Table of emails needing replies.

8. **Zombie Tasks** — items 2+ weeks stale, flagged for triage.

9. **Recent Completions** — what was finished recently.

10. **Priorities Alignment** — calendar-time vs stated priorities.

11. **Grants/Jobs (Parked)** — Dimmed section showing parked grant deadlines as chips, with the earliest deadline highlighted in red.

After writing the file, open it with:
```bash
open {{WORKSPACE}}/dashboard.html
```

---

## Step 5: Notify

Use the `notify-me` skill pattern to send an iMessage summary (optional — remove this step if you don't want phone notifications):

```bash
osascript -e 'tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "{{PHONE}}" of targetService
  send "Plate check done. Dashboard is open. [1-line summary of biggest flag]" to targetBuddy
end tell'
```

---

## Error Handling

- If Gmail MCP is unavailable: skip email section, note it in the briefing
- If Calendar MCP is unavailable: skip calendar section, note it in the briefing
- If Reclaim MCP is unavailable: skip Reclaim section, note it in the briefing
- If `todo.md` doesn't exist: create it with a basic structure
- If `comms.md` doesn't exist: create it with the briefing entry
- Always complete the review with whatever sources ARE available — partial data is better than no review

---

## Quick Mode

If the user says "quick plate check" or "just the highlights":
- Skip the interactive triage (Step 3)
- Only update `comms.md` with a brief status
- Still generate the dashboard
- Don't modify `todo.md`
