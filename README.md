# مصروفاتي · Mina utgifter

Personal finance PWA (Arabic / Svenska / English). No server, no accounts, no AI: all data stays on the device (localStorage).

- `index.html` – the app (built from the v29 source by `tools/build.py`)
- `manifest.webmanifest`, `sw.js`, `icons/` – PWA (installable, works offline)
- `privacy.html` – privacy policy (also available inside the app at `#privacy`)
- `netlify.toml` – headers for Netlify

Deploy: connect this repo to Netlify (no build command, publish directory `/`), then import the Netlify URL in PWABuilder.
