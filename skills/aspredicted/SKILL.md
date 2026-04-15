---
name: aspredicted
description: Write an AsPredicted pre-registration for a study. Walk through each field with the user, then produce a complete pre-registration document.
---

# AsPredicted Pre-Registration

When this skill is triggered, walk the user through writing an AsPredicted pre-registration. Go field by field, drafting each section based on what you know about the study from context. Present a draft for each field and let the user revise before moving on. At the end, compile the full pre-registration into a clean document.

## Template Fields

### 1) Data Collection
Have any data been collected for this study already?

- No, no data have been collected for this study yet.
- It's complicated (explain in Question 8).

### 2) Hypothesis
What is the main question being asked or hypothesis being tested in this study?

### 3) Dependent Variables
Describe the key dependent variable(s), specifying how they will be measured.

### 4) Conditions
How many and which conditions will participants be assigned to?

### 5) Analyses
Specify exactly which analyses you will conduct to examine the main question/hypothesis.

### 6) Outliers and Exclusions
Describe exactly how outliers will be defined and handled, and your precise rule(s) for excluding observations.

### 7) Sample Size
How many observations will be collected or what will determine sample size?

### 8) Other
Anything else you would like to pre-register?

### 9) Name
Give a title for this AsPredicted pre-registration.

### 10) Type of Study
- Experiment
- Survey
- Observational / archival study
- Other

### 11) Data Source
- Prolific
- MTurk
- CloudResearch
- University lab
- Other

## Output

After all fields are finalized, compile into a single clean markdown document saved to the project directory as `aspredicted_<short-name>.md`. Use concise, precise scientific language. Avoid hedging or filler.
