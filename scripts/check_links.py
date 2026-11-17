"""Check local HTML links and asset references without third-party dependencies."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import sys

root = Path(sys.argv[1]).resolve()
errors = []
count = 0
class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        global count
        for key, value in attrs:
            if key not in {"href", "src"} or not value:
                continue
            url = urlsplit(value)
            if url.scheme or url.netloc or not url.path:
                continue
            count += 1
            relative = unquote(url.path)
            target = (root / relative.lstrip("/") if relative.startswith("/") else page.parent / relative).resolve()
            if not target.is_relative_to(root):
                errors.append(f"{page}: link escapes site: {value}")
            elif target.is_dir():
                if not (target / "index.html").is_file():
                    errors.append(f"{page}: missing directory index: {value}")
            elif not target.is_file():
                errors.append(f"{page}: missing {value}")
for page in root.rglob("*.html"):
    Links().feed(page.read_text(encoding="utf-8"))
if errors:
    raise SystemExit("\n".join(errors))
print(f"Checked {count} local links and assets")
