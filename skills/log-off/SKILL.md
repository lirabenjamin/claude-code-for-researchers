---
name: log-off
description: End-of-session wrap-up — updates todo.md, comms.md, and current_state.md with session summary, commits/pushes if git repo, and creates a handoff briefing for the next session. Use when the user says "log off", "wrap up", "call it a night", "done for today", or is ending a work session.
---

# Log Off

End-of-session ritual that wraps up the day's work, updates tracking files, and creates a handoff so the next session picks up instantly without re-onboarding.

> **Setup note:** Replace `{{WORKSPACE}}` below with your own workspace path (e.g., `~/notes/chat/` or `~/Documents/claude-workspace/`). Replace `{{PHONE}}` with your iMessage-capable phone number (or remove the notify step entirely).

---

## Step 1: Review the Session (read-only)

Gather context about what happened this session. Run these in parallel where possible.

### 1a. Local files
- Read `todo.md` at `{{WORKSPACE}}/todo.md`
- Read `comms.md` at `{{WORKSPACE}}/comms.md`
- Read `current_state.md` at `{{WORKSPACE}}/current_state.md` (if it exists)

### 1b. Session history
- Review the conversation history for:
  - Tasks completed
  - Decisions made
  - New items that came up
  - Open questions or blockers
  - Files created or modified

### 1c. Git status (if applicable)
- Check if current directory is a git repo (`git rev-parse --is-inside-work-tree`)
- If yes: run `git status` and `git diff --stat` to see what changed
- If no: skip silently

---

## Step 2: Present Summary to the user

**IMPORTANT: Do NOT update any files yet. Ask the user first.**

Present a structured session recap:

```
## Log Off — [DATE, TIME]

### Done this session:
- [completed items]

### Still open / changed:
- [items that shifted, new blockers, deferred work]

### Decisions made:
- [key decisions or directions chosen]

### Open questions:
- [anything unresolved that needs attention next time]

### Proposed file updates:
- todo.md: [what will change]
- comms.md: [what will be logged]
- current_state.md: [what the handoff will say]
```

Wait for the user to confirm or adjust before proceeding.

---

## Step 3: Update Files

After the user confirms, update three files:

### 3a. `todo.md`
Path: `{{WORKSPACE}}/todo.md`

- Mark completed items as done (e.g., `[x]`)
- Add new items that emerged during the session (with context)
- Reorder by current priority if needed
- Do NOT delete items without the user's approval

### 3b. `comms.md`
Path: `{{WORKSPACE}}/comms.md`

Prepend a dated "Log Off" entry at the top:
```
## Log Off — [DATE, TIME]

**Session summary:** [1-2 sentence overview of what happened]

**Completed:**
- [items finished]

**Still open:**
- [items carried forward]

**Decisions:**
- [key choices made]

**Next session should start with:**
- [top priority for next time]
```

### 3c. `current_state.md`
Path: `{{WORKSPACE}}/current_state.md`

**Overwrite entirely** with a fresh handoff briefing. This is a cold-start file — written so that a new session can pick up without any re-onboarding:

```
# Current State — [DATE, TIME]

## What we were working on
[Brief description of the session's focus]

## Where we stopped
[Exactly what was in progress when we wrapped up]

## What's next
[Concrete next actions, ordered by priority]

## Blockers / Context that would be lost
[Anything non-obvious that the next session needs to know — decisions in flux, waiting on someone, tricky details]

## Key files touched this session
[List of files modified, created, or relevant to pick up work]
```

---

## Step 4: Git (if applicable)

Only if inside a git repo:

1. Stage tracking files only: `git add todo.md comms.md current_state.md`
2. Commit with message: `Log off — [DATE]: [1-line summary]`
3. Push to remote: `git push`

If not a git repo, skip this step silently.

---

## Step 5: Notify + Bedtime Nudge

### iMessage notification (optional)
Send a brief summary via iMessage (remove this block if you don't want phone notifications):

```bash
osascript -e 'tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "{{PHONE}}" of targetService
  send "Session wrapped up. [1-line summary]. current_state.md is ready for next time." to targetBuddy
end tell'
```

### Bedtime nudge
Check the current time. If it's past 11:00 PM:
- Add a gentle reminder: "It's past 11 — nice work today. Go get some rest."
- Keep it light, not preachy.

If it's before 11:00 PM, skip the nudge.

---

## Error Handling

- If `todo.md` doesn't exist: create it with a basic structure
- If `comms.md` doesn't exist: create it with the log-off entry
- If `current_state.md` doesn't exist: create it (this is expected on first run)
- If git push fails: note it in the summary, don't block the rest of the wrap-up
- Always complete the log-off with whatever is available

---

## Quick Mode

If the user says "quick log off" or "quick wrap up":
- Skip the interactive confirmation (Step 2)
- Still update all three files
- Still do git commit/push if applicable
- Still send iMessage notification
- Still check bedtime
