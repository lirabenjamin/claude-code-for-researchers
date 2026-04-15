---
name: render-survey
description: Scaffold and deploy a full-stack behavioral research survey (React + Express + MongoDB) on Render. Supports between-subjects conditions, phased survey flows, AI-assisted tasks, bot detection, keystroke tracking, and platform integrations (Prolific, CloudResearch Connect, Gallup). User describes conditions, stimuli, and measures; skill generates the complete app.
user_invocable: true
---

# Render Survey Builder

You are scaffolding a **production-ready behavioral research survey** as a single-page React app with an Express API and MongoDB backend, deployed on Render. The user describes their experiment (conditions, stimuli, task, measures) and you generate the complete application.

## Architecture Overview

```
project/
├── server.js              # Express API (submit, survey, config, scoring)
├── studies.yaml           # Study configs (conditions, feedback, instrumentation)
├── vite.config.js         # Vite build config with git commit/tag injection
├── render.yaml            # Render deployment config
├── package.json           # Dependencies
├── .env                   # API keys (never commit)
├── .gitignore
├── src/
│   ├── App.jsx            # All screens in one file (state machine pattern)
│   └── App.css            # Responsive styles
└── public/
    └── [stimulus files]   # Images, videos, etc.
```

## Core Design Principles

1. **Single-file SPA**: All screens live in `App.jsx` as a state machine (`screen` state variable). No router needed.
2. **YAML-driven configuration**: All study parameters (conditions, feature flags, instrumentation) are defined in `studies.yaml` and served via `/api/config`.
3. **Client-side randomization**: Condition assignment happens client-side from server-provided condition list. Stored in `sessionStorage` for persistence across reloads. URL param `?condition=X` forces a condition for testing.
4. **Version tracking**: Git commit hash and tag are injected at build time via Vite `define` and sent with every submission as `appVersion`.
5. **Test mode**: `?test=1` writes to a `testing` collection instead of production data. `?admin=1` shows a panel to preview all conditions.
6. **Platform-agnostic**: Works with Prolific (`PROLIFIC_PID`, `STUDY_ID`, `SESSION_ID`), CloudResearch Connect (`participantId`, `assignmentId`, `projectId`), Gallup, or standalone.

## Scaffolding Steps

When the user describes their experiment, follow these steps:

### Step 1: Clarify the design

Ask the user to confirm (if not already specified):
- **Between-subjects conditions**: What are they? (e.g., "solo", "ai-assisted", "human-feedback")
- **Stimulus**: What do participants see? (image, text, video?)
- **Task**: What do participants do? (write, rate, choose, etc.)
- **Measures**: What survey items are collected? (Likert scales, open-ended, etc.)
- **Flow**: What order do screens appear? (intro -> task -> survey -> results -> done is default)
- **Feedback**: Do participants receive performance feedback? What type?
- **Platform**: Prolific, Connect, MTurk, standalone?
- **Instrumentation**: Keystroke tracking? Tab-leave detection? Bot detection (Turnstile)?
- **AI integration**: Does any condition involve an AI tool? What does it do?

### Step 2: Generate `studies.yaml`

Define each study variant. Available fields:

```yaml
study_name:
  study: unique_id          # Used in ?study= URL param
  platform: prolific        # prolific, connect, gallup, standalone
  prolific_completion_url: https://...  # Redirect after completion
  conditions: [solo, ai-assisted]       # Between-subjects conditions
  sample: adult             # adult or kid
  min_votes: 0              # Pairwise comparisons before continuing (0 = skip)
  scoring: none             # none, elo_and_llm, pretrained_model
  feedback_type: null       # null, honest_coarsened, deceptive
  force_ai_compliance: false  # Require AI use before task submission
  track_keystrokes: true    # Log keystrokes with timestamps
  track_tab_leaves: true    # Detect and log tab/window switches
  bot_detection: true       # Cloudflare Turnstile + honeypot
  show_consent: true        # Show IRB consent screen before intro
```

### Step 3: Generate `server.js`

The Express server must include:

```javascript
// Required endpoints:
// GET  /api/config?study=X    → Returns study config (conditions, feature flags)
// POST /api/submit            → Saves task response to MongoDB
// POST /api/survey            → Saves survey phase responses
// GET  /api/results/:id       → Returns results/feedback for participant
```

**Key patterns:**
- Spread `req.body` into the MongoDB document, then add server-side fields (`createdAt`, `status`, moderation results)
- Score/evaluate submissions asynchronously (fire-and-forget after responding to client)
- Use `studies.yaml` for all configuration — never hardcode study parameters
- Serve the Vite-built `dist/` folder in production

**Bot detection** (when enabled):
- Verify Cloudflare Turnstile token server-side
- Check honeypot field (hidden form input that bots fill)
- Record `botTimingMs` (time from page load to submission)
- Block and record bot submissions with `status: 'bot_blocked'`

### Step 4: Generate `App.jsx`

**Screen state machine pattern:**

```jsx
const [screen, _setScreen] = useState('consent');
const [screenTimestamps, setScreenTimestamps] = useState({});
const setScreen = (s) => {
  setScreenTimestamps(prev => ({ ...prev, [s]: new Date().toISOString() }));
  _setScreen(s);
};
```

**Standard screen flow:**
1. `consent` — IRB consent (skip if `show_consent` is false)
2. `intro` — Welcome + step overview
3. `identity_survey` — Pre-task measures (+ attention check if bot detection enabled)
4. `write` / `task` — The main task screen (with optional AI assistant)
5. `process_survey` — Process measures (collected right after task)
6. `rate` — Pairwise comparisons (skip if `min_votes` is 0)
7. `results` — Performance feedback
8. `outcome_survey` — Outcome measures (collected after feedback)
9. `meaning_survey` — Meaning/experience measures
10. `open_ended` — Free-text questions
11. `debrief` — Deception debrief (only if deceptive feedback used)
12. `done` — Completion + redirect to platform

**Condition assignment:**

```jsx
function getCondition(conditionsList) {
  const params = new URLSearchParams(window.location.search);
  const forced = params.get('condition');
  if (forced) { sessionStorage.setItem('condition', forced); return forced; }
  const stored = sessionStorage.getItem('condition');
  if (stored) return stored;
  const assigned = conditionsList[Math.floor(Math.random() * conditionsList.length)];
  sessionStorage.setItem('condition', assigned);
  return assigned;
}
```

**Survey question renderer** (0-10 Likert scale):

```jsx
const renderScaleQuestion = (q) => (
  <div key={q.id} className="survey-question">
    <p className="question-text">{q.text}</p>
    <div className="scale">
      {Array.from({ length: 11 }, (_, i) => (
        <button
          key={i}
          className={`scale-btn ${ratings[q.id] === i ? 'scale-btn-active' : ''}`}
          onClick={() => setRating(q.id, i)}
        >{i}</button>
      ))}
    </div>
    <div className="scale-labels">
      <span>{q.low}</span>
      <span>{q.high}</span>
    </div>
  </div>
);
```

**AI assistant pattern** (for AI-assisted conditions):

```jsx
async function askAI() {
  const res = await fetch(`${API_URL}/api/ai-assist`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, context })
  });
  const data = await res.json();
  setAiResponses(prev => [...prev, { prompt, reply: data.reply }]);
}
```

- AI interactions are logged in the submission payload as `aiInteractions: [{ prompt, reply }]`
- Server-side API key proxy (never expose keys to client)
- Rate limiting per IP
- `force_ai_compliance`: Block task submission until AI has been used at least once

**Payload pattern** — every POST to `/api/submit` and `/api/survey` must include:

```javascript
{
  condition, sample, study, configStudy,
  // Platform IDs (auto-detected from URL params):
  prolificPid, prolificStudyId, prolificSessionId,
  timestamp: new Date().toISOString(),
  appVersion: APP_VERSION,  // { gitCommit, gitTag }
  screenTimestamps,         // ISO timestamps for each screen visit
  // Conditional instrumentation:
  keystrokes,               // if trackKeystrokes
  tabLeaves,                // if trackTabLeaves
  honeypotValue, botTimingMs, turnstileToken,  // if botDetection
}
```

### Step 5: Generate `vite.config.js`

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { execSync } from 'child_process'

function gitInfo() {
  try {
    const commit = execSync('git rev-parse --short HEAD', { encoding: 'utf8' }).trim()
    const tag = execSync('git describe --tags --always 2>/dev/null || echo ""', { encoding: 'utf8' }).trim()
    return { commit, tag }
  } catch { return { commit: 'unknown', tag: '' } }
}
const git = gitInfo()

export default defineConfig({
  plugins: [react()],
  define: {
    __GIT_COMMIT__: JSON.stringify(git.commit),
    __GIT_TAG__: JSON.stringify(git.tag),
  },
})
```

### Step 6: Generate `render.yaml`

```yaml
services:
  - type: web
    name: [project-name]
    runtime: node
    plan: free
    buildCommand: npm install && npm run build
    startCommand: npm start
    envVars:
      - key: MONGODB_URI
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: NODE_ENV
        value: production
```

### Step 7: Generate `package.json`

Core dependencies:
```json
{
  "type": "module",
  "dependencies": {
    "cors": "^2.8.6",
    "dotenv": "^17.3.1",
    "express": "^5.2.1",
    "mongodb": "^7.1.0",
    "react": "^19.2.4",
    "react-dom": "^19.2.4",
    "yaml": "^2.8.2"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^6.0.0",
    "vite": "^8.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "server": "node server.js",
    "start": "node server.js"
  }
}
```

### Step 8: Generate `.gitignore`

```
node_modules
dist
.env
.DS_Store
```

### Step 9: Generate `App.css`

Use the responsive card-based design system:
- `.container` — max-width centered wrapper
- `.screen-card` — white card with shadow and padding
- `.primary-btn` — bold CTA button
- `.scale-btn` / `.scale-btn-active` — Likert scale buttons
- `.progress-bar` / `.progress-fill` — top progress indicator
- `.ai-section` — styled AI assistant panel
- `.survey-question` — question + scale layout
- Responsive: works on mobile and desktop

### Step 10: Generate admin panel

An `?admin=1` URL shows a panel with buttons to preview each condition:

```jsx
function AdminPanel() {
  function go(cond, study) {
    sessionStorage.removeItem('condition');
    window.location.search = `?condition=${cond}&study=${study || 'testing'}`;
  }
  return (
    <div className="container">
      <h1>Admin Demo</h1>
      {/* Buttons for each condition */}
    </div>
  );
}
```

### Step 11: Initialize git, deploy, and verify

```bash
git init
git add -A
git commit -m "Initial survey scaffold"
git tag v1.0.0
```

Then guide the user through:
1. Create a MongoDB Atlas free cluster and get the connection string
2. Create a Render account and connect the repo
3. Set environment variables on Render (MONGODB_URI, OPENAI_API_KEY if using AI)
4. Deploy and test with `?admin=1`

## Styling Reference

The default CSS provides a clean, professional survey look:
- White cards on light gray background
- Blue primary buttons (#2563eb)
- 0-10 Likert scale with circular buttons that highlight on selection
- Progress bar at the top of each screen
- Responsive layout (mobile-friendly)
- Tab-leave warning banner (red)
- AI assistant section (light purple/blue background)
- Feedback cards (green for positive, red for negative)

## Data Schema Reference

### `submissions` collection
```javascript
{
  condition: "solo",           // Assigned condition
  study: "prolific4",          // Study identifier
  configStudy: "prolific4",    // Study used for config (may differ if test mode)
  sample: "adult",             // Participant type
  caption: "...",              // Or whatever the task output is
  prolificPid: "...",          // Platform participant ID
  prolificStudyId: "...",      // Platform study ID
  prolificSessionId: "...",    // Platform session ID
  aiInteractions: [...],       // AI usage log (null if solo)
  appVersion: { gitCommit: "abc1234", gitTag: "v4.0.0" },
  screenTimestamps: { intro: "...", write: "...", ... },
  keystrokes: [{ key: "a", ts: 1234567890, field: "caption" }],
  tabLeaves: [{ leftAt: ..., returnedAt: ..., durationMs: ... }],
  honeypotValue: "",           // Should be empty for real humans
  botTimingMs: 45000,          // Time from page load to submission
  turnstile: { success: true, score: 0.9 },
  status: "approved",          // approved, rejected, bot_blocked
  elo: 1500,                   // If using pairwise comparisons
  voteCount: 0,
  createdAt: ISODate("...")
}
```

### `surveys` collection
```javascript
{
  submissionId: "...",         // Links to submissions._id
  condition: "solo",
  study: "prolific4",
  phase: "identity_process",   // identity_process, outcome_meaning, open_ended
  ratings: { question_id: 7, ... },
  scoreShown: 72,              // What feedback the participant saw
  appVersion: { gitCommit: "abc1234", gitTag: "v4.0.0" },
  screenTimestamps: { ... },
  createdAt: ISODate("...")
}
```

## Versioning Protocol

**Every deployment that participants will see must be tagged:**
```bash
git tag v[major].[minor].[patch]-[study_name]
git push origin --tags
```

Use semantic versioning:
- **Major**: Breaking changes to data schema or experiment design
- **Minor**: New conditions, measures, or screen changes
- **Patch**: Bug fixes, copy edits

The tag and commit hash are automatically embedded in every submission via the `appVersion` field.

## Common Customizations

### Different task types
- **Writing task**: textarea + optional AI assistant
- **Rating task**: Likert scales, sliders, or pairwise comparisons
- **Choice task**: Multiple-choice or forced-choice between options
- **Reading task**: Display text/stimulus, measure time on page

### Different AI integration modes
- `solo`: No AI
- `once-noprompt`: AI generates one response (fixed prompt)
- `once-prompt`: AI generates one response (user-written prompt)
- `many-noprompt`: Unlimited AI generations (fixed prompt)
- `many-prompt`: Unlimited AI generations (user prompts)
- `five-noprompt`: Batch of 5 AI responses at once
- Any of the above with `-scored`: Show instant AI evaluation of each generation

### Feedback types
- `null`: No structured feedback (just show completion)
- `honest_coarsened`: Top/bottom half relative to control condition
- `deceptive`: Randomly assigned positive/negative (requires debrief screen)
- Custom: Percentile, raw score, comparative ("better than X% of participants")

## Important Reminders

- Never hardcode API keys in source files. Use `.env` + environment variables.
- Always include `appVersion` in every database write so you can trace data to code.
- Use `?test=1` during development to avoid polluting production data.
- Tag every deployment before launching to participants.
- The admin panel (`?admin=1`) is for researchers only — participants never see it.
- Survey items should have versioned IDs (e.g., `outcome_capable_v2`) so that if wording changes, old and new responses are distinguishable in the data.
