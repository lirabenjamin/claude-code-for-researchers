# Claude Code Demo — Runbook

Thu 2026-04-16, 2:00–3:00pm ET. Keep this file open on a second screen during practice runs.

Time budget (58 min after Angela's 1-min intro):
- Preliminaries (10)  — 1:00–11:00
- Survey Design (10)  — 11:00–21:00
- Data Analysis (10)  — 21:00–31:00
- Writing (10)        — 31:00–41:00
- Q&A (10)            — 41:00–51:00

---

## Pre-flight checklist (do in this order, last 15 min before demo)

- [ ] WisprFlow running + tested
- [ ] Zoom: screen-share permissions, "optimize for video" OFF, recording ON
- [ ] Two terminal windows open, both in `01 research/ai_agency/`, zoom level ~140%
- [ ] Browser tabs pre-loaded (not logged out): Qualtrics, Render dashboard, Overleaf for agency paper, AsPredicted page (for Katie Q), the shared Google Doc, **this tutorial repo on GitHub** (you'll show it in Survey section)
- [ ] `slides.html` open in a third tab, full-screen tested
- [ ] Silence Slack, iMessage, Gmail notifications
- [ ] Clear `~/Downloads` clutter (you will screen-share)
- [ ] Start a fresh Claude Code session so context is clean
- [ ] Double-check `~/.claude/CLAUDE.md` doesn't reveal anything private before scrolling it on-screen
- [ ] Water + backup mic + phone on Do Not Disturb

**Cut list if running long** (in order): `/latex-workflow` demo → second iteration of the joke survey → Bradley-Terry walkthrough depth → the research-writing detailed output. Never cut `/pipeline-audit` — it is the answer to Katie Q2. Never cut the Google Docs caveat — it's the writing-section punchline.

---

## Angela intro — 0:00–1:00

Mute yourself. Angela gives the 1-min intro. While she talks:
- Verify screen share is on the slides
- Pull up terminal #1 ready for prompts

---

## PRELIMINARIES — 1:00–11:00

### 1:00–1:45 — Why bother? (slide 2)

> "There's a learning curve. We're going to need to use the terminal. We're going to install a few things. You might be thinking — wait, I already have Claude in a browser tab, why put in the effort?
>
> The honest answer: Claude Code lets you do much more, much faster. I think three or four hours of setup and learning will make you roughly **twice as productive in the long run**. That's the tradeoff. You decide if it's worth it for you. I'll try to convince you it is."

### 1:45–3:30 — Claude Code ≠ Claude Chat (slides 3–4)

Three concrete differences, then the unlock:

> "**First: file manipulation.** In the chat tab, you're copy-pasting content back and forth — from the chat to your editor, from your editor back to the chat. Claude Code directly reads and edits files on your machine.
>
> **Second: code execution plus an iteration loop.** Claude can run commands, see the output, catch its own errors, fix them, and try again. Test-operate-test-operate-exit. Depending on task complexity, I can give Claude a high-level instruction and it will work for 15-20 minutes — running, failing, fixing, running again — and come back with finished work. That loop is the whole reason it can take on bigger jobs.
>
> **Third: multi-agent.** A chatbot is one voice talking to you. Claude Code spawns sub-agents under itself — parallel workers for different parts of a task — which makes bigger jobs feasible."

Transition to slide 4 (long-term memory):

> "And then the thing that actually turns this into a collaborator: **long-term memory**.
>
> Claude Chat forgets everything when you close the tab. Claude Code doesn't. Via a handful of markdown files — `CLAUDE.md`, `comms.md`, `todo.md`, `current_state.md` — Claude builds project-specific memory. Who you are. What you're working on. What's been decided. What's still open.
>
> Unlike a human collaborator, this memory is inspectable. You open the files. You can see what Claude remembers about your project. You can rewrite it. That's the unlock."

### 3:30–5:30 — Skills, agents, MCP (slide 5)

> "Three primitives. I'll go light on two of them and heavy on the third.
>
> **Skills** are reusable slash commands. Markdown file, frontmatter, a recipe. Claude picks them up when the description matches what you're asking for. This is where 90% of the value lives for researchers. Focus here.
>
> **Agents** are the multi-agent thing I just mentioned — sub-processes Claude spawns for parallel work. Honestly, I haven't found a ton of use for writing custom agents. The built-in ones are enough.
>
> **MCP servers** are external tool connectors. I've got MCP servers for my email, my calendar, and — the more unusual one — my task manager. I can tell Claude what's on my mind, how important each thing is, when it's due, and it blocks time on my calendar and updates my task list accordingly. That's **Claude as my executive assistant** — different job from Claude as my research assistant, which is what today is about. Happy to talk about the exec-assistant side offline.
>
> For the next hour, we're focused on skills."

### 5:30–7:30 — How skills work (slides 6–7)

Slides show the actual pipeline-audit SKILL.md excerpt + the "how you create / edit" patterns. Walk through verbally, don't switch to terminal.

> "A skill is a markdown file with YAML frontmatter and a body. Name, description, instructions. Claude reads the description and decides when to invoke it based on what you ask for.
>
> **Two moves.**
>
> **One — you create skills by talking to Claude.** You say: 'make me a skill that does X.' Claude scaffolds the SKILL.md. You review, edit if needed, done.
>
> **Two — you refine skills the same way.** Yesterday I was using my Google Docs skill and noticed that after a certain point in the output the text was garbled — dark, broken formatting. Instead of debugging by hand, I told Claude: 'after the third section the text goes garbled. Figure out why, and edit the skill so this doesn't happen again.' It diagnosed it and patched the skill. That's the workflow.
>
> We have 15 skills in the repo — `/plate-check`, `/aspredicted`, `/pipeline-audit`, `/research-writing`, `/log-off`, and more. You build your own the exact same way — by asking."

*No live skill creation. Keep moving.*

### 7:30–8:15 — Why talk, not type (slide 8)

> "I'm using WisprFlow right now — it's free, you press a key, you talk, it transcribes. I type 40 words a minute, I speak 150.
>
> The point isn't speed — it's **clarity**. When I type, I truncate. I write 'clean the data' and hope Claude picks the right exclusions. When I talk, I say 'clean the data, apply our standard exclusions — attention check, under-60-second completion, duplicate IPs — save the clean file with the commit hash in the name.' Talking gets more specific instructions out of me. And more specific instructions get better output."

### 8:15–10:30 — Markdown files = the memory (slides 9–10)

Slides show terminal-styled excerpts of a real `CLAUDE.md` and `comms.md`. Walk through verbally.

> "Four files turn Claude into a collaborator.
>
> **`CLAUDE.md` — who you are to Claude.** The slide shows an excerpt. Your role, your current priorities, your technical conventions, your writing preferences. Always loaded into every session. One big reason Claude gets better over time: you stop repeating yourself. I have a global one in `~/.claude/` and a project-specific one in each repo that overrides it where needed.
>
> **`comms.md` — the async channel.** When Claude has a question too big to answer inline, it writes here with a date. I answer when I have time. The excerpt on the slide is a real example from yesterday — Claude asking me how to handle low-rating jokes in the Bradley-Terry model. I answered later in the same file.
>
> *Analogy that will probably land:* I already keep a running meeting doc with Angela — questions I want to raise, things I've decided, things she's said. Most of you do the same with your advisor or a coauthor. **`comms.md` is that doc, with Claude.** Same workflow, same purpose, same etiquette — dated entries, newest at top, answer when you have time. Nothing new to learn; just a new collaborator to apply it to.
>
> **`current_state.md`** — one or two paragraphs on exactly where the project is. What we're working on, what's blocking, what's next. New session starts — Claude reads this — we pick up without re-explaining.
>
> **`todo.md`** — running task list Claude updates as we work. My log of what I asked for, what's done, what's still open.
>
> That's the memory. Machine-readable and human-readable, both. I can inspect and edit everything Claude remembers."

### 10:30–11:00 — The caveat (slide 11)

> "Before we demo: you are responsible for checking everything. The output is good enough now that it will be tempting not to. Resist that. I'll come back to this in Q&A because Katie asked exactly this question."

Transition slide to Survey Design.

---

## SURVEY DESIGN — 11:00–21:00

### 11:00–11:45 — Point at the skills repo (1 min)

Open the tutorial GitHub repo in a browser tab (pin this for now — you'll come back to it).

> "Quick note before we build. Every skill I use today is in this repo — link in the chat from Lyle in a second. You can clone it, copy-paste any of the 15 skills into `~/.claude/skills/`, and they work immediately. A few of them need you to replace a placeholder like `{{WORKSPACE}}` or a phone number — the README tells you which. That's how you get started without waiting."

### 11:45–15:30 — Qualtrics: build the joke task (3:45 min)

Switch to terminal.

> "Let's build a real study. Something agency-flavored. People show up, do a creative task — write a joke — with or without AI help. Then we measure process agency, outcome agency, and meaning. And we randomize feedback.
>
> The qualtrics-survey skill I'm about to use isn't built into Claude Code — it's a Python package I wrote that calls the Qualtrics API. It's public on GitHub, and the skill tells Claude to install it if it's missing. Please file bugs or feature requests."

Prompt (via WisprFlow, plan mode):
> "/qualtrics-survey. Plan mode first. Build me a between-subjects pilot. Participants log in, see the instructions, write a short joke. Two conditions: with AI writing assistance or without. They answer three process-agency items. Then they get randomized feedback — positive or negative — independent of the actual joke. Then three outcome-agency items. Then three meaning items. 200 subjects on Prolific US. Install the qualtrics_sdk package from GitHub first if it's not already there. Show me the item wording before you write any code."

**When the plan + items appear: read them on-stream.** This is the check-your-work moment:

> "This is the verification step Katie asked about. I'm reading every item before any code runs. My global CLAUDE.md enforces this for anything that codes or rates text — you don't let Claude ship until you've read what it's going to build."

Approve the plan. Let it generate. Tab to Qualtrics, refresh, show the survey exists.

### 15:30–16:30 — Iterate once (1 min)

> "Now a quick edit. I want a bot-resistant attention check after the manipulation."

Prompt:
> "Add an attention check after the manipulation, before the process-agency block. Use the cat-holding-a-math-problem format — an image of a cat holding a whiteboard with a simple arithmetic problem, and participants have to type the answer. Fail the survey if they get it wrong. Bots are bad at reading images of math, so this catches both inattentive humans and LLM-powered bots."

> "You could keep iterating like this forever. I won't — in practice I'd do maybe 5-6 rounds and call it good."

### 16:30–17:30 — Drawbacks of Qualtrics (1 min)

> "Two reasons Qualtrics isn't always the right tool.
>
> **One: custom stuff is hard.** Right now, feedback is randomized — participants get fake positive or negative feedback. What if I want *real* feedback instead? Every joke would need to be rated by other participants, and the feedback would need to be computed live. Qualtrics cannot do that. You need a server.
>
> **Two: iteration is slow.** Every change requires the survey to be re-deployed and re-tested. On a self-hosted app, a code change is live the moment it pushes.
>
> Let's move to the alternative."

### 17:30–20:30 — Render-survey: extend the joke task (3 min)

> "The render-survey skill scaffolds a full-stack web app — React front-end, Express back-end, MongoDB database — and deploys it to Render. The skill does the app scaffolding; you need a GitHub account, a Render account, and a MongoDB Atlas account to host. I won't walk through that setup here, but it's free for the scale a research lab needs, and happy to help you set it up in office hours after."

Open `agency6-experiment/` in Claude Code as the visible example. 30-second tour.

Prompt:
> "/render-survey. Take the joke task we just built in Qualtrics, but change the feedback stage. Instead of randomized feedback, participants get real peer ratings of their joke — we collect ratings from previous participants, and if fewer than three have rated a joke, we backfill with AI ratings using the same rating prompt. Keep everything else identical. Scaffold the app."

Talking point while it builds:

> "Now — the reproducibility benefit, which is directly Katie's first question. The git commit hash gets saved with every single participant's data row. That means my dataset is tied to the exact version of the materials and code that produced it. **Tamper-evident**: if anyone changes a single byte of the materials or code, the commit hash changes, and the link breaks. You can roll back to any commit and see exactly what participants saw. Fully reproducible with zero extra effort. You cannot do this in Qualtrics."

### 20:30–21:00 — Transition (30 sec)

> "Okay — I've collected data. Let's clean it and analyze it, live."

Name-drop: "`/wbl-form-filler` fills Wharton Behavioral Lab submission forms, and there's a Chrome skill that can post HITs to Prolific — both save real hours, both are in the repo. Moving on."

---

## DATA ANALYSIS — 21:00–31:00

Cleaning and analysis go in **one QMD file**, not separate scripts. Run the whole thing top to bottom as a literate document. Easy to read, easy to audit, easy to re-render.

### 21:00–26:00 — Clean + transform (5 min)

Open `analysis/report.qmd` briefly to show where you'll work.

Prompt:
> "/data-analysis. I have the raw joke-task data in `data/raw/`. It's messy — lots of metadata columns, unparsed feedback fields, condition codes that need decoding. Build a cleaning chunk in `analysis/report.qmd` that outputs a clean CSV with only the columns I need for analysis: participant ID, condition, joke text, joke rating if any, process-agency score, outcome-agency score, meaning score. Apply my standard exclusions: failed attention check, duration under 60 seconds, duplicate IPs. Save the clean file with the commit hash in the filename."

Narrate:
> "Cleaning lives inside the QMD, right next to the analysis. No separate preprocessing script. When someone wants to reproduce this paper, they render this one file and they see everything — the exclusions, the transforms, the models, the plots. No hidden state."

### 26:00–30:00 — Analysis: condition differences + Bradley-Terry (4 min)

Prompt:
> "Now run the analysis. Two parts. First: between-condition differences on process agency, outcome agency, and meaning — t-tests with 95% CIs and Cohen's d. Second: Bradley-Terry model of joke quality, using the peer ratings as pairwise comparisons. We want to see if the AI-assisted jokes rank higher than solo jokes. Use `BradleyTerry2` or a lavaan-compatible formulation. Render the QMD to HTML when done."

Talking points while it runs:
> "Bradley-Terry is the right tool here because the data is pairwise — participants rated some jokes but not all, and we want a latent quality score that's comparable across jokes. Don't hardcode anything — every number in the output should come from a live computation."

> "Notice the convention: lavaan for SEM-flavored stuff, not the mediation package. That's a rule in my global CLAUDE.md — I set it once and never re-specify it. Claude just knows."

Show the rendered HTML. Point to one effect size: "That number would go directly into the paper."

### 30:00–31:00 — `/log-off` (1 min)

Prompt:
> "/log-off"

Narrate:
> "End-of-session ritual. Updates `todo.md` with what got done. Writes a session summary to `comms.md`. Overwrites `current_state.md` with a fresh cold-start handoff for next time. Commits and pushes if we're in a git repo. I literally run this at the end of every work block — it's the best habit I've picked up this year."

---

## WRITING METHODS AND RESULTS — 31:00–41:00

### 31:00–32:30 — Why do writing with AI? (1.5 min)

> "The benefit I care about most here isn't speed. It's **reproducibility — no magic numbers**.
>
> When you write methods and results by hand, every number in the manuscript is a potential bug. You compute the effect size, you type it into the draft, then the analysis changes — maybe you add an exclusion — and now your manuscript says 0.42 but the code produces 0.38. This happens constantly. It's how errors survive into published papers.
>
> When Claude writes your methods and results inside a QMD or LaTeX document, every number is **generated by code at render time**. Change the exclusion, re-render, every number updates automatically. The manuscript is always in sync with the analysis. This is why QMD and LaTeX are worth the overhead."

### 32:30–35:30 — `/pipeline-audit` — KEY DEMO (3 min)

> "And this is the tool that catches it when you mess up. This is the one I'd tell everyone in this audience to install today."

Prompt:
> "/pipeline-audit"

> "It scans my code, my manuscript, and the outputs, and checks for internal consistency. Hardcoded numbers. Narrative claims that don't match the results. Stats reported wrong. Figure captions that contradict the figure. It's my direct answer to Katie's hallucination question."

When it flags anything, read it out loud on-stream. If it flags nothing: "A clean audit means the paper is internally consistent right now. Worth running again after any change."

### 35:30–37:30 — LaTeX workflow: Overleaf collab (2 min)

> "My preferred writing setup: LaTeX via Overleaf, backed by a GitHub repo. Once the analysis is done and I'm drafting, this gives me real-time collaboration with coauthors without anyone breaking the numbers. Coauthors edit in Overleaf; Overleaf auto-syncs with GitHub; I pull on my side; numbers stay linked to the code that produced them."

Prompt:
> "/latex-workflow — commit the paper changes and push. Coauthors pick up in Overleaf."

### 37:30–39:00 — Google Docs caveat (1.5 min) — the punchline

> "Some coauthors won't touch Overleaf. They live in Google Docs. There's a skill for that — `/latex-gdoc-roundtrip` — which translates the LaTeX into a formatted Google Doc and brings edits back. Here's the thing to understand though.
>
> **Once you move the text to Google Docs, you destroy the link between the numbers and the code.**
>
> Scenario: you write your results section with live numbers in LaTeX. You export to Google Docs. Your coauthor edits the prose. Great, everyone's happy. Then you decide to exclude participants who reported cheating. The analysis re-runs, the numbers should all change — but the numbers are now frozen strings inside a Google Doc. Somebody has to notice the discrepancy and hand-edit each one. That's where errors come from.
>
> LaTeX + Overleaf keeps the link alive the whole way. Google Docs breaks it. If you have to use Docs, use it for the final polish — after your numbers are locked."

### 39:00–41:00 — Write methods + results, PDF live on the side (2 min)

Set up: PDF of the paper open in Preview on one side, terminal on the other.

Prompt:
> "/research-writing. The analysis is done. Write the methods and results sections. For methods: describe participants (pull real demographics from the data), describe materials (link to the GitHub commit for the survey), describe the procedure. For results: describe the condition differences on process agency, outcome agency, and meaning, then describe the Bradley-Terry quality comparison. Use my writing conventions from global CLAUDE.md — strong topic sentences, no passive voice, no vague quantifiers, always quantify."

> "Watch the PDF. I'm going to fire comments at Claude — 'tighten this paragraph,' 'move the effect size here,' 'the topic sentence buries the lede' — and you'll see the PDF update in real time on the side. This is the loop."

Fire 2-3 edits verbally, let the PDF re-render live.

Transition to Q&A.

---

## Q&A — 41:00–51:00

Lyle has been collecting questions in chat. Take his queue.

### Katie Q1 — "As-Collected" and validating data as collected, not fabricated

**Short answer to deliver:**

> "AsCollected is a registry where you deposit a row per study describing: when the data was collected, where, the data ID, the non-author contributors, and anything else. Author identity is independent of the data, which is good for us because it means we can register the data without complicating authorship.
>
> Here's what I do that slots into AsCollected cleanly: **Prolific is the pool**, which is a clean 'where.' The **raw data source is a timestamped MongoDB collection** — every row has a server-side timestamp, not a client one, so fabrication would need to beat Mongo's append log. I can post the whole raw database alongside the paper. And the **data ID is the GitHub commit hash** at the time of data collection — so if anyone changes a single byte of the materials or code, the hash changes, and the link breaks. The provenance is tamper-evident.
>
> Full provenance claim: 'Pool = Prolific; raw data = timestamped Mongo dump posted at URL X; data ID = git SHA abc123, which uniquely identifies the exact materials and code that generated this data.' That's as-collected, not fabricated."

### Katie Q2 — Checks against Claude hallucinations in analysis

**Short answer to deliver:**

> "Two mechanisms and an opinion.
>
> **Mechanism one: `/pipeline-audit`**, which I just showed. Every time I change anything in the code or the manuscript, it re-audits: hardcoded numbers, narrative-vs-result mismatches, stats-reporting errors. If the audit is clean, the paper is internally consistent.
>
> **Mechanism two: read the QMD, line by line.** I print the rendered HTML and read it top to bottom, with the code chunks visible. This is non-negotiable for any analysis I'm putting my name on. Takes 20 minutes for a typical paper. The QMD format is designed for this — executable code and narrative prose in one document in reading order.
>
> **The opinion:** I think well-prompted Claude code is, on average, cleaner and less bug-prone than what I'd write by hand. Humans forget to apply exclusions consistently. Humans hardcode magic numbers. Humans write `rowwise` when they meant `groupwise`. Claude does these things less often than I do, provided I've told it clearly what I want. The check-your-work discipline is the same you'd apply to an RA's code — just faster, cheaper, more iterable."

### 47:00–50:00 — Open floor / Lyle's queue

If no questions in chat, ask via Lyle:
> "What's one research task you'd want to see done this way? Drop it in chat — I'll try one live if we have time, otherwise bring it to office hours after."

### 50:00–51:00 — Off-ramp

> "Thanks for staying muted. Angela, Lyle — thank you. Sticking around for 30 min on this Zoom for one-on-one setup help. Recording and skills repo in the shared doc."

---

## Fallback plans

| If this breaks... | Do this |
|---|---|
| Qualtrics API 401s | Switch to showing the last survey you built on qualtrics.com; verbally describe what you would have asked for. |
| `qualtrics_sdk` package install fails | Show the `/qualtrics-survey` SKILL.md directly; explain the package is on GitHub and recovery is a 5-line fix. |
| Render deployment fails | Read the `/render-survey` SKILL.md + show `agency6-experiment/` structure; skip the live build. |
| QMD render fails mid-demo | Show the `.qmd` file itself; say "in practice, I'd step through chunk by chunk." |
| Bradley-Terry package missing | Fall back to a simpler "mean rating per condition" analysis. Acknowledge: "the full BT analysis would take this one extra step." |
| `/pipeline-audit` finds nothing to flag | "Clean audit means the paper is currently consistent — here's a screenshot from when it caught a real bug." Have a screenshot ready. |
| `/latex-gdoc-roundtrip` auth fails | Skip the demo, deliver the Google Docs caveat verbally. That caveat is the punchline, not the live demo. |
| Claude Code hangs on a long task | Ctrl-C, say "in practice I'd let it run in the background or use `/loop`." Move on. |
| WisprFlow dies | Switch to keyboard, acknowledge, keep going. |
| Full terminal crash | Second terminal is pre-cd'd. Switch windows. |

---

## Post-demo debrief (do within 1 hour)

- [ ] Note what ran over-time, what went faster than planned
- [ ] Note which prompts landed, which needed re-phrasing live
- [ ] Save chat transcript from Zoom
- [ ] Update this file for the potential sequel Angela mentioned
