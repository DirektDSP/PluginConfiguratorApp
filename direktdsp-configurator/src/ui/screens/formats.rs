use ratatui::Frame;
use ratatui::layout::Rect;
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, List, ListItem};

use crate::app::App;
use crate::config::project_config::PluginFormat;

/// Total number of items: formats + separator + multi-plugin toggle.
fn item_count() -> usize {
    PluginFormat::ALL.len() + 2 // +1 blank separator, +1 multi-plugin toggle
}

fn multi_plugin_index() -> usize {
    PluginFormat::ALL.len() + 1
}

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let mut items: Vec<ListItem> = PluginFormat::ALL
        .iter()
        .enumerate()
        .map(|(i, fmt)| {
            let enabled = app.config.project.formats.contains(fmt);
            let selected = i == app.formats.selected;

            let checkbox = if enabled { "[x]" } else { "[ ]" };
            let prefix = if selected { "▸ " } else { "  " };

            let style = if selected {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else if enabled {
                Style::default().fg(Color::Green)
            } else {
                Style::default().fg(Color::White)
            };

            ListItem::new(Line::from(Span::styled(
                format!("{prefix}{checkbox} {}", fmt.label()),
                style,
            )))
        })
        .collect();

    // Separator
    items.push(ListItem::new(Line::from("")));

    // Multi-plugin toggle
    let mp_selected = app.formats.selected == multi_plugin_index();
    let mp_enabled = app.config.project.multi_plugin;
    let mp_checkbox = if mp_enabled { "[x]" } else { "[ ]" };
    let mp_prefix = if mp_selected { "▸ " } else { "  " };
    let mp_style = if mp_selected {
        Style::default()
            .fg(Color::Yellow)
            .add_modifier(Modifier::BOLD)
    } else if mp_enabled {
        Style::default().fg(Color::Magenta)
    } else {
        Style::default().fg(Color::White)
    };
    let mp_desc_style = Style::default().fg(Color::DarkGray);
    items.push(ListItem::new(Line::from(vec![
        Span::styled(
            format!("{mp_prefix}{mp_checkbox} Multi-Plugin Project"),
            mp_style,
        ),
        Span::styled("  Generate multiple plugins in one project", mp_desc_style),
    ])));

    let list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Plugin Formats (Space to toggle) "),
    );

    f.render_widget(list, area);
}

pub fn handle_input(app: &mut App, key: crossterm::event::KeyEvent) {
    use crossterm::event::KeyCode;
    let total = item_count();
    let separator_idx = PluginFormat::ALL.len();

    match key.code {
        KeyCode::Up | KeyCode::Char('k') => {
            if app.formats.selected > 0 {
                app.formats.selected -= 1;
                // Skip the separator
                if app.formats.selected == separator_idx {
                    app.formats.selected -= 1;
                }
            }
        }
        KeyCode::Down | KeyCode::Char('j') => {
            if app.formats.selected < total - 1 {
                app.formats.selected += 1;
                // Skip the separator
                if app.formats.selected == separator_idx {
                    app.formats.selected += 1;
                }
            }
        }
        KeyCode::Char(' ') | KeyCode::Enter => {
            if app.formats.selected == multi_plugin_index() {
                app.config.project.multi_plugin = !app.config.project.multi_plugin;
            } else if app.formats.selected < PluginFormat::ALL.len() {
                let fmt = PluginFormat::ALL[app.formats.selected];
                if app.config.project.formats.contains(&fmt) {
                    app.config.project.formats.retain(|f| *f != fmt);
                } else {
                    app.config.project.formats.push(fmt);
                }
            }
        }
        _ => {}
    }
}
