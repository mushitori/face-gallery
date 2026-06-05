use std::sync::Mutex;
use std::time::{Duration, Instant};

use tauri::{AppHandle, Manager};
use tauri_plugin_shell::process::{CommandChild, CommandEvent};
use tauri_plugin_shell::ShellExt;

const API_PORT: u16 = 28765;
const HEALTH_TIMEOUT_SECS: u64 = 600;

fn health_url() -> String {
    format!("http://127.0.0.1:{API_PORT}/health")
}

pub struct SidecarState {
    pub child: Mutex<Option<CommandChild>>,
}

impl SidecarState {
    pub fn new() -> Self {
        Self {
            child: Mutex::new(None),
        }
    }
}

fn log_sidecar_bytes(label: &str, bytes: &[u8]) {
    let line = String::from_utf8_lossy(bytes);
    let trimmed = line.trim_end();
    if !trimmed.is_empty() {
        eprintln!("{label}: {trimmed}");
    }
}

fn spawn_health_wait() {
    std::thread::spawn(|| {
        if let Err(err) = wait_for_health() {
            eprintln!("API health check failed: {err}");
        }
    });
}

/// In dev, expect Python API started manually (`npm run dev:api`).
/// In release, spawn PyInstaller sidecar.
pub fn start_sidecar_if_needed(app: &AppHandle) -> Result<(), String> {
    if cfg!(debug_assertions) {
        spawn_health_wait();
        return Ok(());
    }

    let shell = app.shell();
    let sidecar = shell
        .sidecar("api")
        .map_err(|e| e.to_string())?
        .args(["--port", &API_PORT.to_string()]);

    let (mut rx, child) = sidecar.spawn().map_err(|e| e.to_string())?;

    let state = app.state::<SidecarState>();
    *state.child.lock().map_err(|e| e.to_string())? = Some(child);

    tauri::async_runtime::spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Error(err) => eprintln!("sidecar error: {err}"),
                CommandEvent::Stdout(line) => log_sidecar_bytes("api", &line),
                CommandEvent::Stderr(line) => log_sidecar_bytes("api", &line),
                _ => {}
            }
        }
    });

    spawn_health_wait();
    Ok(())
}

pub fn wait_for_health() -> Result<(), String> {
    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(2))
        .build()
        .map_err(|e| e.to_string())?;
    let start = Instant::now();
    while start.elapsed() < Duration::from_secs(HEALTH_TIMEOUT_SECS) {
        if let Ok(res) = client.get(health_url()).send() {
            if res.status().is_success() {
                return Ok(());
            }
        }
        std::thread::sleep(Duration::from_millis(400));
    }
    Err(
        "API health check timed out. Start backend: npm run dev:api (from repo root)"
            .into(),
    )
}

pub fn shutdown_api() {
    let client = reqwest::blocking::Client::builder()
        .timeout(Duration::from_secs(2))
        .build();
    if let Ok(c) = client {
        let _ = c
            .post(format!("http://127.0.0.1:{}/shutdown", API_PORT))
            .send();
    }
}

pub fn kill_sidecar(app: &AppHandle) {
    shutdown_api();
    if let Some(state) = app.try_state::<SidecarState>() {
        if let Ok(mut guard) = state.child.lock() {
            if let Some(child) = guard.take() {
                let _ = child.kill();
            }
        }
    }
}
