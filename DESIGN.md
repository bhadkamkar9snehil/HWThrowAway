# Prototype Workbench Design System

## Product intent

This is an engineering workbench, not a SaaS dashboard.

The primary task is to inspect a mechanical prototype in 3D and understand what is verified, what failed, and what remains unknown. The 3D viewport must remain the visual focus.

## Visual direction

- Quiet industrial instrument.
- Flat, precise surfaces rather than floating glass cards.
- Thin structural dividers are preferred over shadows.
- Avoid decorative gradients, glows, oversized rounded cards, and nested cards.
- Use green only for selection, controls, and engineering status—not as decoration.

## Typography

- UI: IBM Plex Sans.
- IDs, paths, repo state, compact technical labels: IBM Plex Mono.
- Do not use Inter as the default.
- Do not use 8–10 px text.
- Compact application labels may use 11 px; ordinary secondary text starts at 12 px; primary content is 13 px or larger.

## Layout

Desktop:
- 54 px command bar.
- Narrow assembly tree on the left.
- 3D viewport occupies the flexible center and gets the majority of horizontal space.
- Engineering inspector on the right.
- 28 px state rail at the bottom.

Mobile:
- 3D viewport first.
- Inspector follows as a bottom region.
- Hide the persistent assembly tree and use a component selector instead.

## Surfaces

- Main background: cool technical neutral.
- Side panels: solid light surface.
- Radius: 5–6 px for controls; avoid large soft cards.
- No persistent drop shadows.
- Use 1 px structural separators.

## Interaction

- Orbit/pan/zoom must remain immediately available in the viewport.
- Camera presets: Iso, Front, Right, Top.
- Fit, Wire, X-ray, Rotate are persistent utilities.
- Active toggles use the accent tint and aria-pressed.
- Keyboard focus must remain visibly outlined.
- Respect prefers-reduced-motion.

## Evidence presentation

- PASS / FAIL / UNKNOWN is evidence, not decoration.
- Show measurements as plain aligned rows.
- Requirements are flat list items separated by rules.
- Assumptions and risks must never be hidden by an overall PASS.
- Do not invent simulation states. If no solver result exists, say so directly.

## Anti-patterns to avoid

- Dashboard card grids.
- Cards inside panels inside cards.
- Tiny metadata everywhere.
- Excessive status pills.
- Marketing copy.
- Gratuitous animation.
- Decorative 3D chrome competing with the actual model.
