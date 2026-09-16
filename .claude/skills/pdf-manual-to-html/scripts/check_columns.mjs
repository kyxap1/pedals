#!/usr/bin/env node
// Column-break check for two-column sections, across a sweep of widths.
//
// Multi-column balancing moves every break as the viewport changes, so a page
// that looks right at 1400 px strands a figure at 1700. This walks each
// `.half-container` in flow order at every width and reports:
//
//   figure   — an image starts the right column while the text leading into it
//              (either of the two blocks before it) is still in the left one;
//   lead-in  — a block ending in ":" sits in one column and what it introduces
//              (list, menu path, figure) in the other.
//
// Images inside callouts, figure grids, tables and spanning headers are
// skipped: those boxes never split.
//
// Usage: node check_columns.mjs <url> [from=1000] [to=2600] [step=20] [timeoutSeconds=300]
// Exits 1 when anything is found.

import { spawn } from "node:child_process";
import { setTimeout as delay } from "node:timers/promises";

const [, , url, fromArg, toArg, stepArg, timeoutArg] = process.argv;
if (!url) {
  console.error("usage: node check_columns.mjs <url> [from=1000] [to=2600] [step=20] [timeoutSeconds=300]");
  process.exit(2);
}
const from = Number(fromArg ?? 1000);
const to = Number(toArg ?? 2600);
const step = Number(stepArg ?? 20);
const timeoutMs = Number(timeoutArg ?? 300) * 1000;

const chromePath = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const port = 9222 + Math.floor(Math.random() * 1000);
const chrome = spawn(chromePath, ["--headless=new", "--hide-scrollbars", `--remote-debugging-port=${port}`, "--no-first-run"]);
chrome.on("error", (e) => {
  console.error("failed to launch chrome:", e.message);
  process.exit(2);
});
const killer = setTimeout(() => {
  console.error(`timed out after ${timeoutMs}ms — killing chrome`);
  chrome.kill("SIGKILL");
  process.exit(2);
}, timeoutMs);

// Runs in the page; returns [{kind, text}] for the current width.
const probe = `(() => {
  const out = [];
  const skip = '.callout, .warning, .warning-center, .grid-wrapper, .sweep-graphs, .hw-grid, .screen-nav, figure, header, table';
  const label = (el) => el.tagName === 'IMG' ? el.getAttribute('src') : el.textContent.trim().replace(/\\s+/g, ' ').slice(0, 60);
  for (const c of document.querySelectorAll('.half-container')) {
    const cr = c.getBoundingClientRect();
    const mid = cr.left + cr.width / 2;
    const col = (el) => (el.getBoundingClientRect().left + 5 < mid ? 0 : 1);
    const blocks = [...c.querySelectorAll('p, li, h3, h4, h5, h6, img')]
      .filter((e) => !e.closest(skip) && !(e.tagName === 'LI' && e.querySelector('p')) && e.getBoundingClientRect().height > 0);
    if (!blocks.some((b) => col(b) === 1)) continue;
    blocks.forEach((b, i) => {
      if (b.tagName === 'IMG' && col(b) === 1) {
        const before = blocks.slice(Math.max(0, i - 2), i).filter((e) => e.tagName !== 'IMG');
        if (before.some((e) => col(e) === 0)) out.push({ kind: 'figure', text: label(b) });
      }
      const next = blocks[i + 1];
      if (b.tagName !== 'IMG' && next && /:$/.test(b.textContent.trim()) && col(b) !== col(next))
        out.push({ kind: 'lead-in', text: label(b) });
    });
  }
  return out;
})()`;

let found = 0;
try {
  found = await run();
} finally {
  clearTimeout(killer);
  chrome.kill("SIGKILL");
}
process.exit(found ? 1 : 0);

async function run() {
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
  const send = (method, params = {}) => {
    const thisId = ++id;
    ws.send(JSON.stringify({ id: thisId, method, params }));
    return new Promise((res) => pending.set(thisId, res));
  };

  await send("Page.enable");
  const loadFired = new Promise((res) => {
    const handler = (ev) => {
      if (JSON.parse(ev.data).method === "Page.loadEventFired") {
        ws.removeEventListener("message", handler);
        res();
      }
    };
    ws.addEventListener("message", handler);
  });
  await send("Page.navigate", { url });
  await loadFired;
  await delay(200);
  // lazy images below the fold have no height until loaded, which shifts every break
  await send("Runtime.evaluate", {
    expression: `Promise.all([...document.images].map((i) => { i.loading = "eager"; return i.decode().catch(() => {}); }))`,
    awaitPromise: true,
  });

  const hits = new Map();
  for (let w = from; w <= to; w += step) {
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: 800, deviceScaleFactor: 1, mobile: false });
    const r = await send("Runtime.evaluate", { expression: probe, returnByValue: true });
    for (const { kind, text } of r.result.result.value) {
      const key = `${kind}\t${text}`;
      if (!hits.has(key)) hits.set(key, []);
      hits.get(key).push(w);
    }
  }
  ws.close();

  if (!hits.size) {
    console.log(`no column-break issues between ${from} and ${to} px`);
    return 0;
  }
  for (const [key, widths] of hits) {
    const [kind, text] = key.split("\t");
    console.log(`${kind.padEnd(8)} ${widths[0]}..${widths[widths.length - 1]} px (${widths.length} widths)  ${text}`);
  }
  return hits.size;
}
