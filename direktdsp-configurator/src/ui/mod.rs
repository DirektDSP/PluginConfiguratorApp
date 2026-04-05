pub mod screens;
pub mod widgets;

use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Paragraph, Tabs};

use crate::app::{App, Screen};

pub fn draw(f: &mut Frame, app: &App) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3), // Tab bar
            Constraint::Min(0),   // Screen content
            Constraint::Length(1), // Status bar
        ])
        .split(f.area());

    draw_tab_bar(f, app, chunks[0]);

    match app.screen {
        Screen::Welcome => screens::welcome::draw(f, app, chunks[1]),
        Screen::ProjectInfo => screens::project_info::draw(f, app, chunks[1]),
        Screen::Formats => screens::formats::draw(f, app, chunks[1]),
        Screen::Modules => screens::modules::draw(f, app, chunks[1]),
        Screen::MultiPlugin => screens::multi_plugin::draw(f, app, chunks[1]),
        Screen::BuildOptions => screens::build_options::draw(f, app, chunks[1]),
        Screen::Review => screens::review::draw(f, app, chunks[1]),
        Screen::Generate => screens::generate::draw(f, app, chunks[1]),
    }

    draw_status_bar(f, app, chunks[2]);
}

fn draw_tab_bar(f: &mut Frame, app: &App, area: Rect) {
    let active = app.active_screens();
    let titles: Vec<Line> = active
        .iter()
        .map(|s| {
            let style = if *s == app.screen {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::DarkGray)
            };
            Line::from(Span::styled(s.title(), style))
        })
        .collect();

    let tabs = Tabs::new(titles)
        .block(Block::default().borders(Borders::BOTTOM).title(" DirektDSP Plugin Configurator "))
        .select(app.screen.index_in(&active))
        .highlight_style(Style::default().fg(Color::Yellow));

    f.render_widget(tabs, area);
}

fn draw_status_bar(f: &mut Frame, app: &App, area: Rect) {
    let msg = app
        .status_message
        .as_deref()
        .unwrap_or("Ctrl+N: Next | Ctrl+P: Prev | q: Quit");
    let para = Paragraph::new(msg).style(Style::default().fg(Color::DarkGray));
    f.render_widget(para, area);
}
