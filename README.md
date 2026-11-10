# Pinnacle Financial Services — ACA Certification Hub

A standalone static resource hub that shows insurance agents where and how to complete
ACA/Marketplace agent & broker certification — Federal (FFM/CMS) and every State-Based Marketplace.

Plan Year 2027 · Built for Pinnacle Financial Services.

## Files
- `index.html` — the page
- `style.css` — styles (PFS brand: crimson #aa0e33, charcoal #2c2c2c, Roboto/Open Sans)
- `pre65/index.html` — Pre-65 ACA Strategy Guide for agents & brokers (early retirees, MAGI, 400% FPL cliff, HSA strategy, built-in cliff calculator)
- `script.js` — client-side state search/filter (vanilla JS, no dependencies)
- `assets/CMS-FFM-Registration-Guide-PY2027.pdf` — CMS returning-agent registration guide (linked from the Federal section)
- `assets/favicon.svg` — site icon

## Logo
The header loads the official Pinnacle logo from the company CDN. To make the site fully
self-contained, save that image as `assets/pinnacle-logo.png` and change the header `<img src>`
in `index.html` to `assets/pinnacle-logo.png` (an `onerror` fallback to the local path is already in place).

## Deploy on GitHub Pages
1. Push these files to the repository root (branch `main`).
2. Settings → Pages → Source: "Deploy from a branch" → Branch `main` / `/ (root)` → Save.
3. The site publishes at `https://<user>.github.io/<repo>/`.

`.nojekyll` is included so GitHub Pages serves all files as-is.

## Contact
Samuel Tripp · Sales Director – ACA · (800) 772-6881 x7721 · Samuel.Tripp@pfsinsurance.com
