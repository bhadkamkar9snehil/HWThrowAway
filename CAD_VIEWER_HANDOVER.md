# Handover: GitHub-Hosted Interactive CAD Viewer

This document is a reusable setup guide for any GitHub repository that needs a browser-based, interactive 3D CAD viewer.

The goal is simple:

> Commit CAD outputs to GitHub, publish a static viewer with GitHub Pages, and let anyone open supported models in a browser with orbit, pan, zoom, standard views, wireframe, measurements/metadata, and links back to the engineering files.

This pattern does **not** require a backend and does **not** require GitHub Actions.

---

## 1. Recommended architecture

Keep the editable CAD source separate from browser-viewable outputs.

```text
repo/
├─ cad/                         # editable parametric source
│  ├─ part_a.py
│  └─ assembly.py
│
├─ exports/                     # generated engineering + preview geometry
│  ├─ part_a.step               # engineering exchange / source-quality solid
│  ├─ part_a.stl                # simple browser preview / 3D printing
│  ├─ assembly.glb              # preferred browser format for assemblies
│  └─ ...
│
├─ previews/                    # optional lightweight thumbnails
│  ├─ part_a.svg
│  └─ ...
│
├─ docs/                        # GitHub Pages site
│  ├─ index.html                # interactive Three.js viewer
│  └─ models.json               # optional explicit model manifest
│
├─ README.md
└─ AGENTS.md                    # optional instructions for coding/design agents
```

### Source-of-truth rule

The browser mesh is an **output**, not the engineering source of truth.

A good priority order is:

1. Parametric/native CAD source such as CadQuery, FreeCAD, OpenSCAD, STEP-generating code, etc.
2. STEP/STP for engineering interchange.
3. GLB/GLTF or STL for browser viewing.
4. SVG/PNG for thumbnails only.

Do not edit the STL and then treat it as the master design unless that is deliberately how the project is run.

---

## 2. Which formats should be committed?

### STEP / STP

Use for engineering interchange and downstream CAD applications.

Three.js does not natively render STEP directly in the browser, so expose STEP as an **Open / Download engineering file** link rather than making it the primary browser model.

### GLB / GLTF

Preferred for interactive browser viewing when:

- the model is an assembly;
- multiple parts need different colours/materials;
- transforms and hierarchy matter;
- the viewer may later support part selection, hiding, exploded views, etc.

For new multi-part projects, **GLB is usually the best browser-delivery format**.

### STL

Good for:

- individual solid parts;
- quick prototypes;
- 3D-print-oriented geometry;
- simple static-colour previews.

STL has no assembly hierarchy, native material information, or part names.

### OBJ

Usable as a compatibility format, but GLB is generally preferable for new browser-based work.

---

## 3. Naming convention

Use the same stem for files representing the same design revision.

Example:

```text
cad/
  hopper.py

exports/
  hopper_v1.step
  hopper_v1.stl

previews/
  hopper_v1.svg
```

For a browser-first assembly:

```text
cad/
  dispenser_assembly.py

exports/
  dispenser_assembly_v3.step
  dispenser_assembly_v3.glb

previews/
  dispenser_assembly_v3.svg
```

Consistent names make automatic pairing possible.

---

## 4. Viewer technology

A lightweight viewer can be a single static HTML page using Three.js.

Useful modules:

```js
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';
import { OBJLoader } from 'three/addons/loaders/OBJLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
```

A CDN import map is sufficient for a small static site:

```html
<script type="importmap">
{
  "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.180.0/examples/jsm/"
  }
}
</script>
```

No Node.js build is required for this simple pattern.

---

## 5. Minimum interactive functionality

A general-purpose CAD viewer should provide at least:

- orbit with left drag;
- pan with right drag;
- zoom with mouse wheel / trackpad;
- Fit to model;
- isometric view;
- front view;
- right/side view;
- top view;
- wireframe toggle;
- optional auto-rotate;
- grid and axes;
- model name and repository path;
- bounding-box dimensions;
- file size;
- triangle count for mesh formats;
- link to engineering STEP/STP;
- link to editable source;
- link to GitHub;
- direct model download.

For multiple models, add:

- model list;
- search/filter;
- active-model highlighting;
- optional thumbnail;
- mobile model selector.

For assemblies, useful later additions include:

- part tree;
- show/hide parts;
- isolate part;
- part opacity;
- exploded view;
- selection highlighting;
- section/clipping planes.

---

## 6. Model discovery: two valid patterns

There are two good ways to tell the site which models exist.

### Pattern A — explicit manifest

Use `docs/models.json`.

Example:

```json
{
  "project": "Mechanical Prototype",
  "units": "mm",
  "parts": [
    {
      "id": "hopper-v1",
      "name": "Hopper V1",
      "preview": "../previews/hopper_v1.svg",
      "model": "../exports/hopper_v1.stl",
      "step": "../exports/hopper_v1.step",
      "source": "../cad/hopper.py"
    }
  ]
}
```

Advantages:

- deterministic;
- no GitHub API dependency;
- no unauthenticated API rate-limit problem;
- works well for private mirrors or alternate hosting;
- lets the project explicitly control names, ordering, transforms and metadata.

Disadvantage:

- the manifest must be updated when models are added or renamed.

### Pattern B — discover models from the GitHub repository tree

The viewer can query:

```text
https://api.github.com/repos/OWNER/REPO/git/trees/BRANCH?recursive=1
```

Then filter for:

```text
.stl
.obj
.glb
.gltf
```

and pair same-stem files such as `.step`, `.stp`, `.svg`, and source files.

Advantages:

- newly committed exports appear automatically;
- the repository is the live catalog;
- less manual bookkeeping.

Disadvantages:

- unauthenticated GitHub API calls are rate-limited;
- private repositories cannot safely expose a GitHub token in browser JavaScript;
- automatic filename matching must follow a predictable convention.

### Recommended general-purpose approach

Use a **hybrid**:

1. load `models.json` when present;
2. optionally provide a **Refresh from GitHub** function for repository discovery;
3. never put a GitHub personal access token in browser-side JavaScript.

This gives reliable normal operation while retaining automatic discovery when wanted.

---

## 7. Loading raw files from GitHub

For a public repository, a committed model can be loaded from:

```text
https://raw.githubusercontent.com/OWNER/REPO/BRANCH/exports/example.stl
```

For generated links back to GitHub use:

```text
https://github.com/OWNER/REPO/blob/BRANCH/exports/example.step
```

For cache-sensitive previews, append the blob SHA or another revision identifier rather than relying only on timestamps when possible.

Example:

```js
const url = rawModelUrl + '?sha=' + blobSha;
```

---

## 8. Units and orientation

Decide these conventions once per repository.

Recommended:

- engineering units: **millimetres**;
- Z axis: up;
- XY: ground plane;
- browser viewer assumes exported mesh coordinates already use the project unit convention.

STL itself does not formally encode units. Therefore the repository must document the convention.

If a model is unexpectedly 25.4× too large or too small, check whether one tool exported inches and another assumes millimetres.

If a model lies on its side, correct the exporter or record an explicit display transform in the manifest. Avoid silently applying arbitrary rotations per session.

---

## 9. Camera fitting

Do not hard-code the camera for one model.

After loading a model:

1. compute `THREE.Box3().setFromObject(model)`;
2. get its center;
3. get X/Y/Z extents;
4. choose camera distance from the largest extent and field of view;
5. set OrbitControls target to the model center.

This makes the same viewer work for small brackets and much larger assemblies.

---

## 10. GitHub Pages setup

The most important deployment rule is:

> Decide whether Pages serves the repository root or the `docs/` directory, then make the file layout match that choice. Do not mix the two assumptions.

### Recommended configuration: publish `main /docs`

In GitHub:

1. Open the repository.
2. Go to **Settings**.
3. Open **Pages**.
4. Under **Build and deployment**, choose **Deploy from a branch**.
5. Select branch **main**.
6. Select folder **/docs**.
7. Save.

Then:

```text
docs/index.html
```

is served as:

```text
https://OWNER.github.io/REPO/
```

This is the cleanest setup for this pattern.

### Alternative: publish `main /(root)`

If Pages is configured for the repository root, then the interactive viewer must be at:

```text
/index.html
```

or the root page must redirect to the actual viewer:

```html
<!doctype html>
<meta charset="utf-8">
<meta http-equiv="refresh" content="0; url=./docs/">
<script>location.replace('./docs/');</script>
<a href="./docs/">Open CAD viewer</a>
```

The cleaner option is still to publish `main /docs` directly.

---

## 11. Do not confuse these three URLs

For a repository named `my-cad-project`:

### Repository

```text
https://github.com/OWNER/my-cad-project
```

### Pages site

```text
https://OWNER.github.io/my-cad-project/
```

### Raw model asset

```text
https://raw.githubusercontent.com/OWNER/my-cad-project/main/exports/part.stl
```

They serve different purposes.

---

## 12. No GitHub Actions are required

For a repository where CAD exports are explicitly committed, GitHub Pages can serve the viewer directly from a branch/folder.

A custom GitHub Actions workflow is unnecessary unless the project deliberately chooses automated build/export/deployment later.

A simple workflow can remain:

```text
edit CAD source
    ↓
regenerate STEP/STL/GLB/SVG
    ↓
inspect locally
    ↓
commit source + outputs
    ↓
GitHub Pages serves the updated viewer/assets
```

---

## 13. Recommended repository instructions for agents

If ChatGPT, Codex, Claude, or another coding/design agent will work in the repository, put the contract in `AGENTS.md`.

Example:

```md
# CAD repository rules

- Keep editable CAD source in `cad/`.
- Use millimetres unless the project says otherwise.
- Treat native/parametric CAD as source of truth.
- Export STEP for engineering exchange.
- Export GLB for browser assemblies, or STL for simple parts.
- Put browser-ready exports in `exports/`.
- Put optional thumbnails in `previews/`.
- Keep browser viewer files in `docs/`.
- When geometry changes, regenerate and commit matching outputs.
- Keep `docs/models.json` current if the project uses manifest mode.
- Do not add GitHub Actions unless explicitly requested.
- Preserve stable filenames/interfaces where possible so viewer links do not break.
```

---

## 14. Adding a new model

A reusable sequence for every new part is:

### 1. Create/update CAD source

Example:

```text
cad/motor_mount.py
```

### 2. Generate engineering output

```text
exports/motor_mount_v1.step
```

### 3. Generate browser output

For a single part:

```text
exports/motor_mount_v1.stl
```

For a multi-part assembly:

```text
exports/motor_mount_assembly_v1.glb
```

### 4. Optional thumbnail

```text
previews/motor_mount_v1.svg
```

### 5. Register it

If using manifest mode, add it to `docs/models.json`.

If using GitHub-tree discovery and the naming convention is followed, no registration should be necessary.

### 6. Open the Pages site and verify

Check orbit, zoom, Fit, dimensions, engineering-file links and mobile layout.

---

## 15. Local testing

Do not double-click `index.html` and test through `file://`.

Browser security rules can behave differently for modules and loaded assets.

Use a small local web server.

Python:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/docs/
```

If serving from inside `docs/`:

```bash
cd docs
python -m http.server 8000
```

then open:

```text
http://localhost:8000/
```

---

## 16. Deployment verification checklist

Do not declare the viewer live until these checks pass.

- [ ] GitHub Pages is enabled.
- [ ] Correct branch is selected.
- [ ] Correct folder is selected: normally `/docs`.
- [ ] The Pages URL returns the interactive viewer, not README content or an old static page.
- [ ] Browser developer console has no fatal JavaScript errors.
- [ ] At least one STL/GLB actually renders.
- [ ] Orbit works.
- [ ] Pan works.
- [ ] Zoom works.
- [ ] Fit works.
- [ ] Front/right/top/isometric views work.
- [ ] Dimensions are plausible.
- [ ] STEP link opens/downloads the engineering model.
- [ ] Source link points to the editable CAD source.
- [ ] Refreshing the page still works.
- [ ] A newly added model appears through manifest/discovery as intended.
- [ ] Mobile layout is usable.
- [ ] The exact public URL has been opened and verified after deployment.

---

## 17. Common failure modes

### GitHub Pages returns 404

Cause: Pages is not enabled, the wrong branch/folder is selected, or deployment is not complete.

Check:

```text
Repository → Settings → Pages
```

For this architecture use:

```text
main /docs
```

unless the repository was intentionally designed differently.

### The site loads but shows an old static page

Usually the Pages source and the viewer location do not match.

Example failure:

- Pages serves `main /(root)`;
- new viewer was created in `docs/index.html`;
- old root page remains live.

Fix either the Pages setting or the root entry point.

### The model list appears but the model does not render

Check browser console and Network tab.

Typical causes:

- bad raw URL;
- unsupported/corrupt model;
- CORS/network failure;
- incorrect loader for the extension;
- GLTF references external resources that were not committed.

Using self-contained `.glb` avoids many GLTF asset-path issues.

### STEP will not display

Expected. STEP is not handled by the standard Three.js loaders used here.

Provide a browser mesh such as GLB or STL alongside STEP.

### STL dimensions are wrong

STL has no formal unit metadata.

Confirm the exporter and repository both use the same convention, preferably millimetres.

### The page is stale after a commit

GitHub Pages and browser/CDN caches may take a short time to update.

Use revision-aware asset URLs where practical and hard refresh while validating.

### GitHub API discovery suddenly fails

Public unauthenticated GitHub API requests are rate-limited.

Do not put a private token in client-side JavaScript.

Use `models.json` as the stable catalog or move discovery to a trusted server if high traffic eventually requires it.

---

## 18. Security and repository visibility

This static pattern is best for a **public** repository.

For a private repository:

- do not embed a personal access token in HTML/JavaScript;
- raw GitHub URLs may require authentication;
- a public Pages site should not be expected to securely proxy private CAD assets.

If the CAD must stay private, use an authenticated application or hosting layer designed for protected assets.

---

## 19. Recommended default for new repositories

For most prototyping repositories, use this baseline:

```text
Editable geometry        CadQuery / native CAD in cad/
Engineering interchange STEP in exports/
Browser part preview    STL in exports/
Browser assembly        GLB in exports/
Thumbnail               SVG in previews/
Viewer                  Three.js static site in docs/
Model catalog           docs/models.json + optional GitHub refresh
Hosting                 GitHub Pages: main /docs
Units                   millimetres
Up axis                  Z
CI/CD                    none unless explicitly required
```

---

## 20. Handover prompt for another agent

The following can be pasted into a fresh ChatGPT/Codex/agent session:

```text
Set this GitHub repository up as a general-purpose interactive CAD repository.

Requirements:
- Keep editable CAD source under cad/.
- Keep generated engineering/browser assets under exports/.
- STEP/STP is the engineering exchange format.
- Use GLB for browser assemblies and STL for simple single parts.
- Put optional generated thumbnails under previews/.
- Create a static Three.js viewer under docs/.
- Viewer must support orbit, pan, zoom, Fit, iso/front/right/top views,
  wireframe, model selection/search, dimensions, triangle count, file size,
  and links to STEP, source, GitHub and download.
- Use millimetres and Z-up unless the repository states otherwise.
- Support docs/models.json as a deterministic catalog.
- Automatic GitHub-tree discovery may be added as a refresh/fallback, but
  never expose a GitHub token in client-side code.
- The intended GitHub Pages configuration is main /docs.
- Do not add GitHub Actions unless explicitly requested.
- After implementation, verify the actual Pages URL in a browser before
  claiming that the site is live.
- Keep the setup reusable; do not hard-code it around one particular CAD part.
```

---

## 21. Final handover principle

The repository should be usable in three independent ways:

1. **Engineer:** opens the editable CAD source or STEP.
2. **Maker:** downloads STL/GLB and fabrication outputs.
3. **Reviewer:** opens one GitHub Pages URL and inspects the design interactively without installing CAD software.

If all three workflows remain valid after a new model is committed, the repository/viewer separation is working correctly.
