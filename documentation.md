# awadhootloharkar.github.io

Personal portfolio site. Static HTML/CSS output, generated from a data file
and a Jinja2 template, with a local Flask admin GUI for editing content
without touching code.

## Structure
```
data.yaml                 All site content (single source of truth)
templates/index.html.j2   Page template — rendered into index.html
generate_site.py          Rebuild script: data.yaml + template -> index.html
index.html                Generated output (this is what GitHub Pages serves)
css/style.css             Styling
assets/                   Photo, résumé PDF
admin/                    Local Flask GUI for editing data.yaml
environment.yml           Mamba/conda environment spec
```

## 1. Set up the environment (mamba)

From the repo root, in WSL:

```bash
# Install mamba if you don't have it yet (via miniforge)
# https://github.com/conda-forge/miniforge -> download & run the installer, then restart your shell

# Create the environment from the spec in this repo
mamba env create -f environment.yml

# Activate it
mamba activate portfolio
```

If you ever add a library, add it to `environment.yml` (or `requirements.txt`
for pip-only packages) and re-run `mamba env update -f environment.yml`.

To tear down and start fresh: `mamba env remove -n portfolio`.

## 2. Rebuild the static site from data.yaml

```bash
python generate_site.py
```

This reads `data.yaml`, renders `templates/index.html.j2`, and overwrites
`index.html`. Run this any time you hand-edit `data.yaml` directly.

## 3. Edit content through the GUI instead

```bash
cd admin
python app.py
```

Open http://127.0.0.1:5050 in your browser. From the dashboard you can edit:

- **Profile & photo** — name, tagline, links, and upload a new headshot
  (auto-cropped to a square).
- **About**
- **Experience**, **Research**, **Publications**, **Education**, **Skills**
  — add, edit, or remove entries.
- **Contact**

Every save writes straight to `data.yaml` and regenerates `index.html`
automatically. The GUI never touches git — review what changed, then commit
and push yourself:

```bash
git status
git add .
git commit -m "Update portfolio content"
git push
```

The admin app is local-only (`127.0.0.1`) — it's a personal editing tool, not
something to deploy alongside the site.

## Local preview of the site itself

```bash
python3 -m http.server 8000
```
then visit http://localhost:8000

## Deploy

Push to a GitHub repo named `<username>.github.io`, enable Pages on the
`main` branch, root folder. See the deployment walkthrough shared alongside
this project for the full first-time setup.
