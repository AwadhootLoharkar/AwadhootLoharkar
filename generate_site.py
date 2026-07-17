#!/usr/bin/env python3
"""
Rebuild index.html from data.yaml + templates/index.html.j2.

Usage:
    python generate_site.py
"""
import pathlib
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = pathlib.Path(__file__).parent.resolve()

def main():
    data = yaml.safe_load((ROOT / "data.yaml").read_text(encoding="utf-8"))

    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")))
    template = env.get_template("index.html.j2")

    html = template.render(**data)

    out_path = ROOT / "index.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Built {out_path}")

if __name__ == "__main__":
    main()
