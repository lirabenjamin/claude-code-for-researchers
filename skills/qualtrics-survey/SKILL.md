---
name: qualtrics-survey
description: Build a Qualtrics survey from specs using the qualtrics_sdk Python package. Give a description of your survey (questions, blocks, logic, embedded data) and this skill generates and runs a Python script to create it on Qualtrics.
---

# Qualtrics Survey Builder

You are building a Qualtrics survey using the `qualtrics_sdk` Python package. The user will describe what they want, and you will write and execute a Python script that creates the survey via the Qualtrics API.

## Setup

The script must start with:

```python
import os
from dotenv import load_dotenv
from qualtrics_sdk import QualtricsAPI

load_dotenv()
api = QualtricsAPI(
    api_token=os.getenv("QUALTRICS_API_TOKEN"),
    data_center=os.getenv("QUALTRICS_DATA_CENTER", "upenn.qualtrics.com")
)
```

Ensure the working environment has `qualtrics_sdk` installed. If not, install it:

```bash
pip install git+https://github.com/lirabenjamin/qualtricsapi.git
```

Also ensure a `.env` file exists with `QUALTRICS_API_TOKEN` and optionally `QUALTRICS_DATA_CENTER`.

## Available Methods

### Survey lifecycle
- `api.create_survey(name, language="EN")` -> `{"SurveyID": "SV_..."}`
- `api.get_survey(survey_id)` -> full survey definition
- `api.delete_survey(survey_id)` -> bool
- `api.list_surveys()` -> list of surveys
- `api.update_survey_name(survey_id, new_name)` -> bool
- `api.activate_survey(survey_id)` -> bool (REQUIRED before the survey URL will work)
- `api.deactivate_survey(survey_id)` -> bool
- `api.get_survey_url(survey_id)` -> URL string

### Blocks
- `api.create_block(survey_id, block_name)` -> `{"BlockID": "BL_..."}`
- `api.get_blocks(survey_id)` -> dict of all blocks

### Question types
All question methods accept optional `block_id` (for new questions) and `question_id` (to replace an existing question in place). They return `{"QuestionID": "QID..."}`.

**In-place replacement:** Pass `question_id="QID1"` to any create method to replace that question while preserving its position in the block. This changes the question type, text, choices — everything — without affecting order or page breaks.

- **Multiple choice:** `api.create_multiple_choice_question(survey_id, question_text, choices: list, selector="SAVR", allow_multiple=False, block_id=None)`
  - Selectors: `"SAVR"` (radio), `"SAHR"` (horizontal), `"DL"` (dropdown), `"MAVR"` (checkboxes), `"MAHR"` (horizontal checkboxes)
- **Text entry:** `api.create_text_entry_question(survey_id, question_text, text_type="SL", block_id=None)`
  - Types: `"SL"` (single line), `"ML"` (essay/multi-line), `"Form"` (form field)
- **Matrix/Likert:** `api.create_matrix_question(survey_id, question_text, statements: list, scale_points: list, block_id=None)`
- **Slider:** `api.create_slider_question(survey_id, question_text, min_value=0, max_value=100, left_label="", right_label="", block_id=None)`
- **Rank order:** `api.create_rank_order_question(survey_id, question_text, items: list, block_id=None)`
- **NPS (0-10 scale):** `api.create_nps_question(survey_id, question_text=None, left_label="Not at all likely", right_label="Extremely likely", data_export_tag=None, block_id=None)`
  - Creates a 0-10 horizontal scale with labeled endpoints (native Qualtrics NPS selector)
- **Descriptive text:** `api.create_descriptive_text(survey_id, text, block_id=None)`

### Question management
- `api.get_question(survey_id, question_id)` -> question dict
- `api.get_survey_questions(survey_id)` -> list of all questions
- `api.update_question(survey_id, question_id, question_data: dict)` -> bool
- `api.update_question_text(survey_id, question_id, new_text)` -> bool
- `api.delete_question(survey_id, question_id)` -> bool
- `api.add_page_break(survey_id, question_id)` -> bool

### Display logic
- `api.add_display_logic(survey_id, question_id, source_question_id, operator, choice_locator=None, value=None)` -> bool
- `api.add_display_logic_multiple(survey_id, question_id, conditions: list, conjunction="AND")` -> bool
- `api.show_only_if(...)` - alias for add_display_logic
- `api.skip_if(survey_id, question_id, source_question_id, operator, choice_locator=None, value=None, skip_to="EndOfBlock")` -> bool
- `api.add_embedded_data_logic(survey_id, question_id, field_name, operator, value=None)` -> bool
- `api.get_display_logic(survey_id, question_id)` -> dict or None
- `api.delete_display_logic(survey_id, question_id)` -> bool
- **Operators:** `Selected`, `NotSelected`, `Displayed`, `NotDisplayed`, `EqualTo`, `NotEqualTo`, `GreaterThan`, `LessThan`, `GreaterOrEqual`, `LessOrEqual`, `Contains`, `DoesNotContain`, `MatchesRegex`, `Empty`, `NotEmpty`
- **Choice locators** for MC: `"q://QID1/SelectableChoice/1"` (1-based index)

### Branch logic (survey flow)
- `api.add_branch_simple(survey_id, source_question_id, choice_number, block_id, operator="Selected", description=None, position=None)` -> dict
  - Convenience method: branch to a block based on a single MC choice (1-indexed)
- `api.add_branch(survey_id, conditions: list, block_ids: list, description=None, conjunction="AND", position=None)` -> dict
  - Full power: multiple conditions with AND/OR, multiple target blocks
  - Each condition dict: `{"source_question_id": "QID1", "operator": "Selected", "choice_locator": "q://QID1/SelectableChoice/1"}`
  - For embedded data conditions add `"logic_type": "EmbeddedField"` and `"value": "..."`
- `api.add_branch_embedded(survey_id, field_name, operator, value, block_ids: list, description=None, position=None)` -> dict
  - Branch on an embedded data field value
- **Key behavior:** These methods automatically remove referenced blocks from the top-level flow so they only appear inside the branch. Without this, blocks show to all respondents regardless of the condition.
- **Typical pattern:** Create blocks, add questions to them, then call `add_branch_simple()` to nest each block inside its branch.

### Graphics / Images
- `api.upload_graphic(image_source, filename=None, folder=None)` -> `{"id": "IM_...", "url": "https://..."}`
  - Uploads a local file or public URL to the Qualtrics Graphics Library
  - For GitHub images, use the raw URL: `https://raw.githubusercontent.com/user/repo/branch/path.png`
- `api.get_image_html(image_source, width=None, height=None, alt="")` -> HTML string
  - Convenience: uploads the image and returns a ready-to-use `<img>` tag
  - Embed the returned HTML in any question's `question_text` parameter

**Example:**
```python
img = api.get_image_html("https://example.com/photo.png", width=400)
api.create_descriptive_text(survey_id, f"{img}<br>Caption here")
api.create_multiple_choice_question(survey_id, f"{img}<br>What is this?", ["A", "B"])
```

### Survey header & footer
- `api.set_survey_header(survey_id, header_html, append=False)` -> bool
- `api.set_survey_footer(survey_id, footer_html, append=False)` -> bool
- Use `append=True` to add to existing header/footer instead of replacing

**Common header scripts:**
- **Wharton iframe:** `'<script src="https://cdn.research-it.wharton.upenn.edu/qualtrics-iframe-embed/0.1/qualtrics.js"></script>'`
- **Prolific bot check (always include for Prolific studies):** `'<script src="https://assets.prolific.com/assets/js/qualtrics/qualtrics.min.js?rid=${e://Field/ResponseID}&t=CpL5AGiRrd86jdAomBBbrTReQAIiZz1fpQVd3tgpBD1RuS50WMY-66AT2FYwW_fYjCh1zopVqmR-vgnPHHwzb9J3Y4ZQWZRh3WTCRJApCSKv25sJCXWcmVAp"></script>'`

### Randomizer (survey flow)
- `api.add_randomizer(survey_id, elements, subset=1, even_presentation=True, position=None)` -> dict
  - Adds a BlockRandomizer to the survey flow for random condition assignment
  - Elements can be block ID strings (e.g., `"BL_abc123"`) or dicts of embedded data field values (e.g., `{"cond": "1"}`)
  - With `even_presentation=True`, ensures equal distribution across elements
  - Block ID elements are automatically removed from top-level flow (same as branch logic)

### Embedded data
- `api.set_embedded_data(survey_id, field_name, field_type="text", value=None, position="start")` -> dict
- `api.set_embedded_data_fields(survey_id, fields: dict, position="start")` -> dict
- `api.get_embedded_data(survey_id)` -> list
- `api.delete_embedded_data(survey_id, field_name)` -> bool
- `api.get_survey_url_with_embedded_data(survey_id, embedded_data: dict)` -> URL string

## Workflow

1. **Parse the user's survey spec** into blocks, questions, logic, and embedded data.
2. **Write a single Python script** that creates the entire survey. Name it descriptively (e.g., `create_[study_name]_survey.py`).
3. **Make all questions required by default.** After creating each question (except descriptive text), call `api.update_question()` to add force response validation:
   ```python
   q = api.create_multiple_choice_question(survey_id, "...", [...])
   api.update_question(survey_id, q["QuestionID"], {
       "Validation": {"Settings": {"ForceResponse": "ON", "ForceResponseType": "ON", "Type": "None"}}
   })
   ```
   Only skip this for questions the user explicitly marks as optional.
4. **Run the script** and confirm it works.
5. **ALWAYS activate the survey** by calling `api.activate_survey(survey_id)` at the end of the script, BEFORE printing URLs. Surveys are inactive by default and their public URLs will show "this survey is not currently active" until activated. Never share a link without activating first.
6. **ALWAYS print both URLs** at the end — the user needs both:
   - **Preview URL** (for respondents/testing): `api.get_survey_url(survey_id)` → `https://{data_center}/jfe/form/{survey_id}`
   - **Edit URL** (for the researcher to review/tweak in the Qualtrics UI): `https://{data_center}/survey-builder/{survey_id}/edit`
   - When sharing links with the user in chat, always include BOTH links.
7. **Clean up**: do NOT leave the script in the project unless the user wants it. If the user wants to keep it, put it in an `examples/` or `scripts/` folder.

## Important Notes

- **All questions are required by default** unless the user says otherwise. Always add ForceResponse validation after creating each question (except descriptive text).
- Always create blocks first, then add questions to blocks. This keeps the survey organized.
- Add page breaks before questions that have display logic from a different page group.
- For display logic on MC questions, choice_locator uses 1-based indexing: first choice = `"q://QID1/SelectableChoice/1"`.
- Slider display logic uses `value=` directly (internally uses ChoiceNumericEntryValue).
- **Always activate the survey** at the end of the script with `api.activate_survey(survey_id)`. Without this, the survey URL returns an error page.
- Print the survey ID, survey URL (respondent-facing), and edit URL (`https://{data_center}/survey-builder/{survey_id}/edit`) at the end of every script.
- If the survey is for an experiment with conditions, use `add_randomizer()` to evenly assign participants. Declare embedded data fields first with `set_embedded_data()`, then use the randomizer to set their values.
- For branching: create blocks and questions first, then use `add_branch_simple()` to nest blocks inside branches. The method removes blocks from the top-level flow automatically.
- Use `try/except` around the main creation block so partial surveys can be cleaned up on error.
- **Prolific studies:** Always add the Prolific bot check header script via `api.set_survey_header()`. If the user mentions Prolific, include it automatically.
- **Use descriptive variable names in scripts.** Assign question and block return values to meaningful names (e.g., `q_pre_belief_dem`, `block_demographics`, `q_alloc_slider`) instead of reusing generic `q` or single-letter variables. This makes scripts readable and debuggable. Same applies to embedded data field names — use snake_case names that describe what the field stores (e.g., `pre_belief_dem` not `QID2_1`).
