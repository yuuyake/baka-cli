# baka-cli

Watch anime from your terminal. Like [ani-cli](https://github.com/pystardust/ani-cli), but with multiple providers, automatic fallback, tracker sync and Discord presence.

Works on Arch Linux, Debian, Ubuntu and macOS.

## Features

- **Multiple providers**: animepahe (default), hianime, allanime (experimental)
- **Automatic fallback**: if a provider fails, the others are tried before you see an error
- **Tracker sync**: AniList, MyAnimeList and Kitsu update after every episode
- **Continue watching**: offers to resume from your last watched episode
- **Discord Rich Presence**: show what you are watching
- **Pretty terminal**: panels, spinners and fzf menus
- **Sub or dub**, quality selection, subtitles when the provider has them
- **Self-diagnosing**: `baka-cli --doctor` tests every provider
- **Self-updating**: `baka-cli --upgrade`

## Install

```
git clone https://github.com/7yxz/baka-cli
cd baka-cli
bash install.sh
```

The script installs python, pipx, mpv and fzf with pacman, apt or brew, then installs baka-cli with pipx. Check it with `baka-cli -v`.

Manual install: `pipx install .` (needs mpv, fzf is optional).

## Usage

```
baka-cli naruto
baka-cli -p hianime one piece
baka-cli -a -q 720 frieren
baka-cli -e 5 -d bleach
baka-cli -help
```

Controls after each episode: `n` next (default, just press Enter), `p` previous, `r` replay, `f` refresh (clears the terminal and reloads the video from a different source), `s` select episode, `q` quit.

| Flag | Meaning |
|------|---------|
| `-p, --provider` | animepahe (default), hianime, allanime |
| `-a, --all` | search animepahe and hianime together |
| `-d, --dub` | dubbed audio |
| `-q, --quality` | preferred quality, default 1080 |
| `-e, --episode` | start at this episode number |
| `--login / --logout TRACKER` | anilist, mal or kitsu |
| `--status` | show tracker login status |
| `--no-sync` | skip tracker updates for this run |
| `--remap` | re-pick the tracker match for this anime |
| `--rpc-setup` / `--no-rpc` | set up or disable Discord presence |
| `--config` | customize settings on a full-screen page |
| `--sub` | force subbed audio (overrides a dub default) |
| `--doctor` | test every provider |
| `-D, --discord` | open the baka-cli Discord server |
| `--upgrade` | update to the latest version |
| `-v, --version` | show version |

## Providers

| Provider | Notes |
|----------|-------|
| animepahe | Default. Finds a working mirror and handles cookies by itself. Often behind Cloudflare, so it may fail. |
| hianime | Direct scraping, no server needed. Uses `curl_cffi` to look like Chrome. |
| allanime | Experimental, use with `-p allanime`. Uses rotating keys published by anipy-cli. |

If the provider you choose fails, baka-cli tries the others and only shows an error when all of them fail. Working mirrors are remembered in the config.

## Tracker sync

Log in once, then progress updates automatically after you watch 80% of an episode (change it with `BAKA_SYNC_PCT`).

```
baka-cli --login anilist
baka-cli --login mal
baka-cli --login kitsu
baka-cli --status
```

| Tracker | What you need |
|---------|---------------|
| AniList | An app from anilist.co/settings/developer with redirect `https://anilist.co/api/v2/oauth/pin`. Paste the token it shows, or use `--token`. |
| MAL | An app from myanimelist.net/apiconfig, type other, redirect `http://localhost:8765/callback`. Login opens your browser. |
| Kitsu | Email and password, only used once to get a token. |

Progress only moves forward, and the last episode marks the entry completed. Percent tracking needs mpv. Tokens are stored in `~/.config/baka-cli/config.json` (chmod 600).

## Customize

You can also pick the command name there (`command`): `baka-cli`, `b-cli`, `baka` or `bcli`. It adds a small link next to the installed command, and `baka-cli` keeps working too.

`baka-cli --config` opens a settings page: default provider, quality, dub, sync threshold, Discord presence, the info page and more. Choose a setting to toggle or change it. You can also press `c` on the info page between episodes. Command line flags always win over saved settings.

After each episode a full-screen info page shows the anime's details from AniList (score, genres, studio, synopsis) and your progress, with the controls.

## Discord Rich Presence

```
baka-cli --rpc-setup
```

Paste a Discord application ID from discord.com/developers/applications. While you watch, Discord shows "Watching" with the anime's AniList cover, title, episode out of total, time left, score and genres, and a button to its AniList page (all fetched automatically, no login needed). The Discord desktop app must be running. For a logo, upload an image named `baka-cli` under Rich Presence, then Art Assets.

## Upgrade and uninstall

```
baka-cli --upgrade      # latest version from GitHub
pipx uninstall baka-cli # remove
rm -rf ~/.config/baka-cli  # remove saved logins and settings
```

## Troubleshooting

- **animepahe says no working mirror**: it is behind a Cloudflare browser check. Open animepahe in your browser, copy the `cf_clearance` cookie value from the dev tools (Application, Cookies) and run `export PAHE_COOKIE="cf_clearance=VALUE"`. It can expire, and it may not work if your browser differs from the one baka-cli imitates. hianime is usually the easier choice.
- **allanime says keys are stale**: its API rotates keys that anipy-cli publishes. When that file is outdated allanime stops working until it is updated.
- **Video window is blank or frozen**: press `f` on the info page. It clears the terminal and reloads the episode from the next source. If it keeps happening, open `baka-cli --config` and set `mpv_args` to something like `--hwdec=no` or `--vo=gpu`.
- **Everything fails**: run `baka-cli --doctor` and look at which step breaks for each provider.
- **Cloudflare blocks**: make sure `curl_cffi` is installed (`pipx inject baka-cli curl_cffi`). Providers change often, so a different one may work better today.
- **Old version after updating**: run `which -a baka-cli` and delete any copy that is not the pipx one.
- **`./install.sh` not executable**: run it with `bash install.sh`.
- **Wrong tracker match**: run again with `--remap`.

## Environment variables

All optional: `PAHE_URL`, `PAHE_COOKIE`, `HIANIME_URL`, `BAKA_PLAYER` (default mpv), `BAKA_SYNC_PCT`, `DISCORD_CLIENT_ID`, `BAKA_NO_UPDATE_CHECK`.

## Adding a provider

Create a class in `baka_cli/providers/` with these methods, then register it in `providers/__init__.py`:

```python
class MySite:
    name = "mysite"
    in_all = True
    def search(self, q): ...                          # -> [(title, id)]
    def episodes(self, id): ...                       # -> [("Episode 1", ep_id)]
    def stream(self, id, ep_id, quality, dub=False):  # -> (url, headers, subtitle_or_None)
        ...
```

## Community

Questions, bug reports or just want to hang out? Join the Discord: https://discord.gg/U953H5hmPG (or run `baka-cli --discord`).

## Credits and license

hianime logic is ported from [ani-cli](https://github.com/pystardust/ani-cli) and allanime logic from [anipy-cli](https://github.com/sdaqo/anipy-cli). Both are GPL-3.0, so baka-cli is GPL-3.0 too (see `LICENSE`).

## Disclaimer

baka-cli does not host or store any video. It only fetches links from third-party sites. You are responsible for how you use it and for following the laws where you live. Please support the official releases.
