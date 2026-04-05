use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::app::App;
use crate::config::project_config::{ModuleConfig, PluginFormat};

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(area);

    draw_config_summary(f, app, chunks[0]);
    draw_file_tree(f, app, chunks[1]);
}

fn draw_config_summary(f: &mut Frame, app: &App, area: Rect) {
    let cfg = &app.config;
    let p = &cfg.project;

    let formats: String = p
        .formats
        .iter()
        .map(|f| f.label())
        .collect::<Vec<_>>()
        .join(", ");

    let enabled_modules: String = ModuleConfig::MODULES
        .iter()
        .filter(|m| cfg.modules.get(m.key))
        .map(|m| m.label)
        .collect::<Vec<_>>()
        .join(", ");

    let codes = format!("{} / {}", p.manufacturer_code, p.plugin_code);
    let cpp_std = format!("C++{}", cfg.build.cpp_standard);

    let mut lines = vec![
        section_header("Project"),
        field("Name", &p.name),
        field("Product", &p.product_name),
        field("Company", &p.company_name),
        field("Bundle ID", &p.bundle_id),
        field("Codes", &codes),
        field("Version", &p.version),
        field("Multi-Plugin", if p.multi_plugin { "Yes" } else { "No" }),
        Line::from(""),
        section_header("Formats"),
        field("Enabled", &formats),
        Line::from(""),
        section_header("Modules"),
        field("Enabled", &enabled_modules),
        Line::from(""),
        section_header("Build"),
        field("C++ Standard", &cpp_std),
        field(
            "Copy After Build",
            if cfg.build.copy_after_build {
                "Yes"
            } else {
                "No"
            },
        ),
        field("IPP", if cfg.build.ipp { "Yes" } else { "No" }),
    ];

    if p.multi_plugin && !p.plugins.is_empty() {
        lines.push(Line::from(""));
        lines.push(section_header("Plugins"));
        for plugin in &p.plugins {
            lines.push(field(
                "  Plugin",
                &format!(
                    "{} ({}, {})",
                    plugin.name, plugin.bundle_id, plugin.plugin_code
                ),
            ));
        }
    }

    let para = Paragraph::new(lines).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Configuration Summary "),
    );

    f.render_widget(para, area);
}

fn draw_file_tree(f: &mut Frame, app: &App, area: Rect) {
    let name = &app.config.project.name;
    let has_clap = app.config.project.formats.contains(&PluginFormat::CLAP);
    let has_moonbase = app.config.modules.moonbase;
    let has_common = app.config.modules.common_layer;
    let is_multi = app.config.project.multi_plugin;

    let root_name = format!("{name}/");
    let mut lines = vec![
        tree_line(0, &root_name, Color::Cyan),
        tree_line(1, "CMakeLists.txt", Color::White),
        tree_line(1, "project.toml", Color::Green),
        tree_line(1, "VERSION", Color::White),
        tree_line(1, "JUCE/", Color::DarkGray),
        tree_line(1, "cmake/", Color::DarkGray),
        tree_line(1, "cmake-local/", Color::White),
        tree_line(2, "ReadProjectConfig.cmake", Color::White),
        tree_line(2, "ModuleSystem.cmake", Color::White),
        tree_line(2, "options.cmake", Color::Green),
    ];

    if !is_multi {
        lines.push(tree_line(1, "source/", Color::White));
        lines.push(tree_line(2, "PluginProcessor.h/cpp", Color::White));
        lines.push(tree_line(2, "PluginEditor.h/cpp", Color::White));
    }

    if has_common {
        lines.push(tree_line(1, "common/", Color::Yellow));
    }

    if is_multi && !app.config.project.plugins.is_empty() {
        lines.push(tree_line(1, "plugins/", Color::Magenta));
        for plugin in &app.config.project.plugins {
            let pname = format!("{}/", plugin.name);
            lines.push(tree_line(2, &pname, Color::Magenta));
            lines.push(tree_line(3, "CMakeLists.txt", Color::White));
            lines.push(tree_line(3, "source/", Color::White));
            lines.push(tree_line(3, "assets/", Color::White));
            if has_moonbase {
                lines.push(tree_line(3, "moonbase_api_config.json", Color::DarkGray));
            }
        }
    }

    lines.push(tree_line(1, "modules/", Color::White));
    if has_clap {
        lines.push(tree_line(2, "clap-juce-extensions/", Color::DarkGray));
    }
    if has_moonbase {
        lines.push(tree_line(2, "moonbase_JUCEClient/", Color::DarkGray));
    }

    lines.push(tree_line(1, "assets/", Color::White));
    lines.push(tree_line(1, "tests/", Color::White));
    lines.push(tree_line(1, "scripts/", Color::White));

    let para = Paragraph::new(lines).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" File Tree Preview "),
    );

    f.render_widget(para, area);
}

fn section_header(title: &str) -> Line<'static> {
    Line::from(Span::styled(
        title.to_string(),
        Style::default()
            .fg(Color::Cyan)
            .add_modifier(Modifier::BOLD),
    ))
}

fn field(label: &str, value: &str) -> Line<'static> {
    Line::from(vec![
        Span::styled(format!("  {label}: "), Style::default().fg(Color::DarkGray)),
        Span::styled(value.to_string(), Style::default().fg(Color::White)),
    ])
}

fn tree_line(depth: usize, name: &str, color: Color) -> Line<'static> {
    let indent = "  ".repeat(depth);
    let prefix = if depth > 0 { "├─ " } else { "" };
    Line::from(Span::styled(
        format!("{indent}{prefix}{name}"),
        Style::default().fg(color),
    ))
}
