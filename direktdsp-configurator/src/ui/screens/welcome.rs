use ratatui::Frame;
use ratatui::layout::{Alignment, Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, List, ListItem, Paragraph};

use crate::app::App;

const MENU_ITEMS: &[&str] = &["New Project", "Load Preset", "Recent Projects"];

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(8),  // Logo/header
            Constraint::Length(5),  // Menu
            Constraint::Min(0),    // Spacer
        ])
        .split(area);

    // Header
    let header = Paragraph::new(vec![
        Line::from(""),
        Line::from(Span::styled(
            "DirektDSP Plugin Configurator",
            Style::default()
                .fg(Color::Cyan)
                .add_modifier(Modifier::BOLD),
        )),
        Line::from(""),
        Line::from(Span::styled(
            "Configure and generate JUCE plugin projects",
            Style::default().fg(Color::Gray),
        )),
    ])
    .alignment(Alignment::Center)
    .block(Block::default().borders(Borders::NONE));

    f.render_widget(header, chunks[0]);

    // Menu
    let items: Vec<ListItem> = MENU_ITEMS
        .iter()
        .enumerate()
        .map(|(i, item)| {
            let style = if i == app.welcome.selected {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };
            let prefix = if i == app.welcome.selected {
                "▸ "
            } else {
                "  "
            };
            ListItem::new(Line::from(Span::styled(
                format!("{prefix}{item}"),
                style,
            )))
        })
        .collect();

    let menu = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Select an option "),
    );

    // Center the menu horizontally
    let menu_area = centered_rect(40, chunks[1]);
    f.render_widget(menu, menu_area);
}

fn centered_rect(width_pct: u16, area: Rect) -> Rect {
    let pad = (100 - width_pct) / 2;
    Layout::default()
        .direction(Direction::Horizontal)
        .constraints([
            Constraint::Percentage(pad),
            Constraint::Percentage(width_pct),
            Constraint::Percentage(pad),
        ])
        .split(area)[1]
}

pub fn handle_input(app: &mut App, key: crossterm::event::KeyEvent) {
    use crossterm::event::KeyCode;
    match key.code {
        KeyCode::Up | KeyCode::Char('k') => {
            if app.welcome.selected > 0 {
                app.welcome.selected -= 1;
            }
        }
        KeyCode::Down | KeyCode::Char('j') => {
            if app.welcome.selected < MENU_ITEMS.len() - 1 {
                app.welcome.selected += 1;
            }
        }
        KeyCode::Enter => {
            if app.welcome.selected == 0 {
                app.next_screen();
            }
            // TODO: Load Preset, Recent Projects
        }
        _ => {}
    }
}
