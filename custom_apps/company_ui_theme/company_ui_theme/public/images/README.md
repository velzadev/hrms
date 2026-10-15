## Quicxly logo assets (temporary)

These files are **temporary, derived assets**, not production originals. They were cut from the
only logo supplied so far: a 1366×626 JPEG forwarded through WhatsApp
(`WhatsApp Image 2026-10-15 at 5.27.59 PM.jpeg`), which has a flat `#F7F7F7` background, no
transparency and visible JPEG compression.

| File | Made from | Used for |
| --- | --- | --- |
| `quicxly-mark-512.png` | The Q mark (421×420 px in the source), cropped; only the grey background outside its rounded square (radius ≈ 38 px) made transparent; resized | HRMS app tile, sidebar header, launcher top-left logo, loading splash |
| `quicxly-mark-192.png` | Same, 192 px | Spare size (app icon) |
| `quicxly-mark-64.png` / `quicxly-mark-32.png` | Same, 64 / 32 px | Favicon |
| `quicxly-logo-light.png` | Mark as above plus the "Quicxly™" wordmark, with the black ink separated from the grey background; original proportions (3.198:1) | Login page logo (light background only) |

Nothing inside the mark or the wordmark was redrawn or recoloured. There is no light/white
wordmark variant, so on dark surfaces only the mark is used.

**Replace these** with the official originals as soon as they are available (SVG, or PNG with a
transparent background; the full logo, a light variant for dark backgrounds, and the Q mark on
its own). Keep the file names, or update the paths in `boot.py`, then run
`bench build --app company_ui_theme` and hard-refresh (browsers cache favicons aggressively).
