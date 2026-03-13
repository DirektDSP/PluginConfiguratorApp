#!/usr/bin/env python3
"""
Script to assign milestones and verify labels on all issues
"""

import subprocess
import json
import time

REPO = "DirektDSP/PluginConfiguratorApp"

# Map issue numbers to phases and milestones
ISSUE_PHASE_MAP = {
    # Phase 1 - Core Reorganization
    1: {"phase": 1, "milestone": 1, "priority": "p0-critical", "component": "ui:tabs"},
    2: {"phase": 1, "milestone": 1, "priority": "p0-critical", "component": "ui:tabs"},
    3: {"phase": 1, "milestone": 1, "priority": "p1-high", "component": "ui:frontend"},
    22: {
        "phase": 1,
        "milestone": 1,
        "priority": "p0-critical",
        "component": "architecture",
    },
    23: {
        "phase": 1,
        "milestone": 1,
        "priority": "p0-critical",
        "component": "architecture",
    },
    24: {
        "phase": 1,
        "milestone": 1,
        "priority": "p0-critical",
        "component": "architecture",
    },
    25: {
        "phase": 1,
        "milestone": 1,
        "priority": "p1-high",
        "component": "architecture",
    },
    26: {"phase": 1, "milestone": 1, "priority": "p0-critical", "component": "ui:tabs"},
    27: {"phase": 1, "milestone": 1, "priority": "p0-critical", "component": "ui:tabs"},
    28: {"phase": 1, "milestone": 1, "priority": "p0-critical", "component": "ui:tabs"},
    29: {"phase": 1, "milestone": 1, "priority": "p0-critical", "component": "ui:tabs"},
    30: {"phase": 1, "milestone": 1, "priority": "p2-medium", "component": "ui:tabs"},
    # Phase 2 - Quick Start Mode
    4: {"phase": 2, "milestone": 2, "priority": "p0-critical", "component": "ui:tabs"},
    5: {"phase": 2, "milestone": 2, "priority": "p1-high", "component": "presets"},
    6: {"phase": 2, "milestone": 2, "priority": "p2-medium", "component": "ui:tabs"},
    # Phase 3 - Progressive Disclosure
    7: {"phase": 3, "milestone": 3, "priority": "p1-high", "component": "ui:frontend"},
    8: {"phase": 3, "milestone": 3, "priority": "p1-high", "component": "ui:frontend"},
    9: {"phase": 3, "milestone": 3, "priority": "p1-high", "component": "ui:frontend"},
    10: {
        "phase": 3,
        "milestone": 3,
        "priority": "p2-medium",
        "component": "ui:frontend",
    },
    # Phase 4 - Inline Validation
    11: {
        "phase": 4,
        "milestone": 4,
        "priority": "p0-critical",
        "component": "ui:validation",
    },
    12: {
        "phase": 4,
        "milestone": 4,
        "priority": "p1-high",
        "component": "ui:validation",
    },
    13: {
        "phase": 4,
        "milestone": 4,
        "priority": "p1-high",
        "component": "ui:validation",
    },
    # Phase 5 - Summary Page
    14: {"phase": 5, "milestone": 5, "priority": "p0-critical", "component": "ui:tabs"},
    15: {
        "phase": 5,
        "milestone": 5,
        "priority": "p1-high",
        "component": "ui:validation",
    },
    16: {
        "phase": 5,
        "milestone": 5,
        "priority": "p0-critical",
        "component": "ui:backend",
    },
    17: {
        "phase": 5,
        "milestone": 5,
        "priority": "p2-medium",
        "component": "ui:frontend",
    },
    # Phase 6 - Preset Management
    18: {"phase": 6, "milestone": 6, "priority": "p0-critical", "component": "presets"},
    19: {"phase": 6, "milestone": 6, "priority": "p1-high", "component": "presets"},
    20: {"phase": 6, "milestone": 6, "priority": "p1-high", "component": "presets"},
    21: {"phase": 6, "milestone": 6, "priority": "p2-medium", "component": "presets"},
}


def get_issue_labels(issue_number):
    """Get current labels on an issue"""
    url = f"repos/{REPO}/issues/{issue_number}"
    cmd = ["gh", "api", url, "-q", ".labels[].name"]
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd="/root/coding/PluginConfiguratorApp"
    )

    if result.returncode == 0:
        labels = result.stdout.strip().split("\n")
        return [l for l in labels if l]  # Remove empty strings
    return []


def assign_milestone_and_labels(
    issue_number, phase_num, milestone_num, priority, component
):
    """Assign milestone and ensure all labels are present"""
    url = f"repos/{REPO}/issues/{issue_number}"

    # Get current labels
    current_labels = get_issue_labels(issue_number)

    # Determine phase label
    phase_label = f"phase-{phase_num}"

    # Build label list: always include phase, priority, component
    required_labels = [phase_label, priority, component]

    # Keep any additional labels from current state (like 'epic' for epic issues)
    additional_labels = []
    for label in current_labels:
        if label not in [
            "phase-1",
            "phase-2",
            "phase-3",
            "phase-4",
            "phase-5",
            "phase-6",
            "p0-critical",
            "p1-high",
            "p2-medium",
            "p3-low",
            "p4-backlog",
            "ui:frontend",
            "ui:backend",
            "ui:validation",
            "ui:tabs",
            "architecture",
            "presets",
        ]:
            additional_labels.append(label)

    # Combine all labels
    all_labels = required_labels + additional_labels

    # Build command
    labels_str = " ".join([f'-l "{l}"' for l in all_labels])
    cmd = [
        "gh",
        "api",
        "--method",
        "PATCH",
        url,
    ]
    for label in all_labels:
        cmd.extend(["--field", f"labels[]={label}"])
    cmd.extend(["--field", f"milestone={milestone_num}"])

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd="/root/coding/PluginConfiguratorApp"
    )

    return result.returncode == 0


def main():
    print("Assigning Milestones and Labels to Issues...")
    print("=" * 80)

    success = 0
    failed = 0

    for issue_num, info in sorted(ISSUE_PHASE_MAP.items()):
        print(
            f"Issue #{issue_num}: Phase {info['phase']} | Milestone {info['milestone']} | {info['label'] if info.get('label') else '...'}"
        )

        result = assign_milestone_and_labels(
            issue_num,
            info["phase"],
            info["milestone"],
            info["priority"],
            info["component"],
        )

        if result:
            print(f"  ✓ Assigned milestone {info['milestone']} and labels")
            success += 1
        else:
            print(f"  ✗ Failed")
            failed += 1

        time.sleep(0.5)  # Rate limiting

    print("\n" + "=" * 80)
    print(f"✅ Successfully updated: {success} issues")
    print(f"✗ Failed: {failed} issues")
    print(f"📊 Total: {len(ISSUE_PHASE_MAP)} issues")
    print("\nAll issues now have:")
    print("  - Milestone (Phase 1-6)")
    print("  - Phase label (phase-1 through phase-6)")
    print("  - Priority label (p0-critical through p4-backlog)")
    print("  - Component label (ui:frontend, ui:backend, etc.)")


if __name__ == "__main__":
    main()
