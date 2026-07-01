# Assets

Static assets for the project README and docs.

The root `README.md` shows the logo through a theme-adaptive `<picture>` element:

- `synaptic-logo.png` — full-bleed neon-on-black wordmark. Served to
  **dark-mode** viewers, where the black field blends into the page.
- `synaptic-logo-light.png` — the same art with rounded corners (transparent
  outside the round), so on a **light-mode** white page it reads as an
  intentional dark card instead of a hard black box. This is the default
  `<img>` src.

Both are 1535x1024 so they render at the same size at `width="520"`.
