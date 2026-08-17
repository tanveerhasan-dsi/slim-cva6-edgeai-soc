# docs/figures/

Diagram sources. Keep the source here, not only the export.

Prefer Mermaid in fenced ```mermaid blocks inside the documents themselves —
GitHub renders it, and it stays diffable. Use this directory for diagrams too
large to inline, or for exports needed by a paper.

Commit the source alongside any exported image. A PNG whose source has been lost
cannot be corrected when the design changes, and on this project the block
diagram will change.

Figures likely to be needed:

- SoC block diagram: always-on domain, compute domain, CV-X-IF attachment,
  memory, power domains
- The ISA-coverage-versus-PPA curve (R-2.22) — the project's primary figure
- Sensor-to-PWM latency budget allocation (R-2.14)
- Trap-and-emulate control flow, for the compatibility contract
