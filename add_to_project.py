#!/usr/bin/env python3
"""
Script to add issues to GitHub Project and item links
"""

import subprocess
import json

PROJECT_ID = "PVT_kwDOB5FKGc4BRppg"


def list_issues():
    """List all repository issues"""
    cmd = ["gh", "issue", "list", "--json", "number,title,url,labels"]

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd="/root/coding/PluginConfiguratorApp"
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(f"Error listing issues: {result.stderr}")
        return []


def add_issue_to_project(issue_number):
    """Add an issue to the project"""
    cmd = [
        "gh",
        "project",
        "item-add",
        PROJECT_ID,
        "--owner",
        "DirektDSP",
        "--content-id",
        f"{issue_number}",
        "--content-type",
        "Issue",
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd="/root/coding/PluginConfiguratorApp"
    )
    if result.returncode == 0:
        return True
    else:
        print(f"  Error adding issue {issue_number}: {result.stderr}")
        return False


def main():
    print("Adding Issues to GitHub Project...")
    print("=" * 80)

    issues = list_issues()
    print(f"\nFound {len(issues)} issues")

    added = 0
    for issue in issues:
        print(f"Adding: #{issue['number']} - {issue['title'][:60]}")
        if add_issue_to_project(issue["number"]):
            print(f"  ✓ Added")
            added += 1

    print("\n" + "=" * 80)
    print(f"Total issues added to project: {added}/{len(issues)}")


if __name__ == "__main__":
    main()
