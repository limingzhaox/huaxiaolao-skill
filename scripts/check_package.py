"""Check portable local Markdown links and attributed evidence integrity."""
import argparse
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys
from urllib.parse import unquote


def check(root):
    root = Path(root).resolve()
    errors, links = [], 0
    for path in root.rglob("*.md"):
        if ".git" in path.relative_to(root).parts:
            continue
        body = path.read_text(encoding="utf-8-sig")
        for raw in re.findall(r"!?\[[^\]]*\]\(([^\n)]+)\)", body):
            raw = raw.strip().strip("<>")
            if raw.startswith(("https://", "http://", "mailto:", "#")):
                continue
            destination = unquote(raw.split("#", 1)[0])
            target = (path.parent / destination).resolve()
            links += 1
            if Path(destination).is_absolute() or PureWindowsPath(destination).is_absolute() or root not in target.parents or not target.exists():
                errors.append(f"{path.relative_to(root)}: broken/nonportable link {raw}")
    evidence = root / "references/evidence"
    manifest = json.loads((evidence / "manifest.json").read_text(encoding="utf-8"))
    entries = manifest["packaged_evidence"]
    indexed = set()
    for entry in entries:
        path = (evidence / entry["path"]).resolve()
        indexed.add(path)
        if evidence not in path.parents or not path.is_file():
            errors.append(f"missing/escaped evidence: {entry['path']}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            errors.append(f"evidence hash mismatch: {entry['path']}")
        if not entry.get("source_url") or not entry.get("scope"):
            errors.append(f"evidence attribution missing: {entry['path']}")
    images = {p.resolve() for p in evidence.iterdir() if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}}
    for path in images - indexed:
        errors.append(f"unattributed evidence: {path.name}")
    return {"pass": not errors, "markdown_local_links_checked": links, "evidence_files_checked": len(entries), "errors": errors, "limits": "Does not validate scientific truth, image meaning, author permissions or artistic acceptance."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = check(args.root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        result = {"pass": False, "errors": [str(exc)]}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["pass"] else 1)
