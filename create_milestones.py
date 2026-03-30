#!/usr/bin/env python3
"""
Script to create milestones and assign issues to phases
"""

import subprocess
import json
import time

REPO = "DirektDSP/PluginConfiguratorApp"


def create_milestone(title, description, due_date):
    """Create a milestone via GitHub API"""
    url = f"https://api.github.com/repos/{REPO}/milestones"

    data = {
        "title": title,
        "description": description,
        "state": "open",
        "due_on": due_date,
    }

    cmd = [
        "gh",
        "api",
        "--method",
        "POST",
        url,
        "-f",
        f"title={title}",
        "-f",
        f"description={description}",
        "-f",
        f"due_on={due_date}",
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd="/root/coding/PluginConfiguratorApp"
    )
    if result.returncode == 0:
        milestone = json.loads(result.stdout)
        print(f"✓ Created milestone: {title}")
        return milestone["number"]
    else:
        print(f"✗ Error creating milestone {title}: {result.stderr}")
        return None


def create_all_milestones():
    """Create all 6 phase milestones"""
    milestones = [
        {
            "title": "Phase 1: Core Reorganization",
            "description": "Base Tab Architecture, 4-Lifecycle Tabs, File Tree Preview",
            "due_date": "2026-03-22T00:00:00Z",
        },
        {
            "title": "Phase 2: Quick Start Mode",
            "description": "Quick Start Toggle, Example Presets, Review & Generate Shortcut",
            "due_date": "2026-03-26T00:00:00Z",
        },
        {
            "title": "Phase 3: Progressive Disclosure",
            "description": "Plugin Type, Format-Specific, Module Accordion, Template Descriptions",
            "due_date": "2026-04-05T00:00:00Z",
        },
        {
            "title": "Phase 4: Inline Validation",
            "description": "Field-Level, Tab-Level, and Global Validation systems",
            "due_date": "2026-04-12T00:00:00Z",
        },
        {
            "title": "Phase 5: Summary Page",
            "description": "Summary Page Structure, Validation Status, Generate, Success Message",
            "due_date": "2026-04-25T00:00:00Z",
        },
        {
            "title": "Phase 6: Preset Management",
            "description": "XML Preset Schema, Save, Load, and Preset Management Dialog",
            "due_date": "2026-05-07T00:00:00Z",
        },
    ]

    print("Creating Milestones...")
    print("=" * 80)

    milestone_map = {}
    for milestone in milestones:
        milestone_number = create_milestone(
            milestone["title"], milestone["description"], milestone["due_date"]
        )
        if milestone_number:
            milestone_map[milestone["title"]] = milestone_number
        time.sleep(0.5)

    print("\n" + "=" * 80)
    print(f"Created {len(milestone_map)} milestones")

    return milestone_map


def main():
    create_all_milestones()
    print("\nMilestones created successfully!")
    print(
        "\nNext: Run assign_milestones.py to assign issues to their respective phases."
    )


if __name__ == "__main__":
    main()
