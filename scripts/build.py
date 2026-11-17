"""Build the static site and include the library's public technical documents."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]

def build(library: Path, output: Path):
    if output.exists():
        raise SystemExit(f"Output already exists: {output}; choose a fresh directory")
    shutil.copytree(ROOT / "site", output)
    # Keep documentation URLs working while their source stays with the software.
    for source in (library / "docs").rglob("*"):
        if source.is_file() and source.suffix in {".md", ".json", ".bib"} and "assets" not in source.relative_to(library / "docs").parts:
            target = output / source.relative_to(library / "docs")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    (output / ".nojekyll").touch()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    if not (args.library / "docs" / "NEURON_COMPLETION.md").is_file():
        raise SystemExit("--library must point to a synaptic-lens checkout")
    build(args.library, args.output)
