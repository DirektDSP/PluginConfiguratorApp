#!/usr/bin/env python3
"""
Script to create GitHub Issues for UI Revamp Project with Epics and Tasks
"""

import json
import subprocess
import time

# Phase 1: Core Reorganization
PHASE_1_EPICS = [
    {
        "title": "[EPIC] Create Base Tab Architecture",
        "phase": "phase-1",
        "priority": "p0-critical",
        "component": "architecture",
        "description": """Implement BaseTab base class and core architecture to eliminate code duplication across all tabs.

## Objectives
- Create BaseTab abstract class with common methods
- Establish ConfigurationManager singleton
- Set up proper inheritance pattern for all tabs
- Define configuration data flow

## Linked Tasks
- [ ] Create BaseTab abstract class in src/core/base_tab.py
- [ ] Implement ConfigurationManager singleton in src/core/config_manager.py
- [ ] Update MainWindow to use new architecture
- [ ] Create unit tests for base classes

## Success Criteria
- All existing tabs updated to inherit from BaseTab
- ConfigurationManager properly manages state across tabs
- Unit tests pass with >80% coverage
- Code duplication reduced by >40%

## Timeline
- Start: 2026-03-14
- End: 2026-03-16
- Duration: 3 days""",
    },
    {
        "title": "[EPIC] Implement 4-Lifecycle Tabs Structure",
        "phase": "phase-1",
        "priority": "p0-critical",
        "component": "ui:tabs",
        "description": """Create the new 4-tab structure: Define, Configure, Implement, Generate.

## Objectives
- Replace existing 6 tabs with 4 lifecycle-based tabs
- Implement proper tab navigation and validation flow
- Add Previous/Next buttons with validation checks
- Enable direct tab switching via tab bar

## Linked Tasks
- [ ] Create Tab 1: Define (metadata, plugin type)
- [ ] Create Tab 2: Configure (build options, formats)
- [ ] Create Tab 3: Implement (DSP/UI templates, modules)
- [ ] Create Tab 4: Generate (summary, review)
- [ ] Remove old Advanced tab
- [ ] Remove unused placeholder features

## Success Criteria
- 4 tabs fully functional with all content
- Navigation works correctly with validation
- Old tabs and placeholder features removed
- User can complete full flow from Define to Generate

## Timeline
- Start: 2026-03-16
- End: 2026-03-20
- Duration: 5 days

## Dependencies
- Depends on: [EPIC] Create Base Tab Architecture""",
    },
    {
        "title": "[EPIC] Setup Real-Time File Tree Preview",
        "phase": "phase-1",
        "priority": "p1-high",
        "component": "ui:frontend",
        "description": """Implement persistent file tree preview panel visible on all tabs.

## Objectives
- Create FileTreePreview component
- Implement real-time updates on configuration changes
- Add file size/count metrics
- Show template/module additions dynamically

## Linked Tasks
- [ ] Create FileTreePreview widget in src/ui/components/
- [ ] Integrate preview panel into all 4 tabs
- [ ] Implement update triggers for all configuration changes
- [ ] Add visual indicators for enabled/disabled features
- [ ] Implement debouncing for smooth updates

## Success Criteria
- File tree updates in real-time across all tabs
- Shows accurate file structure and counts
- No performance issues with frequent updates
- Clear visual feedback for what's included

## Timeline
- Start: 2026-03-18
- End: 2026-03-22
- Duration: 5 days""",
    },
]

# Phase 2: Quick Start Mode
PHASE_2_EPICS = [
    {
        "title": "[EPIC] Implement Quick Start Toggle",
        "phase": "phase-2",
        "priority": "p0-critical",
        "component": "ui:tabs",
        "description": """Add Quick Start toggle on Tab 1 with wizard-like behavior.

## Objectives
- Add Quick Start toggle switch on Tab 1
- Implement prefilled defaults when enabled
- Simplify UI when Quick Start is ON
- Maintain state when switching modes

## Linked Tasks
- [ ] Add Quick Start toggle component to Tab 1
- [ ] Implement QuickStartDefaults manager
- [ ] Create quick_start_defaults.json
- [ ] Apply defaults when Quick Start enabled
- [ ] Implement mode switching with state preservation

## Success Criteria
- Quick Start toggle works seamlessly
- Defaults applied correctly when enabled
- User selections preserved when switching modes
- UI simplifies appropriately in Quick Start mode

## Timeline
- Start: 2026-03-21
- End: 2026-03-25
- Duration: 5 days""",
    },
    {
        "title": "[EPIC] Create Example Preset Files",
        "phase": "phase-2",
        "priority": "p1-high",
        "component": "presets",
        "description": """Create 3 hardcoded example presets that ship with the application.

## Objectives
- Create StandardAudioFX_Preset.xml
- Create Instrument_Preset.xml
- Create MinimalPlugin_Preset.xml
- Define preset XML schema

## Linked Tasks
- [ ] Design XML schema for presets
- [ ] Create Standard Audio FX preset
- [ ] Create Instrument preset
- [ ] Create Minimal Plugin preset
- [ ] Add preset validation utilities

## Success Criteria
- 3 example presets created and valid
- Presets load correctly in application
- XML schema documented
- Users can use examples immediately

## Timeline
- Start: 2026-03-23
- End: 2026-03-25
- Duration: 3 days""",
    },
    {
        "title": "[EPIC] Implement Review & Generate Shortcut",
        "phase": "phase-2",
        "priority": "p2-medium",
        "component": "ui:tabs",
        "description": """Add "Review & Generate" button on Tab 1 when Quick Start is enabled.

## Objectives
- Add button to jump directly to Tab 4
- Auto-fill Tab 4 with intelligent defaults
- Validate required fields before navigation
- Provide visual feedback on button state

## Linked Tasks
- [ ] Add "Review & Generate" button to Tab 1
- [ ] Implement navigation logic with validation
- [ ] Auto-populate Tab 4 with defaults
- [ ] Add button state management (disabled/enabled)

## Success Criteria
- Button navigates to Tab 4 when clicked
- Only works when required fields are valid
- Tab 4 shows prefilled summary
- Clear visual feedback on validation

## Timeline
- Start: 2026-03-24
- End: 2026-03-26
- Duration: 3 days""",
    },
]

# Phase 3: Progressive Disclosure
PHASE_3_EPICS = [
    {
        "title": "[EPIC] Implement Plugin Type Progressive Disclosure",
        "phase": "phase-3",
        "priority": "p1-high",
        "component": "ui:frontend",
        "description": """Show/hide options based on plugin type selection (Instrument vs FX).

## Objectives
- Show Instrument-specific options when selected
- Show FX-specific options when selected
- Implement smooth animations for disclosure
- Update file tree preview based on type

## Linked Tasks
- [ ] Implement instrument options (polyphony, MIDI)
- [ ] Implement FX options (wet/dry, sidechain, latency)
- [ ] Add disclosure animation components
- [ ] Integrate with file tree preview

## Success Criteria
- Options appear/disappear smoothly
- Correct options shown for each type
- File tree preview updates correctly
- No visual glitches or layout issues

## Timeline
- Start: 2026-03-26
- End: 2026-03-30
- Duration: 5 days

## Can parallelize with: Phase 1 tasks""",
    },
    {
        "title": "[EPIC] Implement Format-Specific Disclosure",
        "phase": "phase-3",
        "priority": "p1-high",
        "component": "ui:frontend",
        "description": """Show/hide format-specific options (AU, CLAP, AUv3).

## Objectives
- Show AU-specific options (AudioComponentDescription, versioning)
- Show CLAP options (extensions, features)
- Show AUv3 options (iOS/macOS platform)
- Implement disclosure for each format

## Linked Tasks
- [ ] Add AU-specific options group
- [ ] Add CLAP-specific options group
- [ ] Add AUv3-specific options group
- [ ] Implement disclosure logic
- [ ] Update file tree preview

## Success Criteria
- Format options shown when format selected
- All format-specific options functional
- File tree shows correct build files
- Works with multiple formats selected

## Timeline
- Start: 2026-03-28
- End: 2026-04-02
- Duration: 6 days

## Can parallelize with: Plugin Type disclosure""",
    },
    {
        "title": "[EPIC] Implement Module Accordion Disclosure",
        "phase": "phase-3",
        "priority": "p1-high",
        "component": "ui:frontend",
        "description": """Add accordion-style expanders for modules (Moonbase, Presets, etc).

## Objectives
- Create AccordionExpander component
- Implement module-specific revealed options
- Add smooth expand/collapse animations
- Support nested accordions

## Linked Tasks
- [ ] Create AccordionExpander widget
- [ ] Implement Moonbase accordion (license type, grace period)
- [ ] Implement Preset Management accordion (format, storage)
- [ ] Add animation system for expanders
- [ ] Update ConfigurationManager for expanded state

## Success Criteria
- Accordions expand/collapse smoothly
- Module options show correctly when enabled
- Animations perform well (>60fps)
- State persisted across tab switches

## Timeline
- Start: 2026-03-30
- End: 2026-04-05
- Duration: 7 days""",
    },
    {
        "title": "[EPIC] Add DSP/UI Template Description System",
        "phase": "phase-3",
        "priority": "p2-medium",
        "component": "ui:frontend",
        "description": """Add descriptions to DSP/UI template selections to show what's included.

## Objectives
- Show brief description for each template
- List included components/features
- Update description dynamically on selection
- Style descriptions nicely

## Linked Tasks
- [ ] Create template description data structure
- [ ] Add description panel to template dropdowns
- [ ] Show component lists for each template
- [ ] Style descriptions with icons/checkmarks

## Success Criteria
- Descriptions show for all templates
- Content is accurate and helpful
- Updates instantly on selection
- Clear visual hierarchy

## Timeline
- Start: 2026-04-01
- End: 2026-04-03
- Duration: 3 days""",
    },
]

# Phase 4: Inline Validation
PHASE_4_EPICS = [
    {
        "title": "[EPIC] Implement Field-Level Validation",
        "phase": "phase-4",
        "priority": "p0-critical",
        "component": "ui:validation",
        "description": """Add real-time validation for individual form fields.

## Objectives
- Validate field values on input/change
- Show visual feedback (green check, red X)
- Display inline error messages
- Implement validation rules

## Linked Tasks
- [ ] Create field validation utilities
- [ ] Implement project name validator
- [ ] Implement bundle ID validator
- [ ] Implement code validators (manufacturer, plugin)
- [ ] Implement output directory validator
- [ ] Add visual feedback components
- [ ] Add inline error message widgets

## Success Criteria
- All fields validated in real-time
- Clear green/red feedback
- Error messages specific and helpful
- No false positives/negatives

## Timeline
- Start: 2026-04-03
- End: 2026-04-08
- Duration: 6 days""",
    },
    {
        "title": "[EPIC] Implement Tab-Level Validation",
        "phase": "phase-4",
        "priority": "p1-high",
        "component": "ui:validation",
        "description": """Add validation status for each tab with required field counters.

## Objectives
- Show validation status in tab footer
- Count required fields remaining
- Jump to invalid fields on click
- Update status as user completes fields

## Linked Tasks
- [ ] Add validation status footer to all tabs
- [ ] Count required fields for each tab
- [ ] Implement "click to fix issues" functionality
- [ ] Update status dynamically
- [ ] Add visual indicators (Ready vs Errors)

## Success Criteria
- Tab footer shows accurate status
- Field counts update in real-time
- Users can quickly find and fix issues
- Status transitions smooth

## Timeline
- Start: 2026-04-06
- End: 2026-04-10
- Duration: 5 days""",
    },
    {
        "title": "[EPIC] Implement Global Validation Status",
        "phase": "phase-4",
        "priority": "p1-high",
        "component": "ui:validation",
        "description": """Add global validation status in status bar and generate button.

## Objectives
- Show overall validation status in status bar
- Display validation summary across all tabs
- Enable/disable Generate button based on validation
- Add tooltip with all issues on Generate button

## Linked Tasks
- [ ] Add global validation to status bar
- [ ] Aggregate validation from all tabs
- [ ] Disable Generate button when invalid
- [ ] Add tooltip listing all issues
- [ ] Update status bar dynamically

## Success Criteria
- Status bar shows accurate overall status
- Generate button disabled appropriately
- Tooltips show helpful issue lists
- Updates smoothly in real-time

## Timeline
- Start: 2026-04-09
- End: 2026-04-12
- Duration: 4 days""",
    },
]

# Phase 5: Summary Page
PHASE_5_EPICS = [
    {
        "title": "[EPIC] Create Summary Page Structure",
        "phase": "phase-5",
        "priority": "p0-critical",
        "component": "ui:tabs",
        "description": """Build the Tab 4 (Generate) summary page with all sections.

## Objectives
- Create summary layout sections (Metadata, Build, DSP, UI, Modules)
- Implement data binding from other tabs
- Add visual design element

## Linked Tasks
- [ ] Create SummaryTab widget
- [ ] Implement Metadata summary section
- [ ] Implement Build Configuration summary
- [ ] Implement DSP Template summary
- [ ] Implement UI Template summary
- [ ] Implement Modules summary with expansion

## Success Criteria
- All sections show correct data from tabs
- Layout is clean and scannable
- Data updates in real-time
- Visual hierarchy is clear

## Timeline
- Start: 2026-04-11
- End: 2026-04-16
- Duration: 6 days""",
    },
    {
        "title": "[EPIC] Add Validation Status to Summary",
        "phase": "phase-5",
        "priority": "p1-high",
        "component": "ui:validation",
        "description": """Show validation status for each section on summary page.

## Objectitives
- Add green/red checkmarks to each section
- Show section-specific error messages
- Implement overall status display
- Add visual focus on invalid sections

## Linked Tasks
- [ ] Add validation indicators to each section
- [ ] Show section error messages
- [ ] Implement overall valid/invalid status
- [ ] Add highlighting for invalid sections
- [ ] Scroll to first invalid section

## Success Criteria
- All sections show validation status
- Errors visible and actionable
- Overall status accurate
- Smooth navigation to issues

## Timeline
- Start: 2026-04-15
- End: 2026-04-18
- Duration: 4 days""",
    },
    {
        "title": "[EPIC] Implement Generate Functionality",
        "phase": "phase-5",
        "priority": "p0-critical",
        "component": "ui:backend",
        "description": """Implement the actual project generation process.

## Objectives
- Clone template repository
- Apply configuration to files
- Generate project files
- Initialize Git repository
- Show progress tracking

## Linked Tasks
- [ ] Update ProjectWorker for new config structure
- [ ] Implement template cloning
- [ ] Implement CMakeLists.txt generation
- [ ] Implement README.md generation
- [ ] Implement file generation from templates
- [ ] Implement Git initialization
- [ ] Add progress bar

## Success Criteria
- Projects generate successfully
- All configuration applied correctly
- Progress tracking works
- Git repository initialized properly

## Timeline
- Start: 2026-04-17
- End: 2026-04-24
- Duration: 8 days""",
    },
    {
        "title": "[EPIC] Add Success Message & Actions",
        "phase": "phase-5",
        "priority": "p2-medium",
        "component": "ui:frontend",
        "description": """Show success message with post-generation actions.

## Objectives
- Display success message
- Show project location
- Add "Open in IDE" action
- Add "Open in Finder" action
- Add "Close" action

## Linked Tasks
- [ ] Create success message dialog
- [ ] Implement "Open in IDE" (VSCode, Xcode, CLion)
- [ ] Implement "Open in Finder" path opening
- [ ] Add styling for success state
- [ ] Add celebration animation

## Success Criteria
- Success message shows correctly
- Actions work across OSes (macOS, Linux, Windows)
- Icons and styling look good
- User can easily navigate to project

## Timeline
- Start: 2026-04-23
- End: 2026-04-25
- Duration: 3 days""",
    },
]

# Phase 6: Preset Management
PHASE_6_EPICS = [
    {
        "title": "[EPIC] Define XML Preset Schema",
        "phase": "phase-6",
        "priority": "p0-critical",
        "component": "presets",
        "description": """Define and implement the XML schema for presets.

## Objectives
- Design comprehensive XML schema
- Create XML validation utilities
- Document schema structure
- Add schema versioning

## Linked Tasks
- [ ] Design XML schema structure
- [ ] Create XSD or DTD for validation
- [ ] Implement XML parser and validator
- [ ] Add schema documentation
- [ ] Create example preset files

## Success Criteria
- Schema supports all configuration options
- Validation catches malformed presets
- Documentation is clear
- Preset files follow schema

## Timeline
- Start: 2026-04-24
- End: 2026-04-28
- Duration: 5 days""",
    },
    {
        "title": "[EPIC] Implement Preset Save Functionality",
        "phase": "phase-6",
        "priority": "p1-high",
        "component": "presets",
        "description": """Add ability to save current configuration as a preset.

## Objectives
- Add "Save as Preset" button
- Implement preset name dialog
- Save configuration to XML
- Store in user预设 directory

## Linked Tasks
- [ ] Add "Save as Preset" to File menu
- [ ] Create preset name input dialog
- [ ] Implement XML serialization
- [ ] Create ~/.plugin_configurator/presets/ directory
- [ ] Add error handling

## Success Criteria
- Presets save correctly to XML
- All settings included in saved file
- Directory created if doesn't exist
- Error handling works

## Timeline
- Start: 2026-04-27
- End: 2026-04-30
- Duration: 4 days""",
    },
    {
        "title": "[EPIC] Implement Preset Load Functionality",
        "phase": "phase-6",
        "priority": "p1-high",
        "component": "presets",
        "description": """Add ability to load presets from file system.

## Objectives
- Add "Load Preset" button
- Show dialog with available presets
- Load configuration from XML
- Apply configuration to all tabs

## Linked Tasks
- [ ] Add "Load Preset" to Tab 1 (Define)
- [ ] Create preset selection dialog
- [ ] Implement XML deserialization
- [ ] Apply configuration to tabs
- [ ] Validate loaded configuration

## Success Criteria
- Dialog shows available presets
- Presets load correctly
- All tabs update with loaded config
- Validation catches invalid presets

## Timeline
- Start: 2026-04-29
- End: 2026-05-04
- Duration: 6 days""",
    },
    {
        "title": "[EPIC] Add Preset Management Dialog",
        "phase": "phase-6",
        "priority": "p2-medium",
        "component": "presets",
        "description": """Create preset management interface for deleting/exporting/importing.

## Objectives
- Show all presets with metadata
- Add delete functionality
- Add export to file
- Add import from file

## Linked Tasks
- [ ] Create preset management dialog
- [ ] Implement delete preset functionality
- [ ] Implement export to file
- [ ] Implement import from file
- [ ] Add preset metadata display

## Success Criteria
- All user presets shown
- Delete removes file and updates UI
- Export creates downloadable file
- Import validates and loads preset

## Timeline
- Start: 2026-05-03
- End: 2026-05-07
- Duration: 5 days""",
    },
]

# ALL EPICS
ALL_EPICS = (
    PHASE_1_EPICS
    + PHASE_2_EPICS
    + PHASE_3_EPICS
    + PHASE_4_EPICS
    + PHASE_5_EPICS
    + PHASE_6_EPICS
)


def create_issue(title, body, labels):
    """Create a GitHub issue using gh CLI"""
    cmd = [
        "gh",
        "issue",
        "create",
        "--title",
        title,
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
            print(f"Error creating issue {title}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception creating issue {title}: {e}")
        return None


def main():
    print("Creating UI Revamp Issues...")
    print("=" * 80)

    epic_map = {}  # Track epic titles to issue numbers

    # Create epic issues
    for epic in ALL_EPICS:
        print(f"\nCreating EPIC: {epic['title']}")
        labels = ["epic", epic["phase"], epic["priority"], epic["component"]]
        epic_url = create_issue(epic["title"], epic["description"], labels)
        if epic_url:
            print(f"  ✓ Created: {epic_url}")
            # Extract issue number from URL
            issue_num = epic_url.split("/")[-1]
            epic_map[epic["title"]] = issue_num
            time.sleep(1)  # Rate limiting
        else:
            print(f"  ✗ Failed to create")

    print("\n" + "=" * 80)
    print("All EPICS created!")
    print(f"\nTotal Epics: {len(ALL_EPICS)}")
    print("\nNext steps:")
    print("1. Review created issues in GitHub")
    print("2. Add individual tasks to each epic")
    print("3. Set up project board if needed")


if __name__ == "__main__":
    main()
