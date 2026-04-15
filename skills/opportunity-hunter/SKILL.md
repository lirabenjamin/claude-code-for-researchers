---
name: opportunity-hunter
description: Search for and rank job openings, grants, prizes, and fellowships relevant to the user's profile. Produce a structured markdown report saved to disk.
---

# Opportunity Hunter

Search for and rank job openings, grants, prizes, and fellowships relevant to the user's profile. Produce a structured markdown report.

## Trigger
Run when the user asks to find opportunities, scan the job market, or check for grants/fellowships/prizes.

> **Setup note:** This skill reads the user's profile from `~/.claude/CLAUDE.md`. Make sure your CLAUDE.md has a section describing your role, fields, target positions, career stage, and (if applicable) immigration/visa status. Replace `{{REPORTS_DIR}}` below with where you want reports saved.

---

## Step 0: Load Profile

Pull candidate profile from `~/.claude/CLAUDE.md`. You need at least:

- **Name**
- **Current role**
- **Fields** (research areas, disciplines)
- **Methods** (experimental, computational, theoretical, etc.)
- **Target positions** (academic TT? industry research? think tank? specify departments and seniority)
- **Career stage** (years post-degree, current rank)
- **Immigration status** (citizenship, visa, pathway) — if relevant. Cap-exempt employers, H-1B sponsorship requirements, roles requiring US citizenship/clearance all matter here.

If `~/.claude/CLAUDE.md` lacks these details, ask the user once, then save to CLAUDE.md before continuing.

---

## Step 1: Search (WebSearch — ~50 queries)

Run WebSearch queries across **5 categories**. Use the current date to make queries timely (e.g., "2026-2027 academic job market"). Vary phrasing to maximize coverage. Substitute the user's fields and target positions into the query patterns below.

### Category A — Academic Jobs (TT)
Search for tenure-track assistant professor positions in the user's target departments (e.g., marketing, management, OB, decision sciences, behavioral science, consumer behavior, or whatever fields they listed).

Target query patterns (substitute `{FIELD}` with each target field):
- `"assistant professor" {FIELD} 2026 2027`
- `tenure track {FIELD} faculty job`
- `{FIELD} faculty position`
- Check discipline-specific job boards (e.g., INFORMS, AMA, AOM, SJDM, Econ JOE, PhilJobs, etc.)
- Aggregators: HigherEdJobs; AcademicKeys; Chronicle

### Category B — Industry Research
Search for research scientist / research engineer roles at labs that match the user's fields:
- Major AI labs (Anthropic, OpenAI, DeepMind, Meta FAIR, Microsoft Research, Apple ML)
- Tech research orgs (Spotify Research, Netflix Research, Amazon Science, Uber, Airbnb)
- Think tanks relevant to the user's area (RAND, Brookings, BIT, ideas42, NBER, etc.)

Query patterns:
- `research scientist {FIELD} [company] 2026`
- `applied research {FIELD} tech`
- `{FIELD} researcher position`

### Category C — Grants
Search for grants matching the user's field and career stage. Major funders vary by discipline — examples:
- NSF directorates (SES, DRMS, DBI, etc.)
- NIH mechanisms (R21, R01, K-awards)
- Foundation grants (Russell Sage, Templeton, Spencer, Sloan, Kauffman, SSRC, etc.)
- Early-career fellowships (Sloan, NSF CAREER, K99/R00)
- Internal / institutional seed grants

Query patterns:
- `{FIELD} grant 2026 deadline`
- `early career grant {FIELD}`
- `NSF CAREER {FIELD} deadline`

### Category D — Prizes & Awards
Search for:
- Early-career awards in the user's discipline
- Best-paper awards in target journals
- Rising-star awards from relevant societies
- Dissertation awards (if still eligible)

Query patterns:
- `early career award {FIELD} 2026`
- `best paper award {FIELD} 2026`
- `rising star {FIELD}`

### Category E — Fellowships & Visiting Positions
- CASBS, Berkman Klein, Schmidt Futures, Radcliffe, Santa Fe Institute
- Visiting scholar programs at top departments
- Sabbatical-replacement visiting positions
- Discipline-specific fellowships

---

## Step 2: Link Verification & Deep Fetch (WebFetch — ALL results)

### CRITICAL: Verify every link before including it in the report.

**For EVERY opportunity you plan to include**, you MUST WebFetch the URL to confirm:
1. The page actually loads (not 404, not a generic careers page)
2. The specific listing/program described actually exists at that URL
3. The details (title, deadline, eligibility) match what the search snippet said

**If a link fails or doesn't match:**
- Try to find the correct URL via a follow-up WebSearch
- If you still can't get a working link, mark it as `🔗 Link unverified — check [organization website]` and provide the org's main URL instead
- NEVER include a dead or unverified link without flagging it

**For the most promising ~20 results**, do a deeper fetch to extract:
- Full job/grant description
- Confirm deadline (flag if unverifiable)
- Check eligibility criteria (career stage, citizenship, field)
- Note immigration/visa information if relevant to the user
- Get application requirements (what materials are needed)

**Common link pitfalls to watch for:**
- Job board links expire quickly — always verify
- Company career pages use JS rendering that WebFetch can't parse — provide a search path instead (e.g., "Search careers.microsoft.com for '{FIELD}'")
- Grant program URLs change year-to-year
- Academic job board aggregators may link to expired postings

---

## Step 3: Score Each Opportunity

Rate each opportunity **1-10** using this weighted rubric. Adjust weights if the user's CLAUDE.md specifies different priorities.

| Criterion | Default weight | Description |
|-----------|----------------|-------------|
| **Field match** | 25% | How well does the role/grant align with the user's research? |
| **Career stage** | 20% | Is this appropriate for the user's current career stage? |
| **Immigration compatibility** | 20% | Can the user apply given their visa/citizenship status? (Skip this criterion if not applicable; redistribute weight across others.) |
| **Prestige / impact** | 15% | Institutional reputation, career signal value |
| **Deadline feasibility** | 10% | Is there enough time to prepare a strong application? |
| **Compensation / funding** | 10% | Salary, grant size, or award amount |

**Composite score** = weighted sum, rounded to 1 decimal.

---

## Step 4: Generate Report

Create a structured markdown report with these sections:

### Report Structure

```markdown
# Opportunity Report — [YYYY-MM-DD]

## Executive Summary
- Total opportunities found: X
- Top 3 highlights (with one-line reason each)
- Urgent deadlines in next 30 days
- Key seasonal note

## A. Academic Jobs (Tenure-Track)
| # | Position | Institution | Fit Score | Deadline | Link |
|---|----------|-------------|-----------|----------|------|

### Detailed Entries
For each:
- **Position:** [title]
- **Institution:** [name, department]
- **Link:** [URL]
- **Deadline:** [date — flag if unverified with ⚠️]
- **Fit score:** [X/10]
- **Why it fits:** [1-2 sentences]
- **Immigration notes:** [if relevant]
- **Application requirements:** [materials needed]
- **Recommended action:** [Apply / Watch / Skip — with reasoning]

## B. Industry Research
[Same table + detailed format]

## C. Grants
[Same table + detailed format]

## D. Prizes & Awards
[Same table + detailed format]

## E. Fellowships & Visiting Positions
[Same table + detailed format]

## Immigration-Flagged Opportunities (if applicable)
List all opportunities where immigration status is a concern or advantage, with specific notes.

## Upcoming Deadlines (Next 90 Days)
| Date | Opportunity | Category | Action Needed |
|------|-------------|----------|---------------|

## Methodology
- Date of search: [date]
- Number of queries: [N]
- Sources checked: [list]
- Limitations: [e.g., some deadlines may have changed]
```

---

## Step 5: Save Report

Save the completed report to:
```
{{REPORTS_DIR}}/[YYYY-MM-DD]-opportunity-report.md
```

---

## Step 6: Notify (optional)

If the user has the `notify-me` skill installed, trigger it with a short summary:
```
Opportunity report ready: [X] opportunities found. Top pick: [best one]. [N] deadlines in next 30 days.
```

---

## Anti-Hallucination Rules

These are **critical**. Violating them makes the report useless.

1. **Never fabricate a listing.** Every opportunity must come from an actual WebSearch or WebFetch result.
2. **Flag unverified deadlines** with ⚠️. If a deadline cannot be confirmed from the source page, say so explicitly.
3. **Do not guess application URLs.** Only include links you actually retrieved AND verified via WebFetch.
4. **Every link in the final report must be WebFetch-verified.** If you could not load the page, mark it with `🔗 Link unverified` and explain how to find it manually.
5. **If a search returns no relevant results for a category, say so.** Do not fill the section with tangentially related results to look comprehensive.
6. **Distinguish between confirmed open positions and recurring annual opportunities** where the current cycle may not be open yet.
7. **Never construct URLs by pattern-matching.**
8. **If WebFetch fails on a JS-heavy page** (common for Ashby, Greenhouse, Workday, Lever), note this and provide a manual search path.

---

## Seasonal Awareness

The academic job market is highly seasonal (at least in the US):
- **Aug–Dec:** Peak TT job postings (most schools post Sept–Nov)
- **Jan–Mar:** Flyouts and offers
- **Apr–Jun:** Late-cycle and failed-search re-postings
- **Year-round:** Industry roles, some grants

Interpret search results accordingly. If running outside peak season, note which recurring opportunities to watch for and when they typically open.

---

## Design Principles

- **Err on comprehensiveness.** Include borderline-relevant opportunities. The user can cut; they can't find what you didn't show them.
- **Immigration is a dealbreaker if flagged.** If the user has immigration constraints in CLAUDE.md, respect them rigorously.
- **Actionability over description.** Every entry should end with a clear recommended action.
- **Real links only.** Every URL must be from an actual search/fetch result.
