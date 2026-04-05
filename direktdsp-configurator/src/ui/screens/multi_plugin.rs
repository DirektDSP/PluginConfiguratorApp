use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, List, ListItem, Paragraph};

use crossterm::event::KeyCode;

use crate::app::{App, PluginFieldSet};

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3), // Help text
            Constraint::Min(0),   // Plugin list / editor
        ])
        .split(area);

    // Help text
    let help = if app.multi_plugin.editing_field.is_some() {
        "Tab: next field | Shift+Tab: prev field | Esc: back to list"
    } else {
        "a: add plugin | d: delete | Enter: edit fields | Up/Down: navigate"
    };
    let help_para = Paragraph::new(help)
        .style(Style::default().fg(Color::DarkGray))
        .block(Block::default().borders(Borders::ALL).title(" Multi-Plugin "));
    f.render_widget(help_para, chunks[0]);

    if app.config.project.plugins.is_empty() {
        let empty = Paragraph::new("No plugins added. Press 'a' to add a plugin.")
            .style(Style::default().fg(Color::DarkGray))
            .block(Block::default().borders(Borders::ALL).title(" Plugins "));
        f.render_widget(empty, chunks[1]);
        return;
    }

    // If editing a specific plugin's fields, show the field editor
    if let Some(field_idx) = app.multi_plugin.editing_field {
        draw_plugin_editor(f, app, chunks[1], app.multi_plugin.selected, field_idx);
    } else {
        draw_plugin_list(f, app, chunks[1]);
    }
}

fn draw_plugin_list(f: &mut Frame, app: &App, area: Rect) {
    let items: Vec<ListItem> = app
        .config
        .project
        .plugins
        .iter()
        .enumerate()
        .map(|(i, plugin)| {
            let selected = i == app.multi_plugin.selected;
            let prefix = if selected { "▸ " } else { "  " };

            let style = if selected {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };

            let desc = format!(
                "  ({}, {})",
                plugin.bundle_id, plugin.plugin_code
            );
            let desc_style = Style::default().fg(Color::DarkGray);

            ListItem::new(Line::from(vec![
                Span::styled(format!("{prefix}{}", plugin.name), style),
                Span::styled(desc, desc_style),
            ]))
        })
        .collect();

    let title = format!(" Plugins ({}) ", app.config.project.plugins.len());
    let list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(title),
    );
    f.render_widget(list, area);
}

fn draw_plugin_editor(f: &mut Frame, app: &App, area: Rect, plugin_idx: usize, focused_field: usize) {
    let Some(pf) = app.multi_plugin.plugin_fields.get(plugin_idx) else {
        return;
    };

    let items: Vec<ListItem> = pf
        .fields
        .iter()
        .enumerate()
        .map(|(i, field)| {
            let focused = i == focused_field;
            let prefix = if focused { "▸ " } else { "  " };

            let label_style = Style::default().fg(Color::DarkGray);
            let value_style = if focused {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };

            ListItem::new(Line::from(vec![
                Span::styled(format!("{prefix}{}: ", field.label), label_style),
                Span::styled(&field.value, value_style),
                if focused {
                    Span::styled("_", Style::default().fg(Color::Yellow))
                } else {
                    Span::raw("")
                },
            ]))
        })
        .collect();

    let plugin_name = &app.config.project.plugins[plugin_idx].name;
    let title = format!(" Editing: {} ", plugin_name);
    let list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(title),
    );
    f.render_widget(list, area);
}

pub fn handle_input(app: &mut App, key: crossterm::event::KeyEvent) {
    if app.multi_plugin.editing_field.is_some() {
        handle_field_editing(app, key);
    } else {
        handle_list_navigation(app, key);
    }
}

fn handle_list_navigation(app: &mut App, key: crossterm::event::KeyEvent) {
    let count = app.config.project.plugins.len();

    match key.code {
        KeyCode::Up | KeyCode::Char('k') => {
            if app.multi_plugin.selected > 0 {
                app.multi_plugin.selected -= 1;
            }
        }
        KeyCode::Down | KeyCode::Char('j') => {
            if count > 0 && app.multi_plugin.selected < count - 1 {
                app.multi_plugin.selected += 1;
            }
        }
        KeyCode::Char('a') => {
            app.add_plugin();
            app.multi_plugin.selected = app.config.project.plugins.len() - 1;
        }
        KeyCode::Char('d') => {
            if count > 0 {
                app.remove_plugin(app.multi_plugin.selected);
            }
        }
        KeyCode::Enter => {
            if count > 0 {
                app.multi_plugin.editing_field = Some(0);
            }
        }
        _ => {}
    }
}

fn handle_field_editing(app: &mut App, key: crossterm::event::KeyEvent) {
    use crossterm::event::KeyCode;

    let plugin_idx = app.multi_plugin.selected;
    let field_idx = app.multi_plugin.editing_field.unwrap();

    match key.code {
        KeyCode::Esc => {
            // Sync back to config and exit editing
            if let Some(pf) = app.multi_plugin.plugin_fields.get(plugin_idx) {
                app.config.project.plugins[plugin_idx] = pf.to_plugin();
            }
            app.multi_plugin.editing_field = None;
        }
        KeyCode::Tab => {
            // Sync current field, move to next
            sync_field_to_plugin(app, plugin_idx);
            let next = (field_idx + 1) % PluginFieldSet::FIELD_COUNT;
            app.multi_plugin.editing_field = Some(next);
        }
        KeyCode::BackTab => {
            sync_field_to_plugin(app, plugin_idx);
            let prev = if field_idx == 0 {
                PluginFieldSet::FIELD_COUNT - 1
            } else {
                field_idx - 1
            };
            app.multi_plugin.editing_field = Some(prev);
        }
        KeyCode::Char(c) => {
            if let Some(pf) = app.multi_plugin.plugin_fields.get_mut(plugin_idx) {
                pf.fields[field_idx].value.push(c);
            }
        }
        KeyCode::Backspace => {
            if let Some(pf) = app.multi_plugin.plugin_fields.get_mut(plugin_idx) {
                pf.fields[field_idx].value.pop();
            }
        }
        _ => {}
    }
}

fn sync_field_to_plugin(app: &mut App, plugin_idx: usize) {
    if let Some(pf) = app.multi_plugin.plugin_fields.get(plugin_idx) {
        if plugin_idx < app.config.project.plugins.len() {
            app.config.project.plugins[plugin_idx] = pf.to_plugin();
        }
    }
}
