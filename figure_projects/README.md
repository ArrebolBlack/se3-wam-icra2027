# Editable figure projects

Each manuscript figure is maintained as an independent, one-slide PowerPoint
project. The PPTX canvas matches the figure's native aspect ratio, and the text,
boxes, and arrows remain editable in PowerPoint.

| Paper figure | Editable project | Paper asset |
|---|---|---|
| Execution-time teaser | `teaser_timeline/teaser_timeline.pptx` | `figures/teaser_timeline.svg` / `.pdf` |
| SE(3)-WAM architecture | `architecture/architecture.pptx` | `figures/architecture.svg` / `.pdf` |
| DB0 benchmark suite | `benchmark_suite/benchmark_suite.pptx` | `figures/benchmark_suite.svg` / `.pdf` |

The manuscript continues to use the PDF exports for deterministic LaTeX layout.
The PPTX files are independent authoring projects and can evolve separately;
accepted changes should then be synchronized back to the corresponding SVG.

All three decks were rendered and visually inspected after export, and each
passes the presentation overflow test.
