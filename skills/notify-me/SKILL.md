---
name: notify-me
description: Send the user an iMessage notification when a long-running task finishes. Use after any multi-step or long-running task, especially one the user has stepped away from.
---

# Post-Task Notification

When you have finished completing a long-running task, send the user an iMessage:

```bash
osascript -e 'tell application "Messages"
  set targetService to 1st service whose service type = iMessage
  set targetBuddy to buddy "{{PHONE}}" of targetService
  send "<BRIEF_SUMMARY_OF_WHAT_YOU_DID>" to targetBuddy
end tell'
```

> **Setup note:** Replace `{{PHONE}}` with your own iMessage-capable phone number (e.g., `+15551234567`). This only works on macOS with Messages configured for iMessage.

Replace the message text with a brief summary of what was done and any errors.

## When to Send
- After completing any multi-step or long-running task
- After finishing a task the user initiated and then stepped away from
