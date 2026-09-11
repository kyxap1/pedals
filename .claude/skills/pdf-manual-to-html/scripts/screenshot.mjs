#!/usr/bin/env node
// Full-page screenshot via Chrome DevTools Protocol.
//
// `chrome --headless --screenshot --window-size=W,H` looks like a one-liner
// but isn't: it crops to exactly W×H instead of capturing full page height,
// and it has no timeout flag, so a bad invocation hangs forever. This script
// drives Chrome over CDP instead — it measures real page height, captures
// the whole thing in one shot, and enforces its own timeout so it can never
// hang undetected regardless of what wraps it.
//
// Usage: node screenshot.mjs <url> <out.png> <width> [timeoutSeconds=30]

import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";
import { writeFileSync } from "node:fs";

const [, , url, outPath, widthArg, timeoutArg] = process.argv;
if (!url || !outPath || !widthArg) {
  console.error("usage: node screenshot.mjs <url> <out.png> <width> [timeoutSeconds=30]");
  process.exit(1);
}
const width = Number(widthArg);
const timeoutMs = Number(timeoutArg ?? 30) * 1000;

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9222 + Math.floor(Math.random() * 1000);

const chrome = spawn(chromePath, [
  "--headless=new",
  "--hide-scrollbars",
  `--remote-debugging-port=${port}`,
  "--no-first-run",
]);
chrome.on("error", (e) => {
  console.error("failed to launch chrome:", e.message);
  process.exit(1);
});

const killer = setTimeout(() => {
  console.error(`timed out after ${timeoutMs}ms — killing chrome`);
  chrome.kill("SIGKILL");
  process.exit(1);
}, timeoutMs);

try {
  await run();
} finally {
  clearTimeout(killer);
  chrome.kill("SIGKILL");
}

async function run() {
  // Wait for the DevTools HTTP endpoint to come up.
  let targetInfo;
  for (let i = 0; i < 100; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`, { method: "PUT" });
      targetInfo = await res.json();
      break;
    } catch {
      await delay(100);
    }
  }
  if (!targetInfo) throw new Error("chrome devtools endpoint never came up");

  const ws = new WebSocket(targetInfo.webSocketDebuggerUrl);
  await new Promise((res, rej) => {
    ws.addEventListener("open", res, { once: true });
    ws.addEventListener("error", rej, { once: true });
  });

  let id = 0;
  const pending = new Map();
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      pending.get(msg.id)(msg);
      pending.delete(msg.id);
    }
  });
  function send(method, params = {}) {
    const thisId = ++id;
    ws.send(JSON.stringify({ id: thisId, method, params }));
    return new Promise((res) => pending.set(thisId, res));
  }

  await send("Page.enable");
  const loadFired = new Promise((res) => {
    function handler(ev) {
      const msg = JSON.parse(ev.data);
      if (msg.method === "Page.loadEventFired") {
        ws.removeEventListener("message", handler);
        res();
      }
    }
    ws.addEventListener("message", handler);
  });
  await send("Page.navigate", { url });
  await loadFired;
  await delay(200); // let webfonts/layout settle

  await send("Emulation.setDeviceMetricsOverride", {
    width,
    height: 800,
    deviceScaleFactor: 1,
    mobile: width < 900,
  });
  const metrics = await send("Page.getLayoutMetrics");
  const height = Math.ceil(metrics.result.cssContentSize.height);

  const shot = await send("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
    clip: { x: 0, y: 0, width, height, scale: 1 },
  });
  if (!shot.result?.data) throw new Error("capture failed: " + JSON.stringify(shot));
  writeFileSync(outPath, Buffer.from(shot.result.data, "base64"));
  console.log(`wrote ${outPath} (${width}x${height})`);
  ws.close();
}
