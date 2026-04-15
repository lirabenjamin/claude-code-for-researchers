# Diagrams

TikZ-authored figures for the Google Slides deck. Nine diagrams, one `.tex` source, rendered to `diagrams.pdf` (nine pages) and one PNG per diagram.

## Why TikZ instead of Google Slides shapes

Positioning shapes via the Slides API is fragile — fonts don't scale cleanly with coordinates, arrow endpoints drift, and anything touching text alignment requires careful batch sequencing. TikZ renders the diagrams once, locally, with pixel-perfect control, and you drop PNGs into the slides by hand.

## Files

- `diagrams.tex` — source. Edit here.
- `diagrams.pdf` — 9-page multipage PDF. Each page is one diagram, tightly cropped.
- `<name>.png` — per-diagram raster (200 dpi), one per slide placeholder.

## Diagram-to-slide mapping

| Slide | PNG | Content |
|---|---|---|
| 5  | `memory.png`         | Claude + 4 markdown files |
| 15 | `joke_flow.png`      | 6-step joke-task flow |
| 17 | `commit_hash.png`    | Materials + Data → git SHA |
| 18 | `webapp_arch.png`    | React → Express → MongoDB |
| 20 | `qmd_cascade.png`    | QMD cascade (raw → rendered) |
| 24 | `no_magic.png`       | Code ↔ manuscript link |
| 26 | `gdocs_trap.png`     | Broken link after Google Docs export |
| 27 | `overleaf_flow.png`  | LaTeX + Overleaf collab loop |
| 31 | `provenance.png`     | Prolific → Mongo → git SHA |

## Rebuild

```bash
# From a directory OUTSIDE OneDrive (OneDrive intercepts LaTeX's intermediate files):
cp diagrams.tex /tmp/build/
cd /tmp/build
pdflatex -interaction=nonstopmode diagrams.tex
pdftoppm -png -r 200 diagrams.pdf page
# Rename page-N.png to match the diagram-to-slide table above.
```

## Workflow in the demo

The Google Slides deck has yellow placeholder boxes on each diagram slide with a one-line description of what the diagram shows. To drop the real diagram in:

1. Open the slide in Google Slides
2. Delete the yellow placeholder box
3. Insert → Image → Upload from computer → pick the matching PNG
4. Resize to fit; center

No scripting needed for the image insert step — it's a manual drop. The placeholders make each slide self-documenting so you know which PNG goes where.
