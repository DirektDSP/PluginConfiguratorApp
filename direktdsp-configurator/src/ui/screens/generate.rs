use std::path::PathBuf;
use std::sync::mpsc;

use ratatui::Frame;
use ratatui::layout::{Constraint, Direction, Layout, Rect};
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, Gauge, List, ListItem, Paragraph};

use crate::app::App;
use crate::config::preset::GenerationConfig;
use crate::generation::generator::{self, GenerationInput};

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3), // Output dir
            Constraint::Length(3), // Progress bar
            Constraint::Length(3), // Status
            Constraint::Min(0),    // Log
        ])
        .split(area);

    // Output directory input
    let dir_style =
        if app.generate.editing_output_dir && !app.generate.running && !app.generate.finished {
            Style::default().fg(Color::Yellow)
        } else {
            Style::default().fg(Color::DarkGray)
        };
    let dir_text = format!("{}/{}", app.generate.output_dir, app.config.project.name);
    let dir_para = Paragraph::new(Line::from(Span::styled(dir_text, dir_style))).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Output Directory "),
    );
    f.render_widget(dir_para, chunks[0]);

    // Progress bar
    let progress = Gauge::default()
        .block(Block::default().borders(Borders::ALL).title(" Progress "))
        .gauge_style(Style::default().fg(Color::Cyan))
        .ratio(app.generate.progress);
    f.render_widget(progress, chunks[1]);

    // Status
    let status_text = if app.generate.finished {
        if let Some(ref err) = app.generate.error {
            Span::styled(format!("Error: {err}"), Style::default().fg(Color::Red))
        } else {
            Span::styled(
                "Generation complete! Press 'q' to quit.",
                Style::default()
                    .fg(Color::Green)
                    .add_modifier(Modifier::BOLD),
            )
        }
    } else if app.generate.running {
        Span::styled("Generating...", Style::default().fg(Color::Yellow))
    } else {
        Span::styled(
            "Edit output path, then press Enter to generate",
            Style::default().fg(Color::Gray),
        )
    };

    let status = Paragraph::new(Line::from(status_text))
        .block(Block::default().borders(Borders::ALL).title(" Status "));
    f.render_widget(status, chunks[2]);

    // Log
    let items: Vec<ListItem> = app
        .generate
        .log
        .iter()
        .map(|line| {
            let color = if line.starts_with("ERROR") {
                Color::Red
            } else if line.starts_with("Warning") {
                Color::Yellow
            } else {
                Color::DarkGray
            };
            ListItem::new(Line::from(Span::styled(
                line.as_str(),
                Style::default().fg(color),
            )))
        })
        .collect();

    let log = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Generation Log "),
    );
    f.render_widget(log, chunks[3]);
}

pub fn handle_input(app: &mut App, key: crossterm::event::KeyEvent) {
    use crossterm::event::KeyCode;

    // Don't accept input while generation is running
    if app.generate.running {
        return;
    }

    // After generation finishes, allow quit
    if app.generate.finished {
        if key.code == KeyCode::Char('q') {
            app.should_quit = true;
        }
        return;
    }

    // Editing the output directory
    match key.code {
        KeyCode::Enter => {
            start_generation(app);
        }
        KeyCode::Char(c) => {
            app.generate
                .output_dir
                .insert(app.generate.output_dir_cursor, c);
            app.generate.output_dir_cursor += c.len_utf8();
        }
        KeyCode::Backspace => {
            if app.generate.output_dir_cursor > 0 {
                let prev = floor_char_boundary(
                    &app.generate.output_dir,
                    app.generate.output_dir_cursor - 1,
                );
                app.generate
                    .output_dir
                    .drain(prev..app.generate.output_dir_cursor);
                app.generate.output_dir_cursor = prev;
            }
        }
        KeyCode::Left => {
            if app.generate.output_dir_cursor > 0 {
                app.generate.output_dir_cursor = floor_char_boundary(
                    &app.generate.output_dir,
                    app.generate.output_dir_cursor - 1,
                );
            }
        }
        KeyCode::Right => {
            if app.generate.output_dir_cursor < app.generate.output_dir.len() {
                app.generate.output_dir_cursor += app.generate.output_dir
                    [app.generate.output_dir_cursor..]
                    .chars()
                    .next()
                    .map(|c| c.len_utf8())
                    .unwrap_or(0);
            }
        }
        KeyCode::Home => {
            app.generate.output_dir_cursor = 0;
        }
        KeyCode::End => {
            app.generate.output_dir_cursor = app.generate.output_dir.len();
        }
        _ => {}
    }
}

fn start_generation(app: &mut App) {
    let output_dir = PathBuf::from(&app.generate.output_dir).join(&app.config.project.name);

    let (tx, rx) = mpsc::channel();
    app.generate.rx = Some(rx);
    app.generate.running = true;
    app.generate.log.clear();
    app.generate.progress = 0.0;

    let input = GenerationInput {
        config: app.config.clone(),
        generation: GenerationConfig::default(),
        output_dir,
        module_registry: None, // TODO: pass module_registry if loaded
    };

    std::thread::spawn(move || {
        generator::run(input, tx);
    });
}

/// Find the largest byte index <= `i` that is a char boundary.
fn floor_char_boundary(s: &str, i: usize) -> usize {
    let mut pos = i;
    while pos > 0 && !s.is_char_boundary(pos) {
        pos -= 1;
    }
    pos
}
