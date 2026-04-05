use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Paragraph};

use crate::app::App;

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let block = Block::default()
        .borders(Borders::ALL)
        .title(" Project Info ");
    let inner = block.inner(area);
    f.render_widget(block, area);

    let field_count = app.project_info.fields.len() as u16;
    let constraints: Vec<Constraint> = (0..field_count)
        .map(|_| Constraint::Length(3))
        .chain(std::iter::once(Constraint::Min(0)))
        .collect();

    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints(constraints)
        .split(inner);

    for (i, field) in app.project_info.fields.iter().enumerate() {
        let focused = i == app.project_info.focused_field;
        let border_style = if focused {
            Style::default().fg(Color::Yellow)
        } else {
            Style::default().fg(Color::DarkGray)
        };

        let mut spans = vec![Span::raw(&field.value)];
        if focused {
            spans.push(Span::styled("▏", Style::default().fg(Color::Yellow)));
        }

        let label = if let Some(ref err) = field.error {
            format!(" {} — {} ", field.label, err)
        } else {
            format!(" {} ", field.label)
        };

        let label_style = if field.error.is_some() {
            Style::default().fg(Color::Red)
        } else if focused {
            Style::default()
                .fg(Color::Yellow)
                .add_modifier(Modifier::BOLD)
        } else {
            Style::default()
        };

        let input = Paragraph::new(Line::from(spans)).block(
            Block::default()
                .borders(Borders::ALL)
                .border_style(border_style)
                .title(Span::styled(label, label_style)),
        );

        f.render_widget(input, chunks[i]);
    }
}

pub fn handle_input(app: &mut App, key: crossterm::event::KeyEvent) {
    use crossterm::event::KeyCode;

    let field_count = app.project_info.fields.len();

    match key.code {
        KeyCode::Tab => {
            app.project_info.focused_field = (app.project_info.focused_field + 1) % field_count;
        }
        KeyCode::BackTab => {
            app.project_info.focused_field = if app.project_info.focused_field == 0 {
                field_count - 1
            } else {
                app.project_info.focused_field - 1
            };
        }
        KeyCode::Char(c) => {
            let field = &mut app.project_info.fields[app.project_info.focused_field];
            field.value.insert(field.cursor, c);
            field.cursor += 1;
            validate_field(field, app.project_info.focused_field);
        }
        KeyCode::Backspace => {
            let field = &mut app.project_info.fields[app.project_info.focused_field];
            if field.cursor > 0 {
                field.cursor -= 1;
                field.value.remove(field.cursor);
                validate_field(field, app.project_info.focused_field);
            }
        }
        KeyCode::Left => {
            let field = &mut app.project_info.fields[app.project_info.focused_field];
            if field.cursor > 0 {
                field.cursor -= 1;
            }
        }
        KeyCode::Right => {
            let field = &mut app.project_info.fields[app.project_info.focused_field];
            if field.cursor < field.value.len() {
                field.cursor += 1;
            }
        }
        _ => {}
    }
}

fn validate_field(field: &mut crate::app::TextFieldState, index: usize) {
    field.error = match index {
        0 => {
            // Plugin Name: non-empty, alphanumeric + underscore
            if field.value.is_empty() {
                Some("Required".into())
            } else if !field.value.chars().all(|c| c.is_alphanumeric() || c == '_') {
                Some("Alphanumeric + underscore only".into())
            } else {
                None
            }
        }
        3 => {
            // Bundle ID: reverse domain notation
            if !field.value.is_empty()
                && !regex::Regex::new(r"^[a-z][a-z0-9]*(\.[a-z][a-z0-9]*)+$")
                    .unwrap()
                    .is_match(&field.value)
            {
                Some("e.g. com.company.plugin".into())
            } else {
                None
            }
        }
        4 | 5 => {
            // Manufacturer/Plugin Code: exactly 4 chars
            if !field.value.is_empty() && field.value.len() != 4 {
                Some("Must be exactly 4 characters".into())
            } else {
                None
            }
        }
        6 => {
            // Version: semver
            if !field.value.is_empty() && semver::Version::parse(&field.value).is_err() {
                Some("Must be semver (e.g. 1.0.0)".into())
            } else {
                None
            }
        }
        _ => None,
    };
}
