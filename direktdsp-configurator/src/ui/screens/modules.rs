use ratatui::Frame;
use ratatui::layout::Rect;
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, List, ListItem};

use crate::app::App;
use crate::config::project_config::ModuleConfig;

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let items: Vec<ListItem> = ModuleConfig::MODULES
        .iter()
        .enumerate()
        .map(|(i, module)| {
            let enabled = app.config.modules.get(module.key);
            let selected = i == app.modules.selected;

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

            let desc_style = Style::default().fg(Color::DarkGray);

            ListItem::new(Line::from(vec![
                Span::styled(format!("{prefix}{checkbox} {}", module.label), style),
                Span::styled(format!("  {}", module.description), desc_style),
            ]))
        })
        .collect();

    let list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Modules (Space to toggle) "),
    );

    f.render_widget(list, area);
}

pub fn handle_input(app: &mut App, key: crossterm::event::KeyEvent) {
    use crossterm::event::KeyCode;
    let count = ModuleConfig::MODULES.len();

    match key.code {
        KeyCode::Up | KeyCode::Char('k') => {
            if app.modules.selected > 0 {
                app.modules.selected -= 1;
            }
        }
        KeyCode::Down | KeyCode::Char('j') => {
            if app.modules.selected < count - 1 {
                app.modules.selected += 1;
            }
        }
        KeyCode::Char(' ') | KeyCode::Enter => {
            let key = ModuleConfig::MODULES[app.modules.selected].key;
            app.config.modules.toggle(key);
        }
        _ => {}
    }
}
