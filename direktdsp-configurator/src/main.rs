mod app;
mod config;
mod generation;
mod ui;
mod validation;

use std::io;
use std::time::Duration;

use color_eyre::Result;
use crossterm::event::{self, Event, KeyCode, KeyModifiers};
use crossterm::terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen};
use crossterm::execute;
use ratatui::backend::CrosstermBackend;
use ratatui::Terminal;

use app::{App, Screen};

fn main() -> Result<()> {
    color_eyre::install()?;

    // Terminal setup
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let result = run(&mut terminal);

    // Terminal teardown
    disable_raw_mode()?;
    execute!(terminal.backend_mut(), LeaveAlternateScreen)?;
    terminal.show_cursor()?;

    result
}

fn run(terminal: &mut Terminal<CrosstermBackend<io::Stdout>>) -> Result<()> {
    let mut app = App::new();

    loop {
        // Poll generation progress when on Generate screen
        if app.screen == Screen::Generate {
            app.poll_generation();
        }

        terminal.draw(|f| ui::draw(f, &app))?;

        // Use a short poll timeout so we can update generation progress
        if event::poll(Duration::from_millis(50))? {
            if let Event::Key(key) = event::read()? {
                // Global keybindings
                match (key.modifiers, key.code) {
                    (_, KeyCode::Char('q')) if app.screen == Screen::Welcome => {
                        app.should_quit = true;
                    }
                    (KeyModifiers::CONTROL, KeyCode::Char('c')) => {
                        app.should_quit = true;
                    }
                    (KeyModifiers::CONTROL, KeyCode::Char('n')) => {
                        app.next_screen();
                        continue;
                    }
                    (KeyModifiers::CONTROL, KeyCode::Char('p')) => {
                        app.prev_screen();
                        continue;
                    }
                    _ => {}
                }

                if app.should_quit {
                    return Ok(());
                }

                // Per-screen input handling
                match app.screen {
                    Screen::Welcome => ui::screens::welcome::handle_input(&mut app, key),
                    Screen::ProjectInfo => ui::screens::project_info::handle_input(&mut app, key),
                    Screen::Formats => ui::screens::formats::handle_input(&mut app, key),
                    Screen::Modules => ui::screens::modules::handle_input(&mut app, key),
                    Screen::MultiPlugin => ui::screens::multi_plugin::handle_input(&mut app, key),
                    Screen::BuildOptions => ui::screens::build_options::handle_input(&mut app, key),
                    Screen::Review => {} // Read-only screen
                    Screen::Generate => ui::screens::generate::handle_input(&mut app, key),
                }
            }
        }
    }
}
