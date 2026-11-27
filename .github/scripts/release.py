"""Package a Forever addon and optionally publish a versioned GitHub release."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import zipfile


def version_tuple(value):
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", value)
    if not match:
        raise ValueError(f"Expected a three-part version, got {value!r}")
    return tuple(map(int, match.groups()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    toc_files = list(root.glob("*.toc"))
    if len(toc_files) != 1:
        raise ValueError("Expected exactly one addon TOC at the repository root")
    toc = toc_files[0]
    addon = toc.stem
    source_toc = toc.read_text(encoding="utf-8-sig")
    match = re.search(r"^## Version:\s*(\S+)", source_toc, re.MULTILINE)
    if not match:
        raise ValueError("Missing TOC version")
    version = version_tuple(match[1])

    if args.publish:
        repository = os.environ["GITHUB_REPOSITORY"]
        pages = subprocess.check_output([
            "gh", "api", f"repos/{repository}/releases?per_page=100",
            "--paginate", "--slurp",
        ], text=True)
        published = []
        for page in json.loads(pages):
            for release in page:
                if release["draft"] or release["prerelease"]:
                    continue
                tag = release["tag_name"]
                if re.fullmatch(r"v\d+\.\d+\.\d+", tag):
                    published.append(version_tuple(tag))
        if published and max(published) >= version:
            major, minor, patch = max(published)
            version = (major, minor, patch + 1)

    version_text = ".".join(map(str, version))
    packaged_toc = re.sub(
        r"^## Version:[^\r\n]*", f"## Version: {version_text}",
        source_toc, count=1, flags=re.MULTILINE,
    )
    addon_files = sorted([*root.glob("*.lua"), *root.glob("*.toc")])
    if (root / "README.txt").is_file():
        addon_files.append(root / "README.txt")
    filenames = {path.name for path in addon_files}
    for line in source_toc.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and line not in filenames:
            raise ValueError(f"TOC references a missing packaged file: {line}")

    dist = root / "dist"
    dist.mkdir(exist_ok=True)
    archive = dist / f"{addon}-v{version_text}-forever.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as output:
        for path in addon_files:
            data = packaged_toc.encode("utf-8") if path == toc else path.read_bytes()
            output.writestr(f"{addon}/{path.name}", data)
    with zipfile.ZipFile(archive) as output:
        if output.testzip() is not None:
            raise ValueError("ZIP integrity check failed")
        assert f"## Version: {version_text}" in output.read(f"{addon}/{toc.name}").decode()
    print(f"Packaged {archive.name}", flush=True)

    if args.publish:
        notes = (
            f"WoW Forever release of {addon}, version {version_text}.\n\n"
            "Install using this repository URL in WowUp's Install from URL dialog. "
            "For a manual installation, download the attached -forever.zip and "
            f"copy the {addon} folder into Interface/AddOns.\n\n"
            f"Source commit: {os.environ['GITHUB_SHA']}\n"
        )
        notes_path = dist / "release-notes.md"
        notes_path.write_text(notes)
        subprocess.run([
            "gh", "release", "create", f"v{version_text}", str(archive),
            "--repo", repository, "--target", os.environ["GITHUB_SHA"],
            "--title", f"{addon} v{version_text}",
            "--notes-file", str(notes_path), "--latest",
        ], check=True)


if __name__ == "__main__":
    main()
