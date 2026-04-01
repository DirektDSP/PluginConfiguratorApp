"""DirektDSP_GUI component registry for template descriptions.

Maps UI template tiers to the DirektDSP_GUI framework components they include.
Component data is organised by category to match the framework's directory
structure (core/, controls/, display/, layout/, chrome/, theme/, config/).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GuiComponent:
    """A single DirektDSP_GUI component."""

    name: str
    category: str
    description: str


# ---------------------------------------------------------------------------
# Full component catalogue — mirrors DirektDSP_GUI repo structure
# ---------------------------------------------------------------------------

_ALL_COMPONENTS: dict[str, GuiComponent] = {
    # core
    "DirektBaseEditor": GuiComponent(
        "DirektBaseEditor", "core", "Base editor class for all plugin UIs"
    ),
    "DirektAutoLayout": GuiComponent(
        "DirektAutoLayout", "core", "Automatic component layout engine"
    ),
    "DirektComponentRegistry": GuiComponent(
        "DirektComponentRegistry", "core", "Central registry for GUI components"
    ),
    "DirektBuildContext": GuiComponent(
        "DirektBuildContext", "core", "Build-time configuration context"
    ),
    # controls
    "DirektKnob": GuiComponent("DirektKnob", "controls", "Rotary knob control"),
    "DirektToggle": GuiComponent("DirektToggle", "controls", "Toggle switch control"),
    "DirektComboBox": GuiComponent("DirektComboBox", "controls", "Drop-down selector"),
    # display
    "DirektLabel": GuiComponent("DirektLabel", "display", "Styled text label"),
    "DirektMeter": GuiComponent("DirektMeter", "display", "Level meter display"),
    # layout
    "DirektFlexContainer": GuiComponent(
        "DirektFlexContainer", "layout", "Flexbox-style layout container"
    ),
    "DirektSection": GuiComponent("DirektSection", "layout", "Grouped section container"),
    "DirektTabPanel": GuiComponent("DirektTabPanel", "layout", "Tabbed panel container"),
    # chrome
    "DirektHeader": GuiComponent("DirektHeader", "chrome", "Plugin header bar"),
    "DirektFooter": GuiComponent("DirektFooter", "chrome", "Plugin footer bar"),
    "DirektPopupPanel": GuiComponent("DirektPopupPanel", "chrome", "Modal popup panel"),
    "DirektPresetBrowser": GuiComponent(
        "DirektPresetBrowser", "chrome", "Built-in preset browser"
    ),
    # theme
    "DirektLookAndFeel": GuiComponent(
        "DirektLookAndFeel", "theme", "Custom look-and-feel styling"
    ),
    "DirektColours": GuiComponent("DirektColours", "theme", "Colour palette definitions"),
    # config
    "DirektConfig": GuiComponent("DirektConfig", "config", "Runtime configuration"),
    "DirektDescriptors": GuiComponent(
        "DirektDescriptors", "config", "Component descriptor definitions"
    ),
    "DirektDescriptorHelpers": GuiComponent(
        "DirektDescriptorHelpers", "config", "Descriptor utility helpers"
    ),
}

# ---------------------------------------------------------------------------
# Template-tier component mappings
# ---------------------------------------------------------------------------

UI_TEMPLATE_COMPONENTS: dict[str, list[str]] = {
    "Minimal": [
        "DirektBaseEditor",
        "DirektBuildContext",
        "DirektKnob",
        "DirektToggle",
        "DirektLabel",
        "DirektConfig",
    ],
    "Standard": [
        "DirektBaseEditor",
        "DirektAutoLayout",
        "DirektComponentRegistry",
        "DirektBuildContext",
        "DirektKnob",
        "DirektToggle",
        "DirektComboBox",
        "DirektLabel",
        "DirektFlexContainer",
        "DirektSection",
        "DirektHeader",
        "DirektFooter",
        "DirektLookAndFeel",
        "DirektColours",
        "DirektConfig",
        "DirektDescriptors",
    ],
    "Advanced": [
        "DirektBaseEditor",
        "DirektAutoLayout",
        "DirektComponentRegistry",
        "DirektBuildContext",
        "DirektKnob",
        "DirektToggle",
        "DirektComboBox",
        "DirektLabel",
        "DirektMeter",
        "DirektFlexContainer",
        "DirektSection",
        "DirektTabPanel",
        "DirektHeader",
        "DirektFooter",
        "DirektPopupPanel",
        "DirektPresetBrowser",
        "DirektLookAndFeel",
        "DirektColours",
        "DirektConfig",
        "DirektDescriptors",
        "DirektDescriptorHelpers",
    ],
    "Scratch": [
        "DirektBaseEditor",
        "DirektBuildContext",
        "DirektConfig",
    ],
}


def get_components_for_template(template_name: str) -> list[GuiComponent]:
    """Return the list of GuiComponent objects for a UI template tier."""
    keys = UI_TEMPLATE_COMPONENTS.get(template_name, [])
    return [_ALL_COMPONENTS[k] for k in keys if k in _ALL_COMPONENTS]


def get_components_grouped(template_name: str) -> dict[str, list[GuiComponent]]:
    """Return components grouped by category for a UI template tier."""
    grouped: dict[str, list[GuiComponent]] = {}
    for comp in get_components_for_template(template_name):
        grouped.setdefault(comp.category, []).append(comp)
    return grouped
