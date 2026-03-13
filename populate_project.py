#!/usr/bin/env python3
"""
Script to add issues to user-level GitHub Project
"""

import subprocess
import json
import time

# Use the user-level project number (not ID)
PROJECT_NUM = 2


def list_all_issues():
    """List all repository issues"""
    cmd = ["gh", "issue", "list", "--json", "number,title,url"]

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd="/root/coding/PluginConfiguratorApp"
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    else:
        print(f"Error listing issues: {result.stderr}")
        return []


def add_issue_to_project(issue_number, issue_title):
    """Add an issue to the project using URL"""
    issue_url = (
        f"https://github.com/DirektDSP/PluginConfiguratorApp/issues/{issue_number}"
    )
    cmd = [
        "gh",
        "project",
        "item-add",
        str(PROJECT_NUM),
        "--owner",
        "@me",
        "--url",
        issue_url,
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
    print("Adding Issues to User-Level GitHub Project...")
    print(f"Project: https://github.com/users/SeamusMullan/projects/2")
    print("=" * 80)

    issues = list_all_issues()
    print(f"\nFound {len(issues)} issues in repository")

    added = 0
    for issue in issues:
        print(f"Adding: #{issue['number']} - {issue['title'][:60]}...")
        if add_issue_to_project(issue["number"], issue["title"]):
            print(f"  ✓ Added successfully")
            added += 1
            time.sleep(0.5)  # Rate limiting
        else:
            print(f"  ✗ Failed to add")

    print("\n" + "=" * 80)
    print(f"✅ Total issues added to project: {added}/{len(issues)}")
    print(f"\n📋 Project URL: https://github.com/users/SeamusMullan/projects/2")
    print(f"📊 Board URL: https://github.com/users/SeamusMullan/projects/2/views/1")


if __name__ == "__main__":
    main()
