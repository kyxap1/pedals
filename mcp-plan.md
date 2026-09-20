# MCP server for the pedal manuals

Design, not built yet. Cloudflare limits and client connector behaviour
verified against the linked sources on 2026-09-19. The one thing still open is
whether Gemini's consumer app admits this server at all — see Risks.

## What it has to do

One remote MCP endpoint that any AI client can point at and ask questions
about these manuals — MIDI, wiring, power, setup steps, examples, anything
printed in the doc.

Consumers, all of them at once:

- **Browser chats** (Claude, ChatGPT, Gemini) — cannot reach
  `pedals.kyxap.pro`. A remote MCP endpoint is the only way in.
- **CLI agents** — Codex, Claude Code, Gemini CLI. Same endpoint, so no
  per-tool config and no stuffing manuals into the context.
- **The rig-configuration app** — its own agents answer open questions about
  the board.

**Token economy is the primary design constraint, not an optimisation.** Every
tool returns a bounded, targeted answer. Nothing hands back a whole manual.

Device control for the Pirate MIDI Bridge4 stays in `pirate-midi-mcp`
(private, talks to the hardware over its Device API). It needs nothing from
here.

## Architecture

```
*/index.html                     source of truth, untouched
     │
     │  CI: build-db.mjs          HTML → sections + tables
     ▼
  dist/pedals.sql                DDL + batched INSERTs + FTS5 population
     │
     │  CI: wrangler d1 execute --remote --file
     ▼
  Cloudflare D1
     ▲
     │  SQL only — the Worker parses nothing
  Worker (createMcpHandler, Streamable HTTP, authless)
     ▲
  browser chats · CLI agents · rig app
```

The builder emits **`.sql`, not a `.sqlite` file** — `wrangler d1 execute
--file` takes SQL only, and a binary database would have to go through
`sqlite3 .dump` anyway. Individual statements have a length cap, so INSERTs are
batched (~500 rows per statement).

**Why D1 rather than JSON in the Worker.** Free Workers cap **CPU at 10 ms per
invocation** (I/O wait excluded). `JSON.parse` of a multi-megabyte index burns
that on every cold start. A D1 query is I/O wait, so search, filtering and
snippet generation cost the Worker essentially no CPU. The 10 ms cap is what
picks the storage, not preference.

Free-tier headroom: 100,000 requests/day, 128 MB memory, D1 500 MB per
database / 10 databases. The corpus is ~830 KB of plain text across 23
manuals. Not close to any limit.

## Schema

```sql
CREATE TABLE pedal (
  slug  TEXT PRIMARY KEY,          -- 'boss-rc-5'
  brand TEXT, model TEXT, type TEXT,
  url   TEXT,                      -- deep-linkable manual page
  specs TEXT                       -- JSON, see below; NULL until extracted
);

CREATE TABLE section (
  id     INTEGER PRIMARY KEY,
  slug   TEXT, anchor TEXT,        -- heading id → https://…/boss-rc-5/#connecting
  title  TEXT, level INT, ord INT,
  part   INT DEFAULT 1,            -- >1 when a long section was split
  chars  INT,                      -- of render, i.e. what a fetch actually costs
  body   TEXT,                     -- full Markdown; what FTS indexes
  render TEXT                      -- what the tools return; big tables stubbed
);

CREATE TABLE tbl (
  id INTEGER PRIMARY KEY,
  slug TEXT, section_id INT,
  caption TEXT,
  data TEXT                        -- {"headers":[…],"rows":[[…]]}, spans expanded
);

CREATE VIRTUAL TABLE section_fts USING fts5(
  title, body, content='section', content_rowid='id'
);
```

`content='section'` makes the index external-content: it stores no second copy
of the body, but it also **does not populate itself**. The dump fills `section`
first, then runs
`INSERT INTO section_fts(section_fts) VALUES('rebuild');`. There are no
triggers, because nothing ever mutates a row — every build drops and recreates.

**`body` is indexed, `render` is served.** The split exists because the largest
tables are also the most important ones, and they do not fit in a reply:

| pedal | section | table |
|---|---|---|
| `source-audio-eq2` | `midi-mapping` | **96 × 4** |
| `source-audio-collider` | `midi-implementation` | 70 × 5 |
| `boss-rc-5` | `control` | 71 × 3 |
| `pirate-midi-bridge4` | `midi-implementation` | 54 × 3 |

`body` keeps those tables whole so a search for `Shimmer` or `B0` still finds
the pedal. `render` replaces any table over ~25 rows with a one-line stub
naming its size and the `get_table` call that pages it. Roughly nine sections
of ~700 are affected, and they are the MIDI implementations.

`specs` JSON holds **only cross-pedal comparables** — the facts you answer by
comparing pedals, not by reading one section:

```json
{
  "power": {"volts": 9, "current_ma": 170, "polarity": "center-negative",
            "battery": "AA x4", "isolated_required": false},
  "io": [{"jack": "INPUT A (MONO)", "kind": "audio-in", "channels": "mono",
          "connector": "TS"}],
  "midi": {"din": false, "trs": true, "trs_type": "A", "usb": true,
           "receives": ["CC", "PC", "clock"], "channel": "1-16"}
}
```

Deliberately **not** in `specs`: control descriptions and CC/PC maps. Copying
them into a hand-built schema creates a second copy that drifts — and, worse,
a CC map lifted out of its prose is often simply wrong. See the MTET case in
Risks.

## Tools

Two tiers. The first two are named and shaped to OpenAI's connector contract,
because that is what makes the server work in ChatGPT *without* Developer Mode
and in Deep Research — see Client compatibility.

| Tool | Args | Returns | ~tokens |
|---|---|---|---|
| `search` | `query` | `{results:[{id, title, url}]}` | ~200 |
| `fetch` | `id` | `{id, title, text, url, metadata}` — one section | 300–1200 |
| `list_pedals` | `type?`, `has_midi?`, `max_current_ma?` | slug, brand, model, type | ~350 for all 23 |
| `get_section` | `pedal`, `anchor`, `part?` | one section as Markdown + deep link | 300–1200 |
| `get_table` | `pedal`, `anchor`, `offset?`, `limit=30` | one page of rows, header repeated, plus its section anchor and link | 200–700 |
| `get_specs` | `pedal` | the `specs` JSON | ~150 |

`search`/`fetch` are thin aliases over the same rows the rich tools serve; `id`
is `<slug>#<anchor>[/part]`. Three contract details are mandatory, not
stylistic:

- **Every result carries a non-empty `url`** — `https://pedals.kyxap.pro/<slug>/#<anchor>`.
  ChatGPT only makes a result citable when `url` is non-empty, and the anchors
  already exist.
- **Each tool declares an `outputSchema`.**
- **Results are returned twice**: as `structuredContent` and as a JSON-encoded
  string inside `content[0].text`.

**There is no `get_manual`.** The surest way to stop an agent burning 30K
tokens on a whole manual is not to expose the call. A human who wants the
whole thing has the URL.

Two details that make the budget real:

- **Sections are sized in CI.** Anything over ~3000 chars is split at
  sub-headings or paragraph boundaries into `part` 2, 3… so `fetch` and
  `get_section` can never return a wall. **A table is atomic** — splitting
  only ever falls on prose, because a table cut in half leaves its second
  piece headerless and unreadable.
- **`search` reports `chars` in `metadata`**, so the agent knows what a fetch
  costs before it makes it. FTS5's own `snippet()` builds the excerpt — in
  SQLite, not in the Worker.

## Client compatibility

Transport is **Streamable HTTP** everywhere: Gemini rejects legacy SSE,
ChatGPT accepts either, Cloudflare's `createMcpHandler()` emits it.

| Client | Authless | How | Gate |
|---|---|---|---|
| **Claude** web/Desktop | **yes** | Customize → Connectors → Add custom connector → URL. OAuth in Advanced settings is *optional*. | Free is capped at 1 connector; Pro/Max/Team/Enterprise unrestricted |
| **ChatGPT** | **yes** | Settings → Connectors → Advanced → Developer Mode, then Create with auth = **No authentication** | Plus/Pro/Team/Enterprise/Edu. Free has no custom connectors |
| **Gemini** web app | **unclear** | gemini.google.com → Settings → Connected Apps → Custom apps | **18+, US-located, personal Google account, Keep Activity on** — and reportedly Gemini Spark only |
| **Codex / Claude Code / Gemini CLI** | yes | config entry pointing at the URL | none |

Two caveats worth knowing before they bite:

- **Claude org-managed connectors do not work authless.** The Team/Enterprise
  admin path assumes OAuth 2.1 and attempts Dynamic Client Registration, which
  fails against a server that exposes no OAuth metadata
  ([issue #402](https://github.com/anthropics/claude-ai-mcp/issues/402)). The
  personal Customize → Connectors path is unaffected.
- **Claude cannot send a Bearer token or custom header** — the connector UI
  offers OAuth client id/secret and nothing else
  ([issue #112](https://github.com/anthropics/claude-ai-mcp/issues/112)). So if
  auth is ever needed, it is full OAuth or nothing; an API-key shortcut is not
  on the table.
- **ChatGPT without Developer Mode rejects any server lacking `search` and
  `fetch`.** That is the whole reason those two tools exist here.

## Build and deploy

The repo is static HTML today. The server adds one Node toolchain — the same
one wrangler already needs — rather than a second language:

```
mcp/
  build-db.mjs        HTML → dist/pedals.sql   (cheerio + turndown)
  build-db.test.mjs   node:test, runs on fixtures
  src/index.ts        Worker: createMcpHandler + 6 tools
  wrangler.toml       d1_databases binding
  package.json
```

`build-db.mjs` walks each `*/index.html`, cuts it at headings that carry an
`id`, converts each section to Markdown, splits anything over ~3000 chars, and
pulls `.doc-table` out separately. It is pure: HTML in, SQL string out, no
network, no D1.

**CI.** A second job in `deploy.yml`, gated on `paths: ['*/index.html',
'mcp/**']`. It runs the builder, then `wrangler d1 execute --remote --file`,
then `wrangler deploy`. The gate is not tidiness — see the write-quota risk
below.

**Local iteration** runs against `wrangler d1 execute --local` and
`wrangler dev`, so rebuilding the database fifty times while fixing the parser
costs nothing against the remote quota.

**Tool descriptions are part of the token budget and of correctness, not
documentation.** The server sets an `instructions` string telling the client to
start from `search` and fetch single sections, and each tool's description
states what it returns and roughly what it costs. A vague description is what
makes an agent call `list_pedals` and then fetch twelve sections it did not
need — and, per risk 5, what makes it answer from a table whose meaning was
two sections away.

**Tests.** `build-db.mjs` carries the project's only non-obvious logic —
span expansion, nested-table flattening, section splitting, anchor derivation.
One `node:test` file over five checked-in fixtures covers it:
`source-audio-collider` (rowspan enumerations), `boss-rc-5` (rowspan *and*
colspan, nested `.mini` tables), `source-audio-eq2` (the 96-row table that
must be stubbed in `render` and kept whole in `body`),
`disaster-area-designs-dpc-micro-ns` (`th scope="row"` label columns),
`boss-ge-7` (the trivial case). Four assertions carry it: every emitted row is
as wide as its header; no `render` exceeds the budget; every table present in
`body` is findable by a term drawn from its last row; every `tbl` row resolves to a
`section_id`, so no table can ever be served without its context. The Worker's
tools are thin SQL and need none.

## Risks

1. **D1 free tier now fails queries when the daily write quota is hit.**
   Since 2026-09-01 Cloudflare enforces 5M rows read and **100K rows written**
   per day on the free plan; over the limit, queries error until 00:00 UTC. A
   full rebuild is roughly 2–5K written rows (~900 sections after splitting,
   ~200 tables, plus FTS5 shadow tables), so 20–50 rebuilds a day. Production
   is nowhere near it; iterating on the builder against `--remote` would walk
   straight into it. Hence the path filter in CI and `--local` during
   development.
2. **Gemini web app may be unreachable regardless of design.** Claude and
   ChatGPT both take authless custom connectors — confirmed. Gemini's consumer
   app gates custom MCP behind 18+, **US location**, a personal (non-work)
   Google account and Keep Activity, and reporting says it is limited to Gemini
   Spark access. None of that is fixable from this side. Gemini CLI has no such
   gate, so the CLI path stays open either way. Nothing else in the design
   depends on this.
3. **Specs drift.** `specs.json` is extracted by agent from prose and verified
   against the PDF once; the HTML it came from keeps changing. Each file stores
   a hash of the source sections, and CI fails when they diverge. Everything
   else in the DB is regenerated from HTML on every push, so it cannot drift by
   construction.
4. **Table normalisation is the one genuinely hard part of the builder.**
   The printed tables use the full HTML table model, and a naive row-by-row
   read corrupts them silently — which is the worst failure mode, because the
   output still looks like a table.

   - **Spans.** `source-audio-collider`'s MIDI table hangs `rowspan="13"` off
     one parameter row and lists its twelve enumerated values underneath;
     `boss-rc-5` has 40 rowspans and 42 colspans. The builder expands spans by
     the HTML table model — value carried down and right until every row is
     full width — so each row stands alone: `Delay (A) Engine | 1 | 0-11 | 0 |
     Digital`. This is also what makes the Markdown correct, since Markdown has
     no rowspan at all.
   - **Nested tables.** `.doc-table` cells contain `<table class="mini">`. The
     inner table is flattened into its cell as `key: value; …`.
   - **Row headers.** 228 body cells across five manuals are `<th scope="row">`,
     not `<td>` — the label column of a table. A builder that collects only
     `<td>` drops them, and `disaster-area-designs-dpc-micro-ns`'s Chain ID
     table degrades to four bare numbers per row with no way to tell which loop
     they belong to. Cells are read as `th, td` in document order; the leading
     `th scope="row"` stays the row's first column.
   - **Class selection.** Real classes are `doc-table grid-table midi-table`,
     `doc-table card-table`, `doc-table matrix` and others — select by class
     token (`table.doc-table`), never by whole-attribute match.
   - **A table does not always sit under the matching heading.**
     `wampler-terraform`'s `midi` section is prose; its MIDI table is under
     `addendum`. So `anchor` is not a reliable way to *find* a table — search
     is, because `body` carries the table inline. `get_table` retrieves a table
     the agent has already located; it does not locate one.

5. **A table's meaning can live outside the table.** This is the one failure
   that produces a confident wrong answer rather than a visible break.

   `old-blood-noise-endeavors-mtet`'s MIDI Command Table reads:

   ```
   Expression 1 MSB | CC 1  | 0-127
   Expression 1 LSB | CC 11 | 0-1
   ```

   From the table alone, `CC 1 100` sets 100. It does not. The arithmetic is in
   the prose of `message-system`: the expression outputs run 0-255, so `CC 1
   100` yields 200, and `CC 11` adds the low bit — `CC 1 100` then `CC 11 1`
   gives 201. An agent that fetched only the table sends exactly half the
   intended value and has no way to notice.

   `disaster-area-designs-dpc-micro-ns` is the same failure at greater distance.
   Its `midi-control` prose states that CC 50, 51 and 52 control loops A, B and
   C — true only at Chain ID 0. The table below it gives the other three sets
   (53-55, 56-58, 59-61), and *how* to change the Chain ID is in
   `configuration-menu`, a different section entirely. A complete answer for a
   board with two of these pedals needs all three pieces.

   Three consequences. `get_table` always returns its section's anchor, title
   and deep link alongside the rows, and its description says the numbers may
   need the surrounding section to interpret. `search` returns every matching
   section, not the best one, and its description tells the agent that one hit
   is rarely the whole answer — for `chain id` it is two sections in different
   parts of the manual. And CC maps stay out of `specs.json` for good: a map
   separated from its prose is not a compressed truth, it is a wrong one.

## Steps

Each step is independently verifiable; nothing after step 1 can start without
it, and step 4 can be skipped indefinitely without breaking anything built
before it.

1. **`mcp/build-db.mjs` + its test.** HTML → `dist/pedals.sql`: sections,
   splitting, span expansion, nested-table flattening, `body`/`render` split,
   anchors, FTS5 rebuild. No D1, no Worker. *Done when* the test passes on all
   four fixtures and `sqlite3 :memory: < dist/pedals.sql` loads clean and
   answers `MATCH 'Shimmer'` with the Collider MIDI section.
2. **Worker with five tools** — `search`, `fetch`, `get_section`, `get_table`,
   `list_pedals` — against local D1.
   *Done when* MCP Inspector against `wrangler dev` returns a citable hit for
   "MIDI channel" and a single section under 1200 tokens.
3. **Deploy and prove the clients.** Second job in `deploy.yml` with
   `cloudflare/wrangler-action@v4` and secret `CLOUDFLARE_API_TOKEN`; path
   filter on. Verify in this order, because each step costs more setup than the
   last: Claude Code → Claude web connector → ChatGPT Developer Mode → **ChatGPT
   with Developer Mode off** (the only thing that actually exercises the
   `search`/`fetch` contract) → Gemini, to find out whether its gate blocks it.
   *Done when* the four CLI/chat clients answer a pedal question end to end.
4. **Specs.** `specs.json` for three dissimilar pedals — Pirate MIDI Bridge4
   (MIDI controller), BOSS RC-5 (looper with MIDI), BOSS GE-7 (plain EQ) — to
   settle the schema, then the remaining 20. Then `get_specs` and the
   `has_midi` / `max_current_ma` filters on `list_pedals`. Add the extraction
   step to the `pdf-manual-to-html` skill so new pedals ship with it.

Needed from the user: Cloudflare account and an API token in repo secrets.
Optionally `mcp.pedals.kyxap.pro` (needs `kyxap.pro` DNS on Cloudflare),
otherwise `*.workers.dev`.

Deferred on purpose: rate limiting. The endpoint is authless and public, and
100K requests/day is the free ceiling. Public manuals are not worth protecting
pre-emptively, and a Cloudflare rate-limiting rule can be added from the
dashboard the day it is needed — no code change.

## Sources

- https://developers.cloudflare.com/workers/platform/limits/
- https://developers.cloudflare.com/agents/guides/remote-mcp-server/
- https://developers.cloudflare.com/d1/platform/limits/
- https://community.cloudflare.com/t/d1-support-for-virtual-tables/607277
- https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp
- https://github.com/anthropics/claude-ai-mcp/issues/402 (org connectors assume OAuth)
- https://github.com/anthropics/claude-ai-mcp/issues/112 (no Bearer / custom headers)
- https://developers.openai.com/api/docs/mcp (`search` / `fetch` schemas)
- https://help.openai.com/en/articles/12584461-developer-mode-and-mcp-apps-in-chatgpt
- https://support.google.com/gemini/answer/17209137 (Gemini custom apps)
- https://support.google.com/g/answer/17106276 (Gemini Enterprise: Streamable HTTP only)
- https://developers.cloudflare.com/d1/best-practices/import-export-data/ (`--file` takes `.sql`)
- https://developers.cloudflare.com/changelog/post/2026-09-01-d1-free-tier-limit-enforcement/ (daily row quotas enforced)
