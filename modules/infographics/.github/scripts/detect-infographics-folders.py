#!/usr/bin/env python3
"""Detect mapped main folders affected by git changes for infographics sync."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MAP_FILE = REPO_ROOT / "agentic-workflows" / "infographics-folder-map.yaml"
STATE_FILE = REPO_ROOT / "agentic-workflows" / "infographics-folder-state.yaml"
TOPIC_SEGMENT_RE = re.compile(r"(?:mod|skill|sec)-.+")


def run_git(*args: str) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def collect_changed_paths() -> list[str]:
    paths: set[str] = set()
    for args in (
        ("diff", "--name-only"),
        ("diff", "--cached", "--name-only"),
    ):
        paths.update(run_git(*args))
    paths.update(run_git("ls-files", "--others", "--exclude-standard"))
    return sorted(paths)


def parse_scalar_value(value: str) -> str | int | bool | None:
    if value in ("null", "~", ""):
        return None
    if value.isdigit():
        return int(value)
    if value in ("true", "false"):
        return value == "true"
    return value


def parse_folder_map(text: str) -> tuple[list[str], list[dict]]:
    ignore_prefixes: list[str] = []
    folders: list[dict] = []
    section: str | None = None
    current: dict | None = None
    fold_key: str | None = None

    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if fold_key and current is not None and line.startswith("      "):
            current[fold_key] = ((current.get(fold_key) or "") + " " + line.strip()).strip()
            continue
        fold_key = None

        if re.match(r"^ignore_prefixes:\s*$", line):
            section = "ignore"
            continue
        if re.match(r"^folders:\s*$", line):
            section = "folders"
            continue

        if section == "ignore":
            m = re.match(r"^\s+-\s+(.+)$", line)
            if m:
                ignore_prefixes.append(m.group(1).strip())
            continue

        if section == "folders":
            if re.match(r"^\s+-\s+path:\s*", line):
                if current:
                    folders.append(current)
                current = {"path": line.split("path:", 1)[1].strip()}
                continue
            if current is not None:
                m_fold = re.match(r"^\s+(\w+):\s*>-\s*$", line)
                if m_fold:
                    fold_key = m_fold.group(1)
                    current[fold_key] = ""
                    continue
                m = re.match(r"^\s+(\w+):\s*(.+)$", line)
                if m:
                    key, value = m.group(1), m.group(2).strip()
                    if key != "path":
                        current[key] = parse_scalar_value(value)

    if current:
        folders.append(current)
    return ignore_prefixes, folders


def load_folder_state() -> dict[str, dict]:
    if not STATE_FILE.is_file():
        return {}
    state: dict[str, dict] = {}
    section: str | None = None
    current_key: str | None = None
    current: dict | None = None
    fold_key: str | None = None

    for raw in STATE_FILE.read_text().splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        if fold_key and current is not None and line.startswith("      "):
            current[fold_key] = ((current.get(fold_key) or "") + " " + line.strip()).strip()
            continue
        fold_key = None

        if re.match(r"^folders:\s*$", line):
            section = "folders"
            continue
        if section != "folders":
            continue

        m_key = re.match(r"^  ([^:\s]+):\s*$", line)
        if m_key:
            if current_key and current is not None:
                state[current_key] = current
            current_key = m_key.group(1)
            current = {}
            continue
        if current is not None:
            m_fold = re.match(r"^    (\w+):\s*>-\s*$", line)
            if m_fold:
                fold_key = m_fold.group(1)
                current[fold_key] = ""
                continue
            m_field = re.match(r"^    (\w+):\s*(.*)$", line)
            if m_field:
                key, value = m_field.group(1), m_field.group(2).strip()
                current[key] = parse_scalar_value(value)

    if current_key and current is not None:
        state[current_key] = current
    return state


def build_folder_registry(folders: list[dict], state: dict[str, dict]) -> list[dict]:
    registry: list[dict] = []
    for folder in folders:
        fp = folder["path"]
        entry = {
            "path": fp,
            "label": folder.get("label", fp),
            "status": folder.get("status", "active"),
            "hub_status": folder.get("hub_status", "unknown"),
            "scope": folder.get("scope", "folder_root"),
            "agent_doc": folder.get("agent_doc", ""),
            "agent_note": folder.get("agent_note", ""),
        }
        if folder.get("skill"):
            entry["skill"] = folder["skill"]
        st = state.get(fp, {})
        if st:
            entry["state"] = {
                k: st[k]
                for k in (
                    "expected_sync_mode",
                    "bootstrap_complete",
                    "diagram_count",
                    "last_sync_commit",
                    "agent_note",
                )
                if k in st
            }
            if st.get("agent_note") and not entry.get("agent_note"):
                entry["agent_note"] = st["agent_note"]
        registry.append(entry)
    return registry


def is_under_prefix(path: str, prefix: str) -> bool:
    return path == prefix or path.startswith(prefix.rstrip("/") + "/")


def matched_folder(path: str, folders: list[dict]) -> dict | None:
    best: dict | None = None
    best_len = -1
    for folder in folders:
        fp = folder["path"]
        if is_under_prefix(path, fp) and len(fp) > best_len:
            best = folder
            best_len = len(fp)
    return best


def is_ignored(path: str, ignore_prefixes: list[str]) -> bool:
    return any(is_under_prefix(path, prefix) for prefix in ignore_prefixes)


def extract_topic_subfolder(folder_path: str, file_path: str) -> str | None:
    """Return the deepest topic-like directory (mod-*/skill-*/sec-*) for a file.

    Picks the most specific segment so a container like ``skill-google-program``
    never shadows the real topic folder ``mod-04-elt`` nested inside it.
    """
    if not is_under_prefix(file_path, folder_path):
        return None
    rel = file_path[len(folder_path) :].lstrip("/")
    segments = rel.split("/")
    topic_depth: int | None = None
    for i, seg in enumerate(segments[:-1]):  # exclude the filename itself
        if TOPIC_SEGMENT_RE.fullmatch(seg):
            topic_depth = i
    if topic_depth is None:
        return None
    return folder_path + "/" + "/".join(segments[: topic_depth + 1])


def candidate_roots(path: str) -> list[str]:
    # Loose files at the repo root are not folders to map.
    if "/" not in path:
        return []
    parts = path.split("/")
    if parts[0].startswith("."):
        return []
    # Treat udemy/<course> as the mappable root, but only when a course
    # subdirectory actually contains the file (avoid mapping a loose udemy/ file).
    if parts[0] == "udemy":
        if len(parts) >= 3:
            return [f"udemy/{parts[1]}"]
        return []
    return [parts[0]]


def marker_exists(folder: dict, topic: str | None = None) -> bool:
    marker = folder.get("bootstrap_marker", "learning-hub.html")
    if folder.get("scope") == "topic_subfolders" and topic:
        return (REPO_ROOT / topic / marker).is_file()
    base = REPO_ROOT / folder["path"] / marker
    return base.is_file()


def main() -> int:
    if not MAP_FILE.is_file():
        print(json.dumps({"error": f"Missing map file: {MAP_FILE}"}), file=sys.stderr)
        return 1

    ignore_prefixes, folders = parse_folder_map(MAP_FILE.read_text())
    state = load_folder_state()
    folder_registry = build_folder_registry(folders, state)
    changed = collect_changed_paths()

    folder_hits: dict[str, set[str]] = {}
    folder_topics: dict[str, set[str]] = {}
    ignored_only = True
    placeholder_touched: dict[str, set[str]] = {}

    for path in changed:
        if is_ignored(path, ignore_prefixes):
            continue
        ignored_only = False
        folder = matched_folder(path, folders)
        if folder:
            fp = folder["path"]
            folder_hits.setdefault(fp, set()).add(path)
            if folder.get("scope") == "topic_subfolders":
                topic = extract_topic_subfolder(fp, path)
                if topic:
                    folder_topics.setdefault(fp, set()).add(topic)
            continue

    mapped_paths = {f["path"] for f in folders}
    candidate_files: dict[str, set[str]] = {}
    for path in changed:
        if is_ignored(path, ignore_prefixes):
            continue
        if matched_folder(path, folders):
            continue
        for root in candidate_roots(path):
            if root in mapped_paths:
                continue
            if is_ignored(root + "/", ignore_prefixes):
                continue
            candidate_files.setdefault(root, set()).add(path)

    affected: list[dict] = []
    for folder in folders:
        fp = folder["path"]
        hits = folder_hits.get(fp)
        if not hits:
            continue

        status = folder.get("status", "active")
        if status == "placeholder":
            placeholder_touched[fp] = hits
            continue

        scope = folder.get("scope", "folder_root")
        topics = sorted(folder_topics.get(fp, []))
        subpaths = sorted(hits)

        if scope == "topic_subfolders":
            if topics:
                # Bootstrap if any touched topic subfolder lacks its own hub.
                needs_bootstrap = any(
                    not marker_exists(folder, topic) for topic in topics
                )
            else:
                # Folder-level change (e.g. docs/, README) with no topic touched:
                # bootstrap only if the aggregate parent hub is missing.
                parent = folder.get("parent_hub")
                if parent:
                    needs_bootstrap = not (REPO_ROOT / parent).is_file()
                else:
                    needs_bootstrap = not marker_exists(folder)
        else:
            needs_bootstrap = not marker_exists(folder)

        entry = {
            "path": fp,
            "label": folder.get("label", fp),
            "mode": "bootstrap" if needs_bootstrap else "incremental",
            "status": status,
            "hub_status": folder.get("hub_status", "unknown"),
            "scope": scope,
            "agent_doc": folder.get("agent_doc", ""),
            "subpaths": subpaths,
        }
        if folder.get("agent_note"):
            entry["agent_note"] = folder["agent_note"]
        st = state.get(fp, {})
        if st.get("expected_sync_mode"):
            entry["expected_sync_mode"] = st["expected_sync_mode"]
        if folder.get("skill"):
            entry["skill"] = folder["skill"]
        if folder.get("parent_hub"):
            entry["parent_hub"] = folder["parent_hub"]
        if topics:
            entry["topic_subfolders"] = topics

        affected.append(entry)

    candidates = [
        {"path": root, "changed_files": sorted(files)}
        for root, files in sorted(candidate_files.items())
    ]

    skip_sync = len(affected) == 0 and len(candidates) == 0

    output = {
        "skip_sync": skip_sync,
        "ignored_only": ignored_only and len(changed) > 0,
        "changed_count": len(changed),
        "folder_registry": folder_registry,
        "affected": affected,
        "candidates": candidates,
        "placeholder_touched": [
            {"path": fp, "subpaths": sorted(paths), "hub_status": "not_started"}
            for fp, paths in sorted(placeholder_touched.items())
        ],
    }

    json.dump(output, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
