#!/usr/bin/env python3
"""
Script to create individual TASK issues and link to epics
"""

import subprocess
import time

# EPIC TO TASK MAPPING
EPIC_TASKS = {
    "https://github.com/DirektDSP/PluginConfiguratorApp/issues/1": {
        "title": "[EPIC] Create Base Tab Architecture",
        "tasks": [
            {
                "title": "[TASK] Create BaseTab abstract class",
                "description": """Create src/core/base_tab.py with base class for all tabs.

## Acceptance Criteria
- BaseTab is abstract (ABC)
- Methods: get_configuration(), load_configuration(), validate(), reset()
- Has setup_ui(), setup_connections() methods
- Proper docstrings

## Files
- Create: src/core/base_tab.py

## Complexity
- Low
- Estimation: 2 hours""",
                "priority": "p0-critical",
                "component": "architecture",
            },
            {
                "title": "[TASK] Implement ConfigurationManager singleton",
                "description": """Create src/core/config_manager.py for centralized config management.

## Acceptance Criteria
- Singleton pattern implemented
- Methods: update_config(), get_full_config(), toggle_quick_start(), validate_all()
- Thread-safe if needed
- Stores configuration from all tabs

## Files
- Create: src/core/config_manager.py

## Complexity
- Medium
- Estimation: 3 hours""",
                "priority": "p0-critical",
                "component": "architecture",
            },
            {
                "title": "[TASK] Update MainWindow to use BaseTab",
                "description": """Refactor MainWindow to use new BaseTab architecture.

## Acceptance Criteria
- All tabs inherit from BaseTab
- MainWindow calls tab methods appropriately
- No code duplication
- Cleaner import structure

## Files
- Modify: src/ui/main_window.py
- Modify: src/ui/tabs/*.py (all tabs)

## Complexity
- Medium
- Estimation: 4 hours""",
                "priority": "p0-critical",
                "component": "architecture",
            },
            {
                "title": "[TASK] Create unit tests for base classes",
                "description": """Write unit tests for BaseTab and ConfigurationManager.

## Acceptance Criteria
- >80% code coverage
- Tests for all public methods
- Edge cases covered
- Tests in tests/ directory

## Files
- Create: tests/test_base_tab.py
- Create: tests/test_config_manager.py

## Complexity
- Medium
- Estimation: 3 hours""",
                "priority": "p1-high",
                "component": "architecture",
            },
        ],
    },
    "https://github.com/DirektDSP/PluginConfiguratorApp/issues/2": {
        "title": "[EPIC] Implement 4-Lifecycle Tabs Structure",
        "tasks": [
            {
                "title": "[TASK] Create Tab 1: Define (metadata, plugin type)",
                "description": """Implement DefineTab with plugin type selection and metadata fields.

## Acceptance Criteria
- Plugin type dropdown (Audio FX, Instrument, Utility)
- Project name, product name, company name fields
- Version field
- Manufacturer code, plugin code, bundle ID (advanced)
- Auto-populates derived fields
- File tree preview updates in real-time

## Files
- Create: src/ui/tabs/define_tab.py

## Complexity
- High
- Estimation: 1 day""",
                "priority": "p0-critical",
                "component": "ui:tabs",
            },
            {
                "title": "[TASK] Create Tab 2: Configure (build options, formats)",
                "description": """Implement ConfigureTab with build settings and format selection.

## Acceptance Criteria
- Format checkboxes (Standalone, VST3, AU, AUv3, CLAP)
- Output directory with browse button
- CI/CD options (GitHub Actions)
- Code signing options
- At least one format required validation
- Format-specific disclosure

## Files
- Create: src/ui/tabs/configure_tab.py

## Complexity
- High
- Estimation: 1.5 days""",
                "priority": "p0-critical",
                "component": "ui:tabs",
            },
            {
                "title": "[TASK] Create Tab 3: Implement (templates, modules)",
                "description": """Implement ImplementTab with DSP/UI templates and module selection.

## Acceptance Criteria
- DSP template dropdown (Simple, EQ, Reverb, Full, Scratch)
- UI template dropdown (Minimal, Standard, Advanced, Scratch)
- Module checkboxes (Moonbase, Inspector, Presets)
- Accordion disclosure for modules
- Updates file tree preview

## Files
- Create: src/ui/tabs/implement_tab.py

## Complexity
- High
- Estimation: 2 days""",
                "priority": "p0-critical",
                "component": "ui:tabs",
            },
            {
                "title": "[TASK] Create Tab 4: Generate (summary, review)",
                "description": """Implement GenerateTab with summary review and generate button.

## Acceptance Criteria
- Summary sections (Metadata, Build, DSP, UI, Modules)
- Validation status indicators
- Generate button with tooltip
- Progress tracking
- Success message with actions

## Files
- Create: src/ui/tabs/generate_tab.py

## Complexity
- High
- Estimation: 1.5 days""",
                "priority": "p0-critical",
                "component": "ui:tabs",
            },
            {
                "title": "[TASK] Remove old Advanced tab and placeholder features",
                "description": """Clean up old 6-tab structure and remove placeholder content.

## Acceptance Criteria
- Advanced tab removed
- Batch generation checkbox removed
- Template library checkbox removed
- References updated
- No broken imports

## Files
- Delete: src/ui/tabs/advanced_tab.py
- Modify: src/ui/main_window.py
- Modify: src/ui/tabs/*.py

## Complexity
- Low
- Estimation: 2 hours""",
                "priority": "p2-medium",
                "component": "ui:tabs",
            },
        ],
    },
    # Add more epic task mappings...
}


# Simplified task creation for demonstration
def create_task(task, epic_url):
    """Create a task issue linked to an epic"""

    # Build body with epic reference
    body = task["description"]
    body += f"\n\n**Parent Epic:** {epic_url}"

    # Build labels
    labels = [task["priority"], task["component"]]

    cmd = [
        "gh",
        "issue",
        "create",
        "--title",
        task["title"],
        "--body",
        body,
        "--label",
        ",".join(labels),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd="/root/coding/PluginConfiguratorApp",
        )
        if result.returncode == 0:
            issue_url = result.stdout.strip()
            return issue_url
        else:
            print(f"Error creating task {task['title']}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception: {e}")
        return None


def main():
    print("Creating Task Issues...")
    print("=" * 80)

    task_count = 0

    for epic_url, epic_data in EPIC_TASKS.items():
        print(f"\n{epic_data['title']}")
        print("-" * 80)

        for task in epic_data["tasks"]:
            print(f"Creating: {task['title']}")
            task_url = create_task(task, epic_url)
            if task_url:
                print(f"  ✓ Created: {task_url}")
                task_count += 1
                time.sleep(1)  # Rate limiting
            else:
                print(f"  ✗ Failed")

    print("\n" + "=" * 80)
    print(f"Total Tasks Created: {task_count}")
    print("\nNext steps:")
    print("1. Review created tasks in GitHub")
    print("2. Link tasks to epics if needed")
    print("3. Continue adding tasks for remaining epics")


if __name__ == "__main__":
    main()
