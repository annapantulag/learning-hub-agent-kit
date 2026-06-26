#!/usr/bin/env python3
"""Validate infographics folder map, state, and filesystem consistency."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "detect_infographics_folders",
    SCRIPT_DIR / "detect-infographics-folders.py",
)
detect = importlib.util.module_from_spec(spec)
spec.loader.exec_module(detect)

REPO_ROOT = detect.REPO_ROOT
MAP_FILE = detect.MAP_FILE
STATE_FILE = detect.STATE_FILE


def collect_problems() -> list[str]:
    problems: list[str] = []

    if not MAP_FILE.is_file():
        return [f"Missing map file: {MAP_FILE.relative_to(REPO_ROOT)}"]

    ignore_prefixes, folders = detect.parse_folder_map(MAP_FILE.read_text())
    state = detect.load_folder_state()

    map_keys = {f["path"] for f in folders}
    state_keys = set(state.keys())

    if map_keys != state_keys:
        only_map = sorted(map_keys - state_keys)
        only_state = sorted(state_keys - map_keys)
        if only_map:
            problems.append(f"folders in map but not state: {', '.join(only_map)}")
        if only_state:
            problems.append(f"folders in state but not map: {', '.join(only_state)}")

    if not ignore_prefixes:
        problems.append("ignore_prefixes is empty — expected at least .cursor/, .github/, gh-docs/")

    for folder in folders:
        path = folder["path"]
        label = folder.get("label", path)

        agent_doc = folder.get("agent_doc")
        if not agent_doc:
            problems.append(f"{path}: missing agent_doc")
        elif not (REPO_ROOT / agent_doc).is_file():
            problems.append(f"{path}: agent_doc not found: {agent_doc}")

        skill = folder.get("skill")
        if skill and not (REPO_ROOT / skill).is_file():
            problems.append(f"{path}: skill not found: {skill}")

        parent_hub = folder.get("parent_hub")
        if parent_hub and not (REPO_ROOT / parent_hub).is_file():
            problems.append(f"{path}: parent_hub not found: {parent_hub}")

        status = folder.get("status", "active")
        hub_status = folder.get("hub_status", "unknown")
        scope = folder.get("scope", "folder_root")
        marker = folder.get("bootstrap_marker", "learning-hub.html")

        if status == "placeholder" and hub_status not in ("not_started", "needs_bootstrap"):
            problems.append(
                f"{path}: status=placeholder but hub_status={hub_status} "
                "(expected not_started or needs_bootstrap)"
            )

        if scope == "folder_root":
            hub_path = REPO_ROOT / path / marker
            if hub_status == "complete" and not hub_path.is_file():
                problems.append(f"{path}: hub_status=complete but missing {path}/{marker}")
            if hub_status == "not_started" and hub_path.is_file():
                problems.append(f"{path}: hub_status=not_started but {path}/{marker} exists")

        st = state.get(path, {})
        if st:
            state_hub = st.get("hub_status")
            if state_hub and hub_status and state_hub != hub_status:
                problems.append(
                    f"{path}: map hub_status={hub_status} != state hub_status={state_hub}"
                )

            expected = st.get("expected_sync_mode")
            if hub_status == "complete" and expected not in ("incremental", None):
                problems.append(
                    f"{path}: hub_status=complete but expected_sync_mode={expected}"
                )
            if status == "placeholder" and expected != "skip":
                problems.append(
                    f"{path}: status=placeholder but expected_sync_mode={expected} (expected skip)"
                )

            if st.get("bootstrap_complete") is True and hub_status in ("not_started", "needs_bootstrap"):
                problems.append(
                    f"{path}: bootstrap_complete=true but hub_status={hub_status}"
                )

        if not folder.get("agent_note"):
            problems.append(f"{path}: missing agent_note (agent guidance for next sync)")

    return problems


def main() -> int:
    problems = collect_problems()
    if problems:
        print("Infographics integrity check failed:\n")
        for problem in problems:
            print(f"  ::error::{problem}")
        print(f"\n{len(problems)} issue(s). Fix map/state/files — see agentic-workflows/infographics-sync.md")
        return 1

    _, folders = detect.parse_folder_map(MAP_FILE.read_text())
    print(
        f"Infographics integrity OK — {len(folders)} mapped folder(s); "
        f"map and state aligned with filesystem."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
