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
- **Remediation:** _pending — make it an honest, focusable read-only affordance (real `<input readonly>` with the sample query)._
- **Status:** open

### Finding 17.2 — Focus disappears after the last sidebar item  [severity: nitpick]
- **Pass:** 1
- **Where:** after Tab past "Context".
- **Expected vs actual:** Focus visibly vanishes (goes to body) — feels like the keyboard stopped. Actual is expected: a read-only dashboard has no other focusable controls, so focus leaves the nav. Sidebar focus ring itself is clear and tab order is correct.
- **Remediation:** Declined as a defect (by-design for a read-only surface); partially improved by 17.1's fix adding a focusable element on `/context`.
- **Status:** declined

_Positives: clear focus ring on all 5 nav links, sensible tab order, Enter activates links correctly._
