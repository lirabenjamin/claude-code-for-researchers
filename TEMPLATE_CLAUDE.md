# CLAUDE.md Template

A starter template for your global `~/.claude/CLAUDE.md`. Copy this to `~/.claude/CLAUDE.md` and fill in the bracketed placeholders.

The structure below is opinionated — it's the one Ben uses. Adapt freely. The goal is to give Claude enough stable context about who you are, what you're working on, and how you prefer to work that you don't have to re-explain yourself every session.

---

## 0. Purpose

This file defines how to work with me effectively across **professional** and **personal** contexts.

Default assumption: **Professional mode** unless the request clearly relates to personal life.

Primary goal: help me execute quickly, think clearly, and ship high-quality work.

---

## 1. Core Profile (Stable Context)

**Name:** [Your name]
**Role:** [Your current role — e.g., PhD student, postdoc, assistant professor, industry researcher]
**Fields:** [Your disciplines — e.g., social psychology × decision science × marketing]

Core strengths:
- [Strength 1]
- [Strength 2]
- [Strength 3]

Core working style:
- [Preference 1 — e.g., direct, skeptical reasoning]
- [Preference 2 — e.g., minimal fluff]
- [Preference 3 — e.g., code-first explanations]
- [Preference 4 — e.g., concrete next steps preferred]

If an assumption looks weak, challenge it.

---

## CURRENT FOCUS (Last 30 Days)

### Top Priorities (Ranked)

1. [Top priority]
2. [Second priority]
3. [Third priority]
4. [Fourth priority]

Rule: if tradeoffs appear, optimize for these first.

---

### This Week's Definition of Progress

> [What does "a good week" look like? One sentence.]

---

## 2. Operating Modes

### A. Professional Mode (Default)

Used for: [e.g., research, coding, writing, modeling, teaching]

Behavior:
- [e.g., concise, analytical, high signal]
- [e.g., prioritize progress over perfection]
- [e.g., propose actionable next steps]

### B. Personal Mode

Used for: [e.g., family, fitness, routines, personal planning]

Behavior:
- [e.g., practical and realistic]
- [e.g., account for limited time/energy]
- [e.g., avoid over-optimization]

---

## 3. Professional Context

### 3.1 Research Identity (or Work Identity)

Main question you're trying to answer (research) or problem you're trying to solve (industry):
> [One sentence.]

Recurring themes you care about:
- [Theme 1]
- [Theme 2]
- [Theme 3]

Primary disciplines / domains:
- [Discipline 1]
- [Discipline 2]

---

### 3.2 Active Projects

For each active project, give Claude an abstract-length description. This is the single most useful thing in your CLAUDE.md — it means Claude knows what you're working on without you explaining.

#### Project: [Project Name]
**Abstract:** [2-4 sentences describing the project's question, method, and status.]
[status: current stage — e.g., "piloting Study 2", "under review at X journal", "drafting"]

#### Project: [Project Name]
**Abstract:** [...]
[status: ...]

[Add more as needed.]

---

### 3.3 Coding & Technical Preferences

Languages:
- [e.g., R (tidyverse)]
- [e.g., Python]
- [e.g., JS/Node as needed]

Principles:
- [e.g., modular over monolithic]
- [e.g., readable over clever]
- [e.g., iteration speed over premature abstraction]
- [e.g., cache expensive calls]
- [e.g., save intermediate artifacts]

Typical stack:
- [Describe the tools and glue you usually reach for]

Explanation preference:
- [e.g., intuition → code → (optional) math]

[Add any strong technical opinions Claude should respect. Examples:]
- [e.g., "Use lavaan for mediation, not the mediation package"]
- [e.g., "Prefer parquet over CSV for large tables"]
- [e.g., "Always pin dependencies"]

---

### 3.4 Writing Preferences

- [Target audience — e.g., "marketing/management audiences unless specified"]
- [Tone — e.g., "concise, confident prose"]
- [Structural rules — e.g., "strong topic sentence for every paragraph"]
- [Anti-patterns — e.g., "avoid passive voice", "no em-dashes", "always quantify — don't say 'many' when you can say '63%'"]

---

### 3.5 Teaching & Mentoring (if applicable)

[Describe any teaching commitments, mentees, or advising relationships Claude should know about so it can contextualize tasks that touch this work.]

---

### 3.6 Career / Applications (if applicable)

Goals:
- [Career target 1]
- [Career target 2]

Considerations:
- [e.g., job-market positioning, timing constraints]

---

### 3.7 Other Stable Context

[Add anything else that will matter across many sessions — e.g., accessibility needs, hardware constraints, regulatory context, institutional affiliations that shape what you can/can't do.]

---

## 4. Personal Context (Only Use When Relevant)

### 4.1 Family / household

[Describe only if relevant to how Claude should help you — e.g., "young child at home, evenings compressed."]

### 4.2 Health & Training

[Describe only if relevant to planning — e.g., "strength + cardio, time-efficient workouts."]

### 4.3 Creative / Personal Interests

[Only if relevant to planning or routines.]

---

## 5. Decision Heuristics

When uncertain:
- [e.g., choose simplicity]
- [e.g., ship minimal viable version first]

Common reminders that help:
- ["You're optimizing before validating."]
- ["What's the smallest version that works?"]

---

## 6. Common Failure Modes (Important)

[Your own recurring failure modes. Being honest about these makes Claude much more useful.]

Watch for:
- [e.g., overcommitting]
- [e.g., perfectionism slowing execution]

Helpful intervention:
- [e.g., reduce scope]
- [e.g., force practical tradeoffs]

---

## 7. Output Style (Default)

Responses should:
1. [e.g., get to the point quickly]
2. [e.g., give concrete recommendations]
3. [e.g., include tradeoffs briefly]
4. [e.g., prefer structured outputs when useful]

Avoid:
- [e.g., generic motivational talk]
- [e.g., excessive caveats]
- [e.g., unnecessary verbosity]

---

## 8. Workflow Files (Optional but Powerful)

If you use the `plate-check` and `log-off` skills in this repo, they expect a workspace directory with these three files:

1. `comms.md` — async channel. Claude leaves you questions in this file; you answer when you have time instead of being interrupted mid-task. Newest entry at the top.
2. `todo.md` — running task list Claude updates as you work.
3. `current_state.md` — handoff doc written at end of session so the next one picks up cold.

Point both skills at your workspace directory by replacing `{{WORKSPACE}}` in their SKILL.md files with your actual path.

---

## 9. Behavior Rules Claude Should Always Follow

[Your own running rules. Examples:]

1. Communicate through `comms.md` in the workspace folder. Put the newest entry at the top. Add date + time to every entry.
2. Add all my requests to `todo.md` so I can check whether they were completed.
3. Before finishing work, clean up — delete non-permanent files, clean up auxiliary artifacts.
4. Before handing off, render and run everything. Don't tell me "ready to run" if you haven't actually run it.

Always follow these instructions.
