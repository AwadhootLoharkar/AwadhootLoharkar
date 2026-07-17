#!/usr/bin/env python3
"""
Local admin GUI for editing the portfolio site content.

Run:
    cd admin
    python app.py
Then open http://127.0.0.1:5050

Every save writes to ../data.yaml and regenerates ../index.html.
Nothing is pushed to GitHub automatically — review the diff, then
`git add . && git commit -m "update" && git push` yourself.
"""
import pathlib
import shutil
import sys

import yaml
from flask import Flask, render_template, request, redirect, url_for, flash
from PIL import Image

ROOT = pathlib.Path(__file__).parent.parent.resolve()
DATA_PATH = ROOT / "data.yaml"
ASSETS_DIR = ROOT / "assets"
PHOTO_PATH = ASSETS_DIR / "photo.jpg"

sys.path.insert(0, str(ROOT))
import generate_site  # noqa: E402

app = Flask(__name__)
app.secret_key = "portfolio-admin-local-only"  # local tool, not exposed to the internet

# Describes every list-type section: which fields it has, in what order,
# and a human label. Add a new section here and it gets a full CRUD UI for free.
LIST_SECTIONS = {
    "experience": {
        "label": "Experience",
        "fields": ["title", "org", "date", "description"],
    },
    "research": {
        "label": "Research",
        "fields": ["title", "subtitle", "date", "description", "link", "link_label"],
    },
    "publications": {
        "label": "Publications",
        "fields": ["title", "venue", "date", "description", "link", "link_label"],
    },
    "education": {
        "label": "Education",
        "fields": ["degree", "org", "date", "description"],
    },
    "skills": {
        "label": "Skills",
        "fields": ["group", "items"],
    },
}


def load_data():
    return yaml.safe_load(DATA_PATH.read_text(encoding="utf-8"))


def save_data(data):
    DATA_PATH.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000),
        encoding="utf-8",
    )
    generate_site.main()


@app.route("/")
def dashboard():
    data = load_data()
    return render_template("dashboard.html", data=data, sections=LIST_SECTIONS)


@app.route("/profile", methods=["GET", "POST"])
def edit_profile():
    data = load_data()
    if request.method == "POST":
        for key in ["name", "location", "tagline", "email", "github", "linkedin"]:
            data["profile"][key] = request.form.get(key, "").strip()

        photo_file = request.files.get("photo")
        if photo_file and photo_file.filename:
            ASSETS_DIR.mkdir(exist_ok=True)
            img = Image.open(photo_file.stream).convert("RGB")
            # Center-crop to a square, then resize — keeps the hero photo consistent
            # no matter what aspect ratio the uploaded picture is.
            w, h = img.size
            side = min(w, h)
            left, top = (w - side) // 2, (h - side) // 2
            img = img.crop((left, top, left + side, top + side)).resize((640, 640))
            img.save(PHOTO_PATH, "JPEG", quality=90)
            data["profile"]["photo"] = "assets/photo.jpg"

        save_data(data)
        flash("Profile updated and site rebuilt.")
        return redirect(url_for("edit_profile"))

    return render_template("profile.html", profile=data["profile"])


@app.route("/about", methods=["GET", "POST"])
def edit_about():
    data = load_data()
    if request.method == "POST":
        raw = request.form.get("paragraphs", "")
        paragraphs = [p.strip() for p in raw.split("\n\n") if p.strip()]
        data["about"]["paragraphs"] = paragraphs
        save_data(data)
        flash("About section updated and site rebuilt.")
        return redirect(url_for("edit_about"))

    joined = "\n\n".join(data["about"]["paragraphs"])
    return render_template("about.html", paragraphs=joined)


@app.route("/contact", methods=["GET", "POST"])
def edit_contact():
    data = load_data()
    if request.method == "POST":
        data["contact"]["blurb"] = request.form.get("blurb", "").strip()
        save_data(data)
        flash("Contact section updated and site rebuilt.")
        return redirect(url_for("edit_contact"))

    return render_template("contact.html", blurb=data["contact"]["blurb"])


@app.route("/section/<name>", methods=["GET", "POST"])
def edit_section(name):
    if name not in LIST_SECTIONS:
        return "Unknown section", 404

    schema = LIST_SECTIONS[name]
    data = load_data()

    if request.method == "POST":
        items = []
        # Rows are posted as row-<index>-<field>. We walk indices until one
        # is missing, skipping any row whose "remove" checkbox was ticked.
        i = 0
        while f"row-{i}-{schema['fields'][0]}" in request.form:
            if request.form.get(f"row-{i}-remove") != "on":
                item = {
                    field: request.form.get(f"row-{i}-{field}", "").strip()
                    for field in schema["fields"]
                }
                items.append(item)
            i += 1

        data[name] = items
        save_data(data)
        flash(f"{schema['label']} updated and site rebuilt.")
        return redirect(url_for("edit_section", name=name))

    return render_template(
        "section.html",
        name=name,
        label=schema["label"],
        fields=schema["fields"],
        items=data.get(name, []),
    )


@app.route("/section/<name>/add", methods=["POST"])
def add_item(name):
    if name not in LIST_SECTIONS:
        return "Unknown section", 404
    schema = LIST_SECTIONS[name]
    data = load_data()
    blank = {field: "" for field in schema["fields"]}
    data.setdefault(name, []).append(blank)
    save_data(data)
    return redirect(url_for("edit_section", name=name))


@app.route("/rebuild", methods=["POST"])
def rebuild():
    generate_site.main()
    flash("Site rebuilt from data.yaml.")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    ASSETS_DIR.mkdir(exist_ok=True)
    app.run(debug=True, port=5050)
