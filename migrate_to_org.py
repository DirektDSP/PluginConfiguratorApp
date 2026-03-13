#!/usr/bin/env python3
"""
Script to add issues to Organizational GitHub Project
"""

import subprocess
import json
import time

# Use the organizational project number
PROJECT_NUM = 1


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
        "DirektDSP",
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
    print("Adding Issues to Organizational GitHub Project...")
    print(f"Project: https://github.com/orgs/DirektDSP/projects/1")
    print("=" * 80)

    issues = list_all_issues()
    print(f"\nFound {len(issues)} issues in repository")

    added = 0
    already_exists = 0
    for issue in issues:
        print(f"Adding: #{issue['number']} - {issue['title'][:60]}...")
        if add_issue_to_project(issue["number"], issue["title"]):
            print(f"  ✓ Added successfully")
            added += 1
            time.sleep(0.5)  # Rate limiting
        else:
            print(f"  ⊘ Already exists or failed")
            already_exists += 1

    print("\n" + "=" * 80)
    print(f"✅ Successfully added: {added}")
    print(f"⊘ Already existed: {already_exists}")
    print(f"📊 Total: {len(issues)} issues")
    print(f"\n📋 Project URL: https://github.com/orgs/DirektDSP/projects/1")
    print(f"📊 Board URL: https://github.com/orgs/DirektDSP/projects/1/views/1")


if __name__ == "__main__":
    main()
