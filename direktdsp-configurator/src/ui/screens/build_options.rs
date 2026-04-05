use ratatui::Frame;
use ratatui::layout::Rect;
use ratatui::style::{Color, Modifier, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, Borders, List, ListItem};

use crate::app::App;
use crate::config::project_config::BuildConfig;

struct BuildOption {
    label: &'static str,
    description: &'static str,
}

const OPTIONS: &[BuildOption] = &[
    BuildOption {
        label: "C++ Standard",
        description: "C++ language standard version",
    },
    BuildOption {
        label: "Copy After Build",
        description: "Copy plugin to system plugin folder after build",
    },
    BuildOption {
        label: "Intel IPP",
        description: "Use Intel Performance Primitives (requires IPP installed)",
    },
];

pub fn draw(f: &mut Frame, app: &App, area: Rect) {
    let items: Vec<ListItem> = OPTIONS
        .iter()
        .enumerate()
        .map(|(i, opt)| {
            let selected = i == app.build_options.selected;
            let prefix = if selected { "▸ " } else { "  " };

            let value = match i {
                0 => {
                    let idx = app.config.build.cpp_standard_index();
                    BuildConfig::CPP_STANDARDS[idx].label.to_string()
                }
                1 => {
                    if app.config.build.copy_after_build {
                        "[x]".to_string()
                    } else {
                        "[ ]".to_string()
                    }
                }
                2 => {
                    if app.config.build.ipp {
                        "[x]".to_string()
                    } else {
                        "[ ]".to_string()
                    }
                }
                _ => String::new(),
            };

            let style = if selected {
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD)
            } else {
                Style::default().fg(Color::White)
            };

            let desc_style = Style::default().fg(Color::DarkGray);

            ListItem::new(Line::from(vec![
                Span::styled(format!("{prefix}{}: {value}", opt.label), style),
                Span::styled(format!("  {}", opt.description), desc_style),
            ]))
        })
        .collect();

    let list = List::new(items).block(
        Block::default()
            .borders(Borders::ALL)
            .title(" Build Options (Space/Enter to toggle, ←/→ for C++ std) "),
    );

    f.render_widget(list, area);
}

pub fn handle_input(app: &mut App, key: crossterm::event::KeyEvent) {
    use crossterm::event::KeyCode;

    match key.code {
        KeyCode::Up | KeyCode::Char('k') => {
            if app.build_options.selected > 0 {
                app.build_options.selected -= 1;
            }
        }
        KeyCode::Down | KeyCode::Char('j') => {
            if app.build_options.selected < OPTIONS.len() - 1 {
                app.build_options.selected += 1;
            }
        }
        KeyCode::Char(' ') | KeyCode::Enter => match app.build_options.selected {
            0 => cycle_cpp_standard(app, true),
            1 => app.config.build.copy_after_build = !app.config.build.copy_after_build,
            2 => app.config.build.ipp = !app.config.build.ipp,
            _ => {}
        },
        KeyCode::Right | KeyCode::Char('l') if app.build_options.selected == 0 => {
            cycle_cpp_standard(app, true);
        }
        KeyCode::Left | KeyCode::Char('h') if app.build_options.selected == 0 => {
            cycle_cpp_standard(app, false);
        }
        _ => {}
    }
}

fn cycle_cpp_standard(app: &mut App, forward: bool) {
    let standards = BuildConfig::CPP_STANDARDS;
    let idx = app.config.build.cpp_standard_index();
    let new_idx = if forward {
        (idx + 1) % standards.len()
    } else if idx == 0 {
        standards.len() - 1
    } else {
        idx - 1
    };
    app.config.build.cpp_standard = standards[new_idx].value;
}
