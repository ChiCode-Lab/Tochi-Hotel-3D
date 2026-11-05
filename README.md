# Tochi Hotel 3D

Interactive 3D concept model of the proposed Tochi Hotel, a single-storey hotel with 13 en-suite guest rooms, a lounge/bar, a kitchen, a reception and a central courtyard. It's built with three.js.

**Live model:** https://chicode-lab.github.io/Tochi-Hotel-3D/ (once GitHub Pages is enabled)

## What's in the model
- Black stone-coated hip roof over a stepped white cornice parapet (top cap projects 550 mm)
- Charcoal brick and sage accent panels, burglar-proofed windows, louvred fanlights
- Open courtyard with a paved walkway to reception
- Front yard with 6 parking bays and parked cars
- Block fence with brick piers, a steel sliding gate, and a security post with generator room

Use the view buttons (Aerial, Front yard, Courtyard, Rear, Plan view) or drag to orbit. Turn the roof off to see the room layout and furniture.

## Files
| Path | What it is |
|---|---|
| `index.html` | The 3D model. It's one self-contained file with three.js bundled in, so it also works offline when opened in a phone or desktop browser. |
| `drawings/` | Ground floor plan and site layout, drawing TH-A-101 Rev P2 (PDF and PNG, A1). |
| `source/plan.py` | Generates the 2D drawing (SVG → PDF/PNG). |
| `source/export3d.py` | Exports the plan geometry to `model.json` for the 3D model. |
| `source/model_template.html` | The three.js scene. `__DATA__` is replaced with `model.json`, and three.js loads from unpkg. |

## Key dimensions
- Building 41.5 m × 17.4 m; plot about 61.5 m × 20.4 m (narrowing to about 18.4 m at the rear)
- Setbacks: front 10 m, rear 10 m, sides 1.5 m
- Guest rooms 5000 × 4000 mm clear, each with a 1800 × 2100 mm en-suite
- North corridor 1500 mm; south and rear corridors 1200 mm; courtyard 5500 mm wide

Drawn by Engr. Chinemenum Paul Ogbonda. Concept and client-review status only; not for construction.
