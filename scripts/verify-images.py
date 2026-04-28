#!/usr/bin/env python3
"""Verify all container images referenced under infra/services."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

IMAGE_PATTERN = re.compile(r'^(?P<indent>\s*)image:\s*(?P<image>\S+)\s*$', re.MULTILINE)
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_SERVICES_DIR = REPO_ROOT / "infra" / "services"


@dataclass
class ImageCheck:
    file: pathlib.Path
    original: str
    resolved: str
    status: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate service image references and optionally swap missing tags for alpine variants."
    )
    parser.add_argument(
        "--services-dir",
        type=pathlib.Path,
        default=DEFAULT_SERVICES_DIR,
        help="Directory to scan for service manifests.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite manifests when an alpine fallback tag is available.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print docker pull output for every request.",
    )
    return parser.parse_args()


def split_image_reference(ref: str) -> Tuple[str, Optional[str]]:
    if "@" in ref:
        reference = ref.split("@", 1)[0]
        return reference, None

    last_slash = ref.rfind("/")
    last_colon = ref.rfind(":")

    if last_colon > last_slash:
        repo = ref[:last_colon]
        tag = ref[last_colon + 1 :]
        return repo, tag

    return ref, None


def pull_image(image: str, cache: Dict[str, bool], verbose: bool) -> bool:
    if image in cache:
        return cache[image]

    cmd = ["docker", "pull", image]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    success = result.returncode == 0
    cache[image] = success

    if verbose or not success:
        status = "pulled" if success else "failed to pull"
        print(f"{status} {image}")
        output = result.stdout.strip()
        if output:
            for line in output.splitlines():
                print(f"  {line}")

    return success


def collect_service_files(root: pathlib.Path) -> List[pathlib.Path]:
    if not root.exists():
        raise SystemExit(f"Services directory {root} does not exist")
    return sorted(root.resolve().rglob("*.yaml"))


def find_images(content: str) -> Iterable[re.Match[str]]:
    return IMAGE_PATTERN.finditer(content)


def apply_replacements(file_path: pathlib.Path, replacements: Dict[str, str]) -> bool:
    if not replacements:
        return False

    content = file_path.read_text()

    def replacer(match: re.Match[str]) -> str:
        image = match.group("image")
        indent = match.group("indent")
        replacement = replacements.get(image)
        if replacement:
            return f"{indent}image: {replacement}"
        return match.group(0)

    updated = IMAGE_PATTERN.sub(replacer, content)
    if updated == content:
        return False

    file_path.write_text(updated)
    return True


def main() -> None:
    args = parse_args()
    pull_cache: Dict[str, bool] = {}
    summary: List[ImageCheck] = []
    replacements: Dict[pathlib.Path, Dict[str, str]] = {}

    for manifest in collect_service_files(args.services_dir):
        content = manifest.read_text()
        for match in find_images(content):
            image = match.group("image")
            if pull_image(image, pull_cache, args.verbose):
                summary.append(
                    ImageCheck(
                        file=manifest,
                        original=image,
                        resolved=image,
                        status="available",
                        detail="image downloads cleanly",
                    )
                )
                continue

            repo, _ = split_image_reference(image)
            fallback = f"{repo}:alpine"
            if fallback != image and pull_image(fallback, pull_cache, args.verbose):
                summary.append(
                    ImageCheck(
                        file=manifest,
                        original=image,
                        resolved=fallback,
                        status="patched",
                        detail="swapped to alpine fallback",
                    )
                )
                replacements.setdefault(manifest, {})[image] = fallback
            else:
                summary.append(
                    ImageCheck(
                        file=manifest,
                        original=image,
                        resolved=image,
                        status="missing",
                        detail="tag unavailable",
                    )
                )

    if args.apply:
        touched = 0
        for manifest, pending in replacements.items():
            if apply_replacements(manifest, pending):
                touched += 1
        print(f"updated {touched} manifest(s)")
    else:
        if replacements:
            print("alpine fallbacks available; rerun with --apply to persist them")

    print("summary")
    counts: Dict[str, int] = {}
    for record in summary:
        counts[record.status] = counts.get(record.status, 0) + 1
    for status in ("available", "patched", "missing"):
        if status in counts:
            print(f"  {status}: {counts[status]}")
    for record in summary:
        rel = record.file.relative_to(REPO_ROOT)
        if record.status == "patched":
            print(f"- {rel}: {record.original} -> {record.resolved} ({record.detail})")
        else:
            print(f"- {rel}: {record.original} ({record.detail})")


if __name__ == "__main__":
    main()
