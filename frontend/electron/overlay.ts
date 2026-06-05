import { app, BrowserWindow, globalShortcut } from "electron";
import path from "path";

const isDev = !app.isPackaged;
const VITE_OVERLAY_URL = "http://127.0.0.1:5173/?mode=overlay";

let overlayWin: BrowserWindow | null = null;

export function createOverlayWindow(): BrowserWindow {
  overlayWin = new BrowserWindow({
    width: 720,
    height: 480,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    show: false,
    skipTaskbar: true,
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    overlayWin.loadURL(VITE_OVERLAY_URL);
  } else {
    overlayWin.loadFile(path.join(__dirname, "../dist/index.html"), {
      query: { mode: "overlay" },
    });
  }

  overlayWin.on("blur", () => {
    overlayWin?.hide();
  });

  return overlayWin;
}

export function registerOverlayShortcut(win: BrowserWindow): void {
  globalShortcut.register("Alt+Space", () => {
    if (win.isVisible()) {
      win.hide();
    } else {
      win.show();
      win.focus();
    }
  });
}

export function getOverlayWindow(): BrowserWindow | null {
  return overlayWin;
}
