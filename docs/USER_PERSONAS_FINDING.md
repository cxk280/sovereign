# User Personas — Findings & Remediation

App under test: the **sovereign operator dashboard** (`http://localhost:5173`, Vite dev
server + `dashboard_api` backend). Date: 2026-07-04. Read-only observability SPA, 5 views.

Pass 1 in progress. Personas driven one at a time in a real browser (Playwright/Chromium).

---

## Persona 8 — Raj Patel, Tech Lead (smart-user)
Goal: navigate all 5 views via sidebar; verify active state, deep links, back/forward. | Outcome: **achieved**

### Finding 8.1 — Silent pause on first sidebar click (no loading feedback)  [severity: nitpick]
- **Pass:** 1
- **Where:** sidebar nav → Registry / Leaderboard (first click after load)
- **Expected vs actual:** Expected instant SPA route swap or a visible loading affordance; actual ~560–760ms gap with no spinner/skeleton captured — a "did that register?" beat.
- **Repro:** 1) Load `/`. 2) Click Registry (or Leaderboard) in the sidebar. 3) Observe the pause before content settles.
- **Remediation:** _pending — evaluate after more personas (may reinforce the loading-feedback point)._
- **Status:** open

### Finding 8.2 — Deep-link full-load latency ~1.1–1.7s  [severity: nitpick]
- **Pass:** 1
- **Where:** direct load of `/leaderboard`, `/context`
- **Expected vs actual:** Likely Vite dev-server cold-compile, not a production bundle concern — flagged for completeness.
- **Remediation:** Declined — dev-server artifact, not a product issue (production is a static nginx-served bundle).
- **Status:** declined

_No bugs, no console errors. Routing, deep-linking, and history all correct; active nav tracks in lockstep._

---

## Persona 17 — Bethany Cole, keyboard-only user (dumb-user)
Goal: reach all 5 views using only the keyboard. | Outcome: **achieved**

### Finding 17.1 — Context "search box" looks like a text input but isn't focusable/typeable  [severity: minor]
- **Pass:** 1
- **Where:** `/context` → "Retrieval preview" panel, the rounded search box + magnifier + query text.
- **Expected vs actual:** It looks exactly like an editable search field (and the blue paths look like links); actual — it's a static `<div>`, not reachable by Tab, not typeable. A keyboard-only user assumes their keyboard is broken; everyone else is tempted to type.
- **Repro:** 1) Go to `/context`. 2) Tab through — focus skips the whole retrieval panel and loops back to the nav. 3) The box invites typing but nothing happens.
- **Remediation:** Fixed in `dashboard/src/views/Context.tsx` + `app.css` — the query is now a real `<input readOnly>` (keyboard-focusable, announced read-only, `aria-label`), with a `:focus-within` ring on the box, and a new caption ("A sample query … illustrative, read-only preview (not a live search in this build)") that sets expectations. Hint changed to "example · top N".
- **Status:** fixed

### Finding 17.2 — Focus disappears after the last sidebar item  [severity: nitpick]
- **Pass:** 1
- **Where:** after Tab past "Context".
- **Expected vs actual:** Focus visibly vanishes (goes to body) — feels like the keyboard stopped. Actual is expected: a read-only dashboard has no other focusable controls, so focus leaves the nav. Sidebar focus ring itself is clear and tab order is correct.
- **Remediation:** Declined as a defect (by-design for a read-only surface); partially improved by 17.1's fix adding a focusable element on `/context`.
- **Status:** declined

_Positives: clear focus ring on all 5 nav links, sensible tab order, Enter activates links correctly._

---

## Persona 18 — Dylan Reeves, colorblind / deuteranopia (dumb-user)
Goal: tell good/bad and distinguish chart series without relying on color. | Outcome: **achieved**

### Finding 18.1 — Leaderboard chart series distinguishable by color hue only  [severity: major]
- **Pass:** 1
- **Where:** `/leaderboard` "Pass rate by task" chart + legend.
- **Expected vs actual:** Legend was three dots differing only by hue; emerald (code-review) and amber (test-gen) bars read as the same brown to a deuteranope, with no tooltip and no per-bar series label. Info was recoverable only from the table below, not the chart.
- **Repro:** 1) `/leaderboard`. 2) Ignore the table. 3) Try to name which colored bar is "test-gen" from the chart alone.
- **Remediation:** Fixed in `dashboard/src/components/charts.tsx` + `Leaderboard.tsx` — added a **texture channel**: series cycle solid → diagonal-hatch → dots, applied to both the bars and the legend swatches, so the three series are distinguishable without color. Also added per-bar `<title>` tooltips ("code-review: 0.78") for hover/AT. Verified visually.
- **Status:** fixed

### Finding 18.2 — Stat-tile trend arrows need domain knowledge to read as good/bad  [severity: nitpick]
- **Pass:** 1 | **Where:** `/` stat tiles.
- **Note:** Uses ▲/▼ glyphs (shape, not color-only) so direction is always readable; whether "up" is good depends on the metric. Not color-only.
- **Remediation:** Declined — direction is shape-encoded; metric semantics are conventional (latency down = good). Not a color-accessibility defect.
- **Status:** declined

### Finding 18.3 — Could not observe a degraded/down state (static healthy data)  [severity: nitpick]
- **Pass:** 1 | **Where:** `/` READINESS rows.
- **Note:** Readiness renders the status word (`{status}`) as text, so a non-healthy state stays colorblind-safe by text; the demo data is always "healthy" so it couldn't be exercised.
- **Remediation:** Declined — status is text-rendered (not color-only); coverage gap of the static dataset, not a defect.
- **Status:** declined

_Positives: Overview health pill, READINESS words, ▲/▼ deltas, Registry active/candidate text pills, and Adoption by-surface text+% labels are all colorblind-safe._

---

## Persona 13 — Mrs. Alvarez, low-vision user at ~200% zoom (dumb-user)
Goal: read all 5 views comfortably at high zoom / narrow width. | Outcome: pass 1 **partially blocked** → **fixed**

### Finding 13.1 — Context retrieval panel collapses to a sliver; page grows to ~7500px  [severity: blocker]
- **Pass:** 1 | **Where:** `/context` at ≤720px — the two cards sat side-by-side; the "Retrieval preview" card squeezed to ~2–90px and file paths wrapped one character per line.
- **Remediation:** Fixed — `.row` now `flex-wrap: wrap` and side cards use `.side-card` (`flex: 1 1 300px`), so cards **stack** on narrow screens; `.result-path` uses `overflow-wrap: anywhere`. Verified: page height 1117px (was 3762–7524), no 1-char wrapping.
- **Status:** fixed

### Finding 13.2 — Overview/Adoption stat tiles crush & clip values; second card squeezed  [severity: blocker]
- **Pass:** 1 | **Where:** `/` and `/adoption` — 6-tile flex row refused to wrap ("680 ms" → "68C", "ERROR RATE" clipped); the chart card next to Backend/By-surface collapsed to a sliver.
- **Remediation:** Fixed — `.stat-row` is now `grid` with `repeat(auto-fit, minmax(150px, 1fr))` (tiles wrap to 2/3 columns), and the chart/side cards stack via the `.row` wrap. Verified: no page overflow at 720px, all values fully visible.
- **Status:** fixed

### Finding 13.3 — Leaderboard x-axis model labels overlap when narrow  [severity: minor/bug]
- **Pass:** 1 | **Where:** `/leaderboard` chart x-axis (~31px text overlap between model names).
- **Remediation:** Fixed — the chart has a `min-width: 600px` inside a `.chart-scroll` (`overflow-x: auto`) container, so on narrow screens it scrolls horizontally instead of colliding labels; desktop is unchanged.
- **Status:** fixed

### Finding 13.4 — Registry model names wrap mid-syllable + slight table overflow  [severity: minor]
- **Pass:** 1 | **Where:** `/registry` table + routing cards.
- **Remediation:** Fixed — tables are wrapped in `.table-wrap` (`overflow-x: auto`) with `white-space: nowrap` cells, so the table scrolls inside its card instead of wrapping names or overflowing the page.
- **Status:** fixed

### Finding 13.5 — Muted gray captions fail WCAG AA contrast (~2.45:1)  [severity: minor]
- **Pass:** 1 | **Where:** dashboard-wide — stat-tile labels, captions, axis ticks in `--text-muted` #94A3B8 on the near-white canvas.
- **Remediation:** Fixed — `--text-muted` darkened to slate-500 `#64748B` (~4.6:1 on the canvas, meets AA for normal text). The sidebar's on-dark muted token is separate and unaffected.
- **Status:** fixed

---

## Persona 14 — Chad Mueller, impatient mobile user / iPhone (dumb-user)
Goal: glance at the dashboard on a phone (390px portrait). | Outcome: pass 1 **blocked** → **fixed**

### Finding 14.1 — Fixed 240px sidebar never collapses on phone  [severity: blocker]
- **Pass:** 1 | **Where:** all views at 390px — the left rail ate ~224px of 390, leaving ~166px of content; no hamburger/collapse.
- **Remediation:** Fixed — added a `@media (max-width: 720px)` breakpoint: `.shell` stacks to a column and `.sidebar` becomes a horizontal top nav bar (wrapping nav pills, wordmark left, "PLATFORM" label hidden). Content is full-width beneath.
- **Status:** fixed

### Finding 14.2 — Whole page scrolls sideways on phone  [severity: blocker]
- **Pass:** 1 | **Where:** all views (content 516–559px in a 390px viewport).
- **Remediation:** Fixed as a consequence of 14.1 (sidebar off the horizontal axis) + the earlier row/grid reflow. Verified: all 5 views report "fits" (no sideways scroll) at 390px.
- **Status:** fixed

### Finding 14.3 — Text wraps letter-by-letter in squeezed columns  [severity: bug]
- **Pass:** 1 | **Where:** Registry routing / Leaderboard table / Context paths at ~150px content width.
- **Remediation:** Fixed — content now gets full width (14.1); tables scroll in `.table-wrap`, routing cards wrap (`.route-grid` flex-wrap), paths use `overflow-wrap: anywhere`.
- **Status:** fixed

### Finding 14.4 — Topbar title collides with the status pills  [severity: bug]
- **Pass:** 1 | **Where:** all views — 2-line titles overlapped the "Ollama · local" / health pills.
- **Remediation:** Fixed — mobile `.topbar` is `flex-wrap: wrap` with `height: auto`, so the title and pills stack instead of overlapping.
- **Status:** fixed

### Finding 14.5 — "Requests by day" chart renders blank in portrait  [severity: bug]
- **Pass:** 1 | **Where:** `/adoption` at narrow width — 30 bars with 6px gaps exceeded the container, yielding a negative bar width → blank SVG.
- **Remediation:** Fixed in `charts.tsx` `BarChart` — gap now `Math.max(1, Math.min(6, w/n/4))` and bar width clamped `≥1`, so it never blanks. Verified: chart renders at 390px.
- **Status:** fixed

_Landscape (844px) already worked; the fixes make portrait usable too._

---

## Persona 20 — "Guy Fieri Jr.", URL tinkerer (dumb-user)
Goal: type random/unknown URLs and get sane results. | Outcome: pass 1 **issues** → **fixed**

### Finding 20.1 — No 404 page; unknown routes silently render Overview  [severity: major]
- **Pass:** 1 | **Where:** `/admin`, `/login`, `/settings`, `/registryyy`, etc.
- **Expected vs actual:** A wrong URL quietly showed the Overview dashboard (HTTP 200, no nav highlighted, no signal) — a confused user gets no indication the route doesn't exist.
- **Remediation:** Fixed — added `dashboard/src/views/NotFound.tsx` (a styled 404 with a "Back to Overview" link) and pointed the `*` route at it (`App.tsx`). Verified: `/admin`, `/registryyy` → "404 · Page not found".
- **Status:** fixed

### Finding 20.2 — `/context/extra/deep` showed 404 content but kept "Context" highlighted  [severity: minor]
- **Pass:** 1 | **Where:** deep unknown path under a real prefix.
- **Expected vs actual:** Nav lied — the `/context` link matched the prefix and stayed active while the content was the fallback.
- **Remediation:** Fixed — every sidebar `NavLink` now uses `end` (exact match), so a deep unknown path activates no nav item. Verified: `/context/extra/deep` → 404, no active nav; `/context` still activates correctly.
- **Status:** fixed

### Finding 20.3 — `/api/overview` shows raw JSON; `/robots.txt` falls to the SPA  [severity: nitpick]
- **Pass:** 1 | **Where:** non-SPA paths.
- **Remediation:** Declined — `/api/*` returning JSON is correct (it's the API; in prod nginx proxies it), and a missing `robots.txt` on an internal, unindexed operator tool is immaterial. Not product-facing defects.
- **Status:** declined

_`/Leaderboard` (wrong case) correctly rendered Leaderboard — React Router matches case-insensitively; expected._
