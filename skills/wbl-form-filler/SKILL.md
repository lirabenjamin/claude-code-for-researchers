---
name: wbl-form-filler
description: Fill out Wharton Behavioral Lab (WBL) study submission forms on JotForm. Use this skill whenever the user mentions WBL forms, study submission forms, scheduling a study launch, MKT form, OID form, Wharton Behavioral Lab, or wants to submit a study to the lab. Also trigger when user pastes a filled-in markdown template for either the MKT or OID form.
---

# WBL Study Submission Form Filler

> **Wharton-specific skill.** Only useful if you submit studies through the Wharton Behavioral Lab. If you run studies through a different lab, adapt this skill to that lab's forms — the Chrome automation pattern is the reusable part.

This skill helps fill out the two Wharton Behavioral Lab JotForm study submission forms:

- **MKT form**: https://www.jotform.com/241085735774060 (Marketing department)
- **OID form**: https://form.jotform.com/213328023193044 (OID department)

## Workflow

### Step 1: Generate the MD template

When the user asks to fill a WBL form, generate the appropriate markdown template below so they can fill it in and paste it back. Pre-fill any known defaults the user has stored.

### Step 2: Fill the form in Chrome

When the user pastes back a completed template:
1. Use `tabs_context_mcp` to get/create a tab
2. Navigate to the form URL
3. Use `read_page` with `filter="interactive"` to get element refs
4. Use `form_input` to fill each field
5. **Do NOT click Submit** — always let the user review and submit manually

### Known Defaults (REPLACE WITH YOUR OWN)

The defaults block below is an example. Replace with your own name, email, faculty contacts, IRB numbers, and budget codes before using. These values never change between studies, so storing them saves time.

**MKT form example defaults:**
- Name: {{USER_FULL_NAME}}
- Email: {{USER_EMAIL}}
- Faculty Contact: {{MKT_FACULTY_CONTACT}}
- IRB: {{MKT_IRB_NUMBER}}
- Funding Source: {{MKT_FUNDING_SOURCE}}
- Budget Code: {{MKT_BUDGET_CODE}}

**OID form example defaults:**
- Name: {{USER_FULL_NAME}}
- Email: {{USER_EMAIL}}
- Faculty Contact: {{OID_FACULTY_CONTACT}}
- IRB: {{OID_IRB_NUMBER}}
- Funding Source: {{OID_FUNDING_SOURCE}}
- Budget Code: {{OID_BUDGET_CODE}}

---

## MKT Form Template

```markdown
# MKT Study Submission

## Your Info
- First Name: {{USER_FIRST_NAME}}
- Last Name: {{USER_LAST_NAME}}
- Email: {{USER_EMAIL}}

## Collaborator (leave blank if none)
- Collaborator First Name:
- Collaborator Last Name:
- Collaborator Email:

## Scheduling
- Launch Date: YYYY-MM-DD
- Launch Time: (e.g. 9:00 AM)

## Study Details
- IRB #: {{MKT_IRB_NUMBER}}
- Project Title:
- Faculty Contact: {{MKT_FACULTY_CONTACT}}
- Funding Source: {{MKT_FUNDING_SOURCE}}
- Budget Code: {{MKT_BUDGET_CODE}}

## Platform & Participants
- Panel: (Connect / Prolific / MTurk) [Default to Prolific if unsure]
- HIT Title:
- HIT Description:
- Number of Participants:
- Pay per Participant:
- Expected Duration (minutes):
- Total Study Cost Including Fees: (Prolific cost is 1.33 times the participant's pay — calculate based on the inputs above.)
- Worker Qualifications/Exclusions: (Default is 95% approval rate and speaks English.)

## Survey
- Survey Link:
- Seeking WBL subsidy?: (Yes / No)
- Qualtrics Survey Title (if seeking subsidy):
- Confirmed permissions to WBLResearchData@wharton.upenn.edu?: (Yes / No)
- Completion Code/Redirect:

## Requirements
- Study Requirements: (No mobiles / Audio / Microphone / Writing / Desktop Only / Tablet Only / Mobile Only / Bot Check / LLM Check / None of these)

## Additional Comments
```

---

## OID Form Template

```markdown
# OID Study Submission

## Your Info
- First Name: {{USER_FIRST_NAME}}
- Last Name: {{USER_LAST_NAME}}
- Email: {{USER_EMAIL}}

## Study Details
- Project Name (internal):
- IRB #: {{OID_IRB_NUMBER}}
- Faculty Contact: {{OID_FACULTY_CONTACT}}
- Funding Source: {{OID_FUNDING_SOURCE}}
- Budget Code: {{OID_BUDGET_CODE}}

## Scheduling
- Launch Date: YYYY-MM-DD
- Launch Time: (e.g. 10:00 AM)

## Platform & Participants
- Panel: (Prolific / MTurk / Connect / TeenVoice)
- Number of Participants:
- Pay per Participant:
- Will you be offering a bonus? If so, how much?:
- Expected Duration (minutes):
- Total Participant Compensation Including Fees:
- Worker Qualifications/Exclusions:

## HIT Details
- HIT Title:
- Description:
- Keywords:

## Survey
- Survey Link:
- WBL Subsidy: (I have done this, and will share the title below / I am not seeking the WBL subsidy)
- Qualtrics Survey Title:
- Confirmed permissions to WBLResearchData@wharton.upenn.edu?: (Yes / No)
- Payment Code:

## Additional Comments
```

---

## Form Filling Notes

- The date picker on both forms is a calendar widget. Use JavaScript to set date values if `form_input` doesn't work on the date field.
- Time slots are a listbox — use `form_input` with the option text (e.g. "9:00 AM").
- Checkboxes for study requirements (MKT) need individual toggling.
- The MKT form scrolls — you may need to read the page multiple times or use `ref_id` to find lower fields.
- Always re-read the page (`read_page`) immediately before filling, as refs can go stale.
- **Never click Submit.** Let the user review first.
