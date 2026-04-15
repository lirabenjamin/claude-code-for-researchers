me: latex-workflow
description: Reproducible manuscript workflow where scripts generate numbers, tables, and figures that are read into LaTeX. Tables are split so scripts output only the tabular body; LaTeX wraps it in table environments. Iteration happens by rendering and reviewing the compiled PDF.
---

# LaTeX Reproducible Workflow

## Core Principle

Everything must be reproducible.

- Scripts generate all numbers, table bodies, and figures.
- LaTeX only assembles outputs.
- Never hardcode results inside the manuscript.

---

## Overall Pipeline

1. Run scripts to generate outputs (numbers / tables / figures).
2. LaTeX reads these outputs.
3. Render the PDF.
4. Review the PDF.
5. Iterate by editing scripts or LaTeX text (never manual edits of computed results).

---

## 1) Project Structure (Required)

Example structure:

```
project/
├── data/
│   ├── raw/
│   └── processed/
├── scripts/
│   ├── 00_clean.R
│   ├── 01_eda.R
│   └── 02_analysis.qmd
├── scripts/_helpers/
│   └── tex_numbers.R
├── output/
│   ├── figures/
│   ├── tables/
│   └── numbers/
├── paper/
│   ├── main.tex
│   ├── sections/
│   └── refs.bib
└── Makefile (optional)
```

Rules:

- Outputs go only in `output/`.
- LaTeX reads from `output/`.
- No manual insertion of computed values.

---

## 2) Numbers: Script-Generated Macros + Helper Function

### Output format

Write LaTeX macros to:

- `output/numbers/<name>.tex`

Example file content:

```
% Auto-generated. Do not edit by hand.
\newcommand{\N}{1200}
\newcommand{\MainEffect}{0.42}
\newcommand{\MainPValue}{$<.001$}
```

### Required R helper

Put this helper at:

- `scripts/_helpers/tex_numbers.R`

```r
# scripts/_helpers/tex_numbers.R

#' Write/update LaTeX \\newcommand macros in a .tex file.
#'
#' - Creates file if it doesn't exist.
#' - Updates existing macro if present.
#' - Appends macro otherwise.
#'
#' IMPORTANT:
#' - Avoid "magic numbers": compute in code, then write here.
#' - If you want to pass raw LaTeX (e.g., "$<.001$"), set force_latex=TRUE.
#'
#' @param path Path to .tex file (e.g., "output/numbers/main_numbers.tex")
#' @param name Macro name WITHOUT leading backslash (e.g., "MainEffect")
#' @param value Value to write (numeric or character)
#' @param digits Digits for numeric formatting
#' @param force_latex If TRUE, treat value as literal LaTeX (no escaping)
#' @return Invisible TRUE
write_tex_command <- function(path, name, value, digits = 3, force_latex = FALSE) {
  stopifnot(is.character(path), length(path) == 1L)
  stopifnot(is.character(name), length(name) == 1L)
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)

  # Format value
  val <- value
  if (!force_latex) {
    if (is.numeric(value) && length(value) == 1L && !is.na(value)) {
      val <- formatC(value, format = "f", digits = digits)
      val <- sub("0+$", "", val)
      val <- sub("\\.$", "", val)
    } else {
      val <- as.character(value)
    }
    # Minimal escaping for plain strings
    val <- gsub("\\\\", "\\\\textbackslash{}", val)
    val <- gsub("([%&#_])", "\\\\\\1", val, perl = TRUE)
  } else {
    val <- as.character(value)
  }

  line <- sprintf("\\\\newcommand{\\\\%s}{%s}", name, val)

  if (!file.exists(path)) {
    writeLines(c("% Auto-generated. Do not edit by hand.", line, ""), path)
    return(invisible(TRUE))
  }

  x <- readLines(path, warn = FALSE)

  # Match existing macro definition: \newcommand{\Name}{...}
  pat <- sprintf("^\\\\\\\\newcommand\\{\\\\\\\\%s\\}\\{.*\\}$", name)

  if (any(grepl(pat, x))) {
    x[grepl(pat, x)] <- line
  } else {
    if (length(x) > 0 && nzchar(tail(x, 1))) x <- c(x, "")
    x <- c(x, line, "")
  }

  writeLines(x, path)
  invisible(TRUE)
}
```

### Usage

```r
source("scripts/_helpers/tex_numbers.R")

nums_path <- file.path("output", "numbers", "main_numbers.tex")

write_tex_command(nums_path, "N", nrow(dat), digits = 0)
write_tex_command(nums_path, "MainEffect", est, digits = 2)
write_tex_command(nums_path, "MainPValue", "$<.001$", force_latex = TRUE)
```

---

## 3) Tables: Scripts Output *Only* `tabular`; LaTeX Wraps `table`

### Output format

Scripts should write ONLY the `tabular` (and optionally `booktabs` rules) to:

- `output/tables/<name>.tex`

The exported file must NOT include:

- `\begin{table}...\end{table}`
- captions, labels, notes wrappers, float placement

Example exported file (`output/tables/tab_main_results.tex`):

```
% Auto-generated. Do not edit by hand.
\begin{tabular}{lrr}
\toprule
Condition & Estimate & SE \\
\midrule
AI & 0.42 & 0.10 \\
Control & 0.12 & 0.09 \\
\bottomrule
\end{tabular}
```

### LaTeX wrapper pattern (in manuscript)

In the manuscript, LaTeX owns the float:

```tex
\begin{table}[t]
  \centering
  \caption{Main results}
  \label{tab:main}
  \input{../output/tables/tab_main_results.tex}
  % Optional notes:
  % \begin{tablenotes}
  %   \footnotesize Notes: Standard errors in parentheses.
  % \end{tablenotes}
\end{table}
```

---

## 4) Figures: Script-Generated Files

- Save figures to `output/figures/`.
- Use stable names: `fig_<topic>.pdf` (preferred) or `.png`.

LaTeX includes them:

```tex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{../output/figures/fig_main_effect.pdf}
  \caption{Main effect}
  \label{fig:main}
\end{figure}
```

---

## 5) LaTeX Responsibilities

LaTeX should ONLY:

- structure narrative
- wrap floats (`table`, `figure`)
- `\input{}` numeric macro files
- `\input{}` tabular-only table files
- include figure files

Never compute results inside LaTeX.

---

## 6) Iteration Workflow (Critical)

1. Run scripts to regenerate outputs.
2. Render LaTeX.
3. Open and inspect PDF.
4. Fix mismatches between claims and outputs.
5. Repeat.

The PDF is the review artifact.

---

## 7) Reproducibility Rules

- Absolutely NO magic numbers.
- Never type statistics manually in LaTeX.
- All results originate from scripts.
- Deleting `output/` and rerunning must reconstruct the paper.

---

## 8) Final Checks Before Submission

Confirm:

- manuscript compiles cleanly
- all tables are tabular-only inputs
- all numbers are from macro files
- all figures are script-generated
- PDF has been reviewed end-to-end
- no manual statistical values remain in `.tex` sources

---

## Guiding Rule

If results change, the paper should update automatically after re-running scripts and compiling LaTeX.

