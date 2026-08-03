# Setting up the live terminal

`terminal/index.html` is a self-contained, no-build-step terminal emulator.
Visiting it and typing `whoami` (or `help`, `about`, `skills`, `projects`,
`certs`, `contact`, `socials`, `clear`, `banner`) prints real info about you
— no backend, it's a lookup table of commands in plain JavaScript.

To make the **⚡ Live Terminal** badge in the README actually go somewhere,
host the page with GitHub Pages. Two ways to do it:

## Option A — a dedicated site repo (matches the badge URL as-is)
1. Create a new **public** repo named exactly `TharaniDharan10.github.io`.
2. Put `terminal/index.html` at the **root** of that repo, renamed to `index.html`.
3. Push. GitHub serves it automatically at `https://TharaniDharan10.github.io`
   — no Pages setup needed, that repo name is special-cased by GitHub.

## Option B — serve it from this same profile repo
1. Keep `terminal/index.html` where it is in this repo.
2. Repo → **Settings → Pages → Source** → deploy from branch `main`, folder `/ (root)` or `/terminal` if supported.
3. Your URL will be `https://TharaniDharan10.github.io/TharaniDharan10/terminal/`
   instead of the clean root URL — update the badge link in `README.md` to match.

Either way, no server, database, or API key is required — it's static HTML/CSS/JS.

## Customizing
All the copy the terminal prints lives in the `commands` object near the top
of the `<script>` tag in `index.html` — edit the strings there (e.g. add a
`blog` command, tweak `whoami`, add an easter egg) and refresh.
