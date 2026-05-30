# Assets Directory

## Purpose

This directory stores images, diagrams, and other visual assets for documentation.

## Contents

### Conceptual Images
- Architecture diagrams
- Block diagrams  
- Data flow illustrations

### Generated Images (after GDS build)
- Layout screenshots from KLayout
- GDS renders (PNG/SVG)
- Utilization heatmaps

## Important Distinction

### Concept Images
Concept images are hand-drawn or tool-generated illustrations that show the intended architecture. They are NOT:
- Actual silicon layout
- OpenLane/OpenROAD output
- Verified GDS renders

Always label concept images clearly.

### Actual GDS Renders
After successful GDS generation, renders from KLayout or similar tools showing the actual layout. These should be:
- Clearly labeled with generation date
- Linked to specific workflow run
- Verified against reports

## Naming Convention

```
concept_architecture.png     - Conceptual diagram
concept_tensortile_flow.png  - Conceptual diagram
gds_layout_YYYYMMDD.png      - Actual GDS render
klayout_zoom_YYYYMMDD.png    - KLayout screenshot
```

## Adding Images

1. Keep file sizes reasonable (<1MB preferred)
2. Use PNG for diagrams, SVG for scalable graphics
3. Include in documentation with relative paths
4. Add alt text for accessibility

## Current Assets

```
(No assets uploaded yet)
```

Add actual files and update this list as the project progresses.
