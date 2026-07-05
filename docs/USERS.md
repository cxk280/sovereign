# User Personas — sovereign operator dashboard

Twenty realistic users for black-box browser testing of the operator **dashboard**
(the only graphical UI in `sovereign`). The dashboard is a **read-only
observability surface** with five views — Overview, Model registry, Evaluation
leaderboard, Adoption & impact, Context browser — reached from a left sidebar. No
auth, no forms, no mutations.

Roster is balanced ~10 expert/technical (`smart-user`) and ~10 naive/careless
(`dumb-user`), varied across device, connection, patience, and accessibility.

| # | Name | Type | Agent | One-line goal |
|---|------|------|-------|---------------|
| 1 | Priya Nair | expert | smart-user | Confirm the platform is healthy right now |
| 2 | Marcus Bell | expert | smart-user | Find which model is the curated route for code-gen |
| 3 | Dana Whitfield | expert | smart-user | Read the eval leaderboard and identify the winner |
| 4 | Sol Ramírez | expert | smart-user | Check adoption trend and estimated hours saved |
| 5 | Aisha Okonkwo | expert | smart-user | See what internal sources are indexed for RAG |
| 6 | Tom Vasquez | expert | smart-user | Verify p50/p95 latency and error rate at a glance |
| 7 | Lena Fischer | expert | smart-user | Cross-check registry backend vs. leaderboard model |
| 8 | Raj Patel | expert | smart-user | Navigate all five views quickly via the sidebar |
| 9 | Grace Lim | expert | smart-user | Evaluate the retrieval preview quality |
| 10 | Otto Brandt | expert | smart-user | Assess whether numbers look real vs. placeholder |
| 11 | Barb Jensen | naive | dumb-user | "Is the thing working?" — just wants a green light |
| 12 | Kevin Doyle | naive | dumb-user | Clicks everything, expects buttons to do stuff |
| 13 | Mrs. Alvarez | naive | dumb-user | Low vision; needs large, high-contrast text |
| 14 | Chad Mueller | naive | dumb-user | On a phone, impatient, double-taps, rotates screen |
| 15 | Yuki Tanaka | naive | dumb-user | Non-native English reader; scans for meaning |
| 16 | Pop-pop Ray | naive | dumb-user | Not technical; confused by jargon (p95, quant, MCP) |
| 17 | Bethany Cole | naive | dumb-user | Keyboard-only (mouse broken); tabs through the app |
| 18 | Dylan Reeves | naive | dumb-user | Colorblind (deuteranopia); reads status by color |
| 19 | Nina Popov | naive | dumb-user | Slow 3G; refreshes when it "looks stuck" |
| 20 | Guy Fieri Jr. | naive | dumb-user | Types random URLs like /admin, /login, /settings |

---

## Expert / technical (smart-user)

### 1 — Priya Nair, Staff SRE
- **Device/conn:** 27" 4K, wired. Chrome.
- **Mindset:** On-call; wants a single-glance health verdict.
- **Goal:** Land on Overview and decide in <10s whether the platform is healthy.
- **Quirks:** Reads the health pill + readiness rows first; distrusts vague "OK".

### 2 — Marcus Bell, AI Platform Engineer
- **Device/conn:** MacBook, fast wifi.
- **Mindset:** Owns model routing; wants the curated model per task.
- **Goal:** On Registry, determine which model code-gen routes to and why.
- **Quirks:** Expects routing to be explicit and to match the leaderboard winner.

### 3 — Dana Whitfield, ML Evaluation Lead
- **Device/conn:** Linux desktop, dual monitor.
- **Goal:** On Leaderboard, identify the top model and read exact pass rates.
- **Quirks:** Checks that the chart and the ranked table agree.

### 4 — Sol Ramírez, DevEx Manager
- **Device/conn:** Laptop.
- **Goal:** On Adoption, read the 30-day trend, acceptance rate, and hours saved.
- **Quirks:** Wants the by-surface split (IDE/CI/CLI) to sum sensibly.

### 5 — Aisha Okonkwo, Knowledge/RAG Engineer
- **Goal:** On Context, see which source types are indexed and their doc counts.
- **Quirks:** Sanity-checks that retrieval hits cite real-looking paths.

### 6 — Tom Vasquez, Reliability Engineer
- **Goal:** Read p50/p95 latency, tokens/sec, and error rate on Overview.
- **Quirks:** Cares that trend arrows point the sensible direction (lower latency = good).

### 7 — Lena Fischer, Senior Backend Eng
- **Goal:** Cross-check that the registry's active model matches the leaderboard note.
- **Quirks:** Notices the 1.5b (deployed) vs 7b (eval winner) distinction.

### 8 — Raj Patel, Tech Lead
- **Goal:** Move through all five views quickly; confirm nav highlights the current view.
- **Quirks:** Uses back/forward buttons; expects deep links to work.

### 9 — Grace Lim, Applied Scientist
- **Goal:** Judge the retrieval-preview result quality on Context.
- **Quirks:** Reads snippets and scores; expects descending relevance.

### 10 — Otto Brandt, Skeptical Architect
- **Goal:** Decide if the dashboard shows real data or placeholders.
- **Quirks:** Looks for "illustrative" honesty; pokes at every number.

## Naive / careless (dumb-user)

### 11 — Barb Jensen, Office Manager
- **Device:** Old Windows laptop, Edge.
- **Goal:** Wants to see "everything is fine" without reading jargon.
- **Quirks:** Looks only for green/red; ignores numbers.

### 12 — Kevin Doyle, Intern
- **Goal:** Clicks every element expecting something to happen.
- **Quirks:** Impatient; assumes cards/rows are buttons.

### 13 — Mrs. Alvarez, Low-vision user
- **Device:** Laptop at 150% browser zoom.
- **Goal:** Read the page with large text and strong contrast.
- **Quirks:** Zooms in; complains if text is tiny/low-contrast or layout breaks.

### 14 — Chad Mueller, Sales, on a phone
- **Device:** iPhone, Safari, portrait then landscape.
- **Goal:** Glance at the dashboard on mobile.
- **Quirks:** Double-taps, rotates, expects it to fit the small screen.

### 15 — Yuki Tanaka, Non-native English reader
- **Goal:** Understand what each view is for by scanning.
- **Quirks:** Relies on labels/icons; trips on idioms and abbreviations.

### 16 — Pop-pop Ray, Non-technical visitor
- **Goal:** Figure out "what is this?" with no jargon knowledge.
- **Quirks:** Confused by p95, quant, MCP, tokens/sec.

### 17 — Bethany Cole, Keyboard-only user
- **Device:** Laptop, broken trackpad.
- **Goal:** Reach all five views using only Tab/Enter.
- **Quirks:** Needs visible focus and keyboard-operable nav.

### 18 — Dylan Reeves, Colorblind user (deuteranopia)
- **Goal:** Tell healthy vs. problem states without distinguishing red/green.
- **Quirks:** Relies on text/shape, not just color, for status.

### 19 — Nina Popov, Slow connection
- **Device:** Laptop throttled to slow 3G.
- **Goal:** Load the dashboard and read it despite slowness.
- **Quirks:** Refreshes when a page looks blank/stuck; hates silent loading.

### 20 — "Guy Fieri Jr.", URL tinkerer
- **Goal:** Pokes at random routes (/admin, /login, /settings, /registryyy).
- **Quirks:** Expects a sane result (not a blank screen) for unknown URLs.
