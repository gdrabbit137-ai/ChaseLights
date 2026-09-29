# B149 — Mobile Administrative-Area Production Smoke

## Goal

Close the gap between B143 branch-level Browser Smoke and the actual deployed ChaseLights homepage.

The production smoke verifies the mobile administrative-area bottom sheet on \`https://chaselights.app/index.html\` using a 390×844 emulated phone viewport.

## Deployment freshness

Before Selenium runs, CI downloads the deployed:

- \`index.html\`
- \`assets/app.js\`
- \`assets/app.css\`

and requires their SHA-256 values to match the current \`main\` checkout exactly.

This prevents a passing browser test against stale GitHub Pages bytes.

## Browser contract

The deployed smoke verifies:

1. the homepage loads forecast data;
2. the \`<=640px\` mobile picker mode is active;
3. tapping the area trigger opens and scroll-locks the bottom sheet;
4. dialog and \`aria-modal\` semantics are present;
5. the sheet remains below the viewport height;
6. backdrop, search, close, and Done controls are present;
7. selecting Hualien immediately updates the filter and keeps the sheet open;
8. the selected area exposes \`aria-pressed=true\`;
9. Done closes the sheet;
10. background scroll position is restored;
11. a screenshot artifact is retained for visual inspection.

## Trigger

- Pull requests changing the B148 smoke files run the static contract only.
- Pushes to \`main\` changing homepage assets or the smoke itself run the deployed production smoke.
- Manual workflow dispatch remains available.
