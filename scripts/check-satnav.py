import re
import sys
from pathlib import Path

html_path = Path("index.html")
if not html_path.is_file():
    sys.exit("FAIL: index.html is missing from the repository root")

html = html_path.read_text(encoding="utf-8")
scripts = re.findall(r'<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script\s*>', html, re.I | re.S)
if not scripts:
    sys.exit("FAIL: no inline JavaScript was found")

Path("/tmp/satnav-inline.js").write_text("\n".join(scripts), encoding="utf-8")
ids = re.findall(r'\bid=["\']([^"\']+)["\']', html, re.I)
duplicates = sorted({item for item in ids if ids.count(item) > 1})
if duplicates:
    sys.exit("FAIL: duplicate HTML ids: " + ", ".join(duplicates))

js = "\n".join(scripts)
referenced = set(re.findall(r'\$\(\s*["\']([^"\']+)["\']\s*\)', js))
missing = sorted(referenced - set(ids))
if missing:
    sys.exit("FAIL: JavaScript references missing HTML ids: " + ", ".join(missing))

required_ids = ["launch", "startNav", "stopNav", "destination", "roadMap", "instruction", "speed", "speedLimit", "distance", "arrival"]
missing_required = [item for item in required_ids if item not in ids]
if missing_required:
    sys.exit("FAIL: required satnav elements missing: " + ", ".join(missing_required))

required_functions = ["startGPS", "onPosition", "calculateRoute", "updateNavigation", "checkSpeedLimit"]
missing_functions = [name for name in required_functions if not re.search(r'\bfunction\s+' + re.escape(name) + r'\s*\(', js)]
if missing_functions:
    sys.exit("FAIL: required navigation functions missing: " + ", ".join(missing_functions))

print("PASS: index.html exists")
print("PASS: no duplicate HTML ids")
print("PASS: JavaScript DOM id references resolve")
print("PASS: required satnav elements and functions exist")
