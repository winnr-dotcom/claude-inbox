---
name: launch-qa
description: Launch QA with 5 first-time-user personas (impatient, skeptic, mobile 375px on slow 3G, non-native English, breaker). Each walks a given URL from landing page to first success in a real browser (Playwright) and reports confusion points. Report-only: never fixes code. Use when asked to "launch QA", "first-user test" or "walk the app as new users".
argument-hint: <url> [--rerun <previous-report.md>]
---

# /launch-qa <url>

Report-only launch QA. Never edit code, never auto-fix. Output is a ranked findings report.

## Guardrails
- Target is the single URL passed in. If none is given, ask; do not guess.
- Prefer staging/preview. If the host looks like production (winnr.lovable.app, vaulteva.lovable.app, fundarem.com), stop and ask Bo to confirm in this session before any run.
- Never submit real payment, real personal data, or credentials. Sign-ups use clearly fake data (qa+<persona>@example.com). Stop a persona at the first step that needs money, a real email/SMS code, or an irreversible action, and record it as "blocked by design".
- The breaker persona sends junk only through normal UI fields (long strings, emoji, script-looking text, empty submits, double-clicks, back/refresh mid-flow). No scanning, fuzzing tools or load.
- Do not change other repos. Do not echo secrets.

## Method
1. Define "first success" for the app in one line (e.g. account created and first core action done). If unclear from the landing page, state the assumption in the report.
2. Spawn 5 subagents in parallel, each with a fresh context, Playwright (chromium, headless), and only: the URL, the first-success line, and its persona brief. Each saves screenshots to `launch-qa/<persona>/NN-<slug>.png` and returns a list of moments of confusion, getting stuck or annoyance, each with: step, what it saw, what it expected, severity (blocker / major / minor), screenshot path, console errors/failed requests at that moment.
   1. **Impatient**: skims, clicks the first prominent button, gives up at the first error or after ~3 unclear steps.
   2. **Skeptic**: before signing up, reads pricing, terms, privacy; flags missing/broken/vague legal pages, hidden costs, unclear data use, no contact info.
   3. **Mobile**: viewport 375x812, touch emulation, throttle to slow 3G via CDP (`Network.emulateNetworkConditions`, ~400 kbps down, 400 ms latency). Flags horizontal scroll, tiny tap targets (<44px), overlapping elements, slow first paint (>3 s), layout shift.
   4. **Non-native English**: follows only the literal UI text; no inference from context or domain jargon. Flags idioms, jargon, ambiguous buttons, error messages that don't say what to do.
   5. **Breaker**: junk into every field, empty submits, double-clicks on every submit, back/forward/refresh mid-flow, opening flow in two tabs. Flags unhandled errors, duplicate submissions, lost state, stack traces or raw errors shown to the user.
3. Merge in the orchestrating session: dedupe by root cause, count how many personas hit each issue, rank by (personas hit, then max severity). Keep the per-persona evidence links.
4. Write the report to `launch-qa/report-<date>.md`:
   - Verdict line (can a new user reach first success? which personas failed to).
   - Ranked table: #, issue, personas hit (n/5), severity, step, screenshot.
   - "Blocked by design" list.
   - Suggested fix per issue as a one-line suggestion only.
5. Report to Bo: plain English first, top 5 issues, report path. Stop. Do not fix.

## Rerun (after Bo or a builder has fixed things)
`/launch-qa <url> --rerun launch-qa/report-<date>.md`: repeat step 2 with the same personas, then add a column to the report showing each earlier issue as fixed / still there / new. Judge by the screenshots, not by claims.

## Running it
One-time: Playwright available (`npx playwright install chromium`) and the skill copied to `~/.claude/skills/launch-qa/SKILL.md`.
```
/launch-qa https://<staging-or-preview-url>
```
For Winnr, Vaulteva or Fundarem, use a Lovable preview/staging URL where one exists. Running against the live hosts (winnr.lovable.app, vaulteva.lovable.app, fundarem.com) needs Bo's explicit go-ahead in the session, and sign-up flows will create fake accounts there.

## Cost
Five parallel browser agents; expect a few hundred K tokens per run, more with many screenshots. Use a smaller model for the personas and a stronger one for the merge if cost matters.
