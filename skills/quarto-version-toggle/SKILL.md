---
name: quarto-version-toggle
description: Create a single Quarto HTML document that contains multiple pre-rendered versions of an analysis (e.g. different datasets or model specifications), switchable via client-side JavaScript buttons — no re-render needed.
---

# Quarto Multi-Version Toggle Pattern

Use this pattern when an analysis has boolean or categorical toggles (e.g. `full_data`, `pool_controls`) and you want all combinations pre-rendered into one HTML file with JS buttons to switch between them.

## Architecture

Split the document into two files:

1. **`code.qmd`** — orchestrator: YAML + CSS/JS toggle UI + a driver chunk that loops over versions and calls `knitr::knit_child`
2. **`_body.qmd`** — the entire analysis body, no YAML, no setup chunk. All toggle variables (`full_data`, `pool_controls`, etc.) are used as plain R objects — they are injected by the driver loop.

## Step 1: `_body.qmd`

Copy everything from the original `.qmd` starting after the setup chunk. Do **not** include the YAML header or the setup/library chunk.

All references to toggle variables (e.g. `if (pool_controls) ...`, `if (full_data) ...`) stay exactly as-is.

Save figures using a `fig_path` variable that is also injected by the driver:
```r
ggsave(paste0(fig_path, "my_plot.png"), ...)
```

## Step 2: `code.qmd` — YAML

```yaml
---
title: "My Analysis"
date: today
format:
  html:
    code-fold: true
    toc: false
execute:
  echo: true
  warning: false
  message: false
---
```

Set `toc: false` to avoid duplicate TOC entries from the 4 rendered copies of every heading.

## Step 3: CSS/JS Toggle UI

Add a raw HTML chunk (`{=html}`) with:
- A sticky button bar
- `.version-panel { display: none }` / `.version-panel.active { display: block }`
- JS state object mapping each axis to its current value
- A function that computes the active version string and toggles `data-version` attributes

```html
<style>
  #version-controls {
    position: sticky; top: 0; z-index: 1000;
    background: white; border-bottom: 2px solid #ddd;
    padding: 10px 16px; display: flex; flex-wrap: wrap;
    gap: 10px; align-items: center;
  }
  .ver-btn {
    padding: 5px 14px; border: 2px solid #bbb;
    border-radius: 20px; background: #f8f8f8;
    cursor: pointer; font-size: 0.88em;
  }
  .ver-btn.active { background: #2166AC; color: white; border-color: #2166AC; }
  .version-panel { display: none; }
  .version-panel.active { display: block; }
</style>

<div id="version-controls">
  <span>Data:</span>
  <button class="ver-btn" id="btn-fd-T" onclick="setToggle('fd','T',this)">Full Data</button>
  <button class="ver-btn" id="btn-fd-F" onclick="setToggle('fd','F',this)">Subset</button>
  <span>|</span>
  <span>Model:</span>
  <button class="ver-btn" id="btn-pc-F" onclick="setToggle('pc','F',this)">3-Condition</button>
  <button class="ver-btn" id="btn-pc-T" onclick="setToggle('pc','T',this)">Pooled</button>
</div>

<script>
  var _state = { fd: 'T', pc: 'T' };   // default version shown on load

  function updateDisplay() {
    var ver = _state.fd + _state.pc;    // e.g. "TT", "TF", "FT", "FF"
    document.querySelectorAll('.version-panel').forEach(function(el) {
      el.classList.toggle('active', el.dataset.version === ver);
    });
  }

  function setToggle(axis, value, btn) {
    _state[axis] = value;
    var prefix = axis === 'fd' ? 'btn-fd-' : 'btn-pc-';
    ['T','F'].forEach(function(v) {
      var b = document.getElementById(prefix + v);
      if (b) b.classList.toggle('active', v === value);
    });
    updateDisplay();
  }

  document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('btn-fd-T').classList.add('active');
    document.getElementById('btn-pc-T').classList.add('active');
    updateDisplay();
  });
</script>
```

The version ID is constructed by concatenating each axis value: `fd + pc` → `"TT"`, `"TF"`, `"FT"`, `"FF"`.

## Step 4: Setup Chunk

```r
```{r setup, echo=FALSE}
library(tidyverse); library(arrow); # ... all libraries

# Path helper: works both interactively and when rendered by Quarto
is_running_in_quarto <- function() Sys.getenv("QUARTO_DOCUMENT_PATH") != ""
base_path <- if (is_running_in_quarto()) "../my-folder/" else "./my-folder/"
tab_path  <- if (is_running_in_quarto()) "../output/tables/" else "./output/tables/"
dir.create(tab_path, recursive = TRUE, showWarnings = FALSE)

# Helper functions (shared across all versions)
numformat <- function(x, digits = 2) sprintf(paste0("%.", digits, "f"), x)
# ... etc

# Lower inline figure DPI to keep HTML file size manageable
knitr::opts_chunk$set(dpi = 150)
```
```

## Step 5: Driver Chunk

```r
```{r driver, results='asis', echo=FALSE}
versions <- list(
  TT = list(full_data = TRUE,  pool_controls = TRUE),
  TF = list(full_data = TRUE,  pool_controls = FALSE),
  FT = list(full_data = FALSE, pool_controls = TRUE),
  FF = list(full_data = FALSE, pool_controls = FALSE)
)

for (ver_id in names(versions)) {
  full_data     <- versions[[ver_id]]$full_data
  pool_controls <- versions[[ver_id]]$pool_controls

  # Load appropriate data
  data_file <- if (full_data) "analysis_data.parquet" else "analysis_data_subset.parquet"
  dat <- read_parquet(paste0(base_path, data_file))

  # Apply pool_controls toggle
  if (pool_controls) {
    dat <- dat %>% mutate(treatment = if_else(treatment == "Contact", "Contact", "Control"))
  }

  # Version-specific figure output path
  fig_path <- paste0(
    if (is_running_in_quarto()) "../output/figures/" else "./output/figures/",
    ver_id, "/"
  )
  dir.create(fig_path, recursive = TRUE, showWarnings = FALSE)

  # Open the version div
  cat(sprintf('\n<div class="version-panel" data-version="%s">\n\n', ver_id))

  # Read _body.qmd, prepend ver_id to every chunk label to avoid duplicates
  body_path <- paste0(base_path, "_body.qmd")
  body_text <- readLines(body_path, warn = FALSE)
  body_text <- gsub(
    pattern     = "^```\\{r ([^,}]+)",
    replacement = paste0("```{r ", ver_id, "-\\1"),
    x           = body_text
  )

  # Set unique fig.path prefix so inline figures don't overwrite each other
  knitr::opts_chunk$set(fig.path = paste0("code_files/figure-html/", ver_id, "-"))

  child_out <- knitr::knit_child(
    text  = paste(body_text, collapse = "\n"),
    envir = environment(),   # child sees full_data, pool_controls, fig_path, dat, helpers
    quiet = TRUE
  )
  cat(child_out)

  knitr::opts_chunk$set(fig.path = "code_files/figure-html/")
  cat('\n</div>\n\n')
}
```
```

## Key Details

**Chunk label deduplication**: `knitr` errors if the same label appears twice. The `gsub` on `body_text` prepends the version ID (e.g. `TT-my-chunk`) before each `knit_child` call, making all labels unique.

**Figure deduplication**: `knitr::opts_chunk$set(fig.path = ...)` with a version prefix ensures inline figures (e.g. `TT-my-plot-1.png`, `TF-my-plot-1.png`) don't overwrite each other. `ggsave` calls in `_body.qmd` use `fig_path` which already includes the version ID.

**Variable injection**: `envir = environment()` passes all variables from the driver loop scope into the child — `full_data`, `pool_controls`, `dat`, `fig_path`, and all helper functions defined in the setup chunk are all available in `_body.qmd` without any changes.

**File size**: With N versions × M chunks each producing plots, the HTML can get large. Mitigate with `knitr::opts_chunk$set(dpi = 150)` in setup (for inline figures) while keeping `dpi = 300` in `ggsave` calls for saved files.

**TOC**: Set `toc: false` in YAML. All 4 versions contain the same headings, so a Quarto-generated TOC would have 4× duplicate entries. Add a custom sticky nav manually in the JS/CSS block if needed.

**Version ID naming**: Use a short string encoding all toggle states, e.g. for two booleans: `TT`, `TF`, `FT`, `FF`. For a categorical toggle with 3 levels use a descriptive suffix: `full_modelA`, `full_modelB`, `subset_modelA`, etc.

## Extending to More Toggles

Add another axis to `_state` and another set of buttons. The version string just gets longer:

```js
var _state = { fd: 'T', pc: 'T', party: 'all' };
function updateDisplay() {
  var ver = _state.fd + _state.pc + '_' + _state.party;
  ...
}
```

And add corresponding entries to the `versions` list in R.
