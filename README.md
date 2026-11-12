**[Download the Latest Release Here](https://github.com/Rag-isnt-fluffy/Rags-Webscraper/releases/tag/V2.5)**
The following is a copy of the latest release's README.md found above ^.

# Rags-Webscraper
V.2.5.0 (Yep I've skiped again)

> I've tried to leave comments where I can, sorry if they're incorrect (or there are spelling errors)

A Python web crawler that collects titles, headings, summaries, categories and the links between pages, with local (JSONL) or Firebase Firestore storage. It has **modes** for different kinds of sites (Wikipedia/wikis, news sites, Tor `.onion` sites, or any generic site), can be **stopped and resumed**, **retries failures with backoff**, and comes with a **command line search tool** and a **test suite**. Works on Windows, macOS and Linux.

This is a personal project I'm using to pratise Python, experiment with web scraping, learn how to format & label code and learn how to organise and store collected data.

## Features
- **Modes** — `wiki`, `news`, `onion` and `generic`, each with its own URL rules and extraction.
- **Resumable** — the queue and visited URLs are saved after every page; rerun the same command to continue.
- **Reliable** — retries with exponential backoff, honours `Retry After`, logs failures, prints a final summary.
- **Richer records** — intro summary, categories, outgoing links, plus mode specific details.
- **Search** — `search.py` searches `results.jsonl` by text, title, heading, category, backlinks and similarity.
- **Configurable** — output file, page limit, crawl depth, delay, retries, domains, and more (see [Options](#options)).
- **Polite by default** — respects `robots.txt` (except onion mode), identifies itself, waits between requests.
- **Tested** — 100+ tests using saved sample HTML; no live requests.

## Setup
Requires Python 3.9+.

**macOS / Linux**
```bash
git clone https://github.com/Rag-isnt-fluffy/Rags-Webscraper.git
cd Rags-Webscraper
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
**Windows (PowerShell)**
```powershell
git clone https://github.com/Rag-isnt-fluffy/Rags-Webscraper.git
cd Rags-Webscraper
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

(Use `python3` on macOS and `py` or `python` on Windows. Inside an activated virtual environment, plain `python` works everywhere. Examples below use `python`.) Edit `USER_AGENT` in `config.py` before crawling real sites. Include contact details so site administrators can reach you.

## Quick start
```bash
python Webcrawler.py                                   #wiki mode, starting at Wikipedia's Main Page
python Webcrawler.py --max-pages 50 --max-depth 2      #a small crawl
python search.py "web scraping"                        #search what you collected
```

Press **Ctrl+C** at any time. Progress is saved; run the same command again to carry on.

## Modes

Pick one with `--mode`. The starting URL is changeable with `--start` (repeatable) or `--seeds FILE`.
| Mode | Follows | Extracts (in `details`) |
|---|---|---|
| `wiki` (default) | article links inside the page body of one wiki (skips `Talk:`, `File:`, `Category:`, edit/history URLs...) | article title, infobox fields, reference count, external link count, last edited, Wikidata ID, disambiguation flag |
| `news` | links on the same site (subdomains included), skipping images, feeds, AMP... | is-article flag, authors, publish/modified dates, publisher, language, canonical URL, word count, keywords, **related-story links**, **political-lean heuristic**, login pages |
| `onion` | any `.onion` link (or only the start site with `--stay-on-site`), over Tor | other `.onion` hosts linked, v2/v3 address, contact emails, PGP key present, clearnet link count, rough site type (forum, marketplace, link directory...), login pages |
| `generic` | links on the starting domain (plus `--allow-domain`) | meta description, keywords, login pages |

```bash
#wikipedia (or any MediaWiki site)
python Webcrawler.py --mode wiki --start https://en.wikipedia.org/wiki/Web_scraping --max-depth 2
python Webcrawler.py --mode wiki --start https://fr.wikipedia.org/wiki/Python_(langage)

#news: needs a start URL tag articles with your own source ratings if you like
python Webcrawler.py --mode news --start https://www.example-news.com --max-pages 200 --output news.jsonl
python Webcrawler.py --mode news --start https://www.example-news.com --source-ratings ratings.json

#any site
python Webcrawler.py --mode generic --start https://example.com --allow-domain cdn.example.com

#onion (needs Tor running, see below)
python Webcrawler.py --mode onion --start http://<56-character-address>.onion --max-depth 2 --output onion.jsonl
python Webcrawler.py --mode onion --seeds onion_seeds.txt --stay-on-site
```

Every mode also records every page's `links`, `summary`, `categories` and, where a page contains a password form, a `login` entry (see [Login pages](#login-pages)).

### Onion mode and Tor

Onion mode sends all traffic through a local Tor SOCKS proxy and finds it automatically (port 9050, then 9150). It does not default to a start page: pass an `.onion` address you chose.

- **macOS:** `brew install tor && brew services start tor`, or just open Tor Browser and leave it running.
- **Windows:** open Tor Browser and leave it running, or run the Tor Expert Bundle.
- Custom setup: `--proxy socks5h://HOST:PORT`.

It uses a generic browser User Agent (not your contact string), never fetches images or files, and stores only metadata (title, headings, summary, links), not page bodies. Crawl responsibly and within the law where you live.

### Political lean (news mode)

`details.political` is a **crude keyword heuristic**: it counts left- and right-coded phrases (lists are in `analysis.py`; edit them) and reports `lean`, `score` (-1 to +1), the hit counts and `confidence: "low"`. It measures vocabulary, not accuracy or bias. It is US-centric, and an article quoting both sides will look "mixed". Articles with fewer than 3 hits are labelled `unknown`. For something sturdier, supply your own ratings:

```json
{"example-news.com": "center", "another-paper.org": "left"}
```
and pass `--source-ratings ratings.json`; the matching label appears as `details.political.source_rating`.

### Login pages

all modes except `wiki` passively **detect** login and registration forms (any `<form>` with a password field, including whether it looks like a registration form or has a CAPTCHA) and links whose URL looks like a login page (`/login`, `/signin`, `/wp-login.php`...). They are recorded in `details.login` / `details.login_links` and the pages are crawled like any other. The crawler never submits a form, never logs in and never guesses credentials. Find them later with `python search.py --login`.

## Options
Run `python Webcrawler.py --help` for the full list.
| Option | Default | Description |
|---|---|---|
| `--mode {wiki,news,onion,generic}` | `wiki` | What kind of site to crawl |
| `--start URL` (alias `--start-url`) | Wikipedia Main Page in wiki mode; required otherwise | Starting URL; repeat for several |
| `--seeds FILE` | | Text file, one start URL per line (`#` comments allowed) |
| `--allow-domain DOMAIN` | | Also follow links to this domain (repeatable) |
| `--stay-on-site` | off | Onion mode: don't follow links to other `.onion` sites |
| `--source-ratings FILE` | | News mode: JSON `{"domain": "label"}` of your own source ratings |
| `--max-pages N` | `1000` | Stop after N stored pages **in total, including earlier runs** |
| `--max-depth N` | unlimited | Link hops from the start URL(s). `0` = start pages only |
| `--delay SECONDS` | `1.0` (`2.0` onion) | Pause between requests |
| `--timeout SECONDS` | `10` (`45` onion) | Per-request timeout |
| `--retries N` | `3` | Retries per URL on timeouts, connection errors, 429 and 5xx |
| `--retry-failed` | off | Put URLs that failed in earlier runs back in the queue |
| `--ignore-robots` | off | Skip the `robots.txt` check (onion mode never checks) |
| `--output FILE` | `results.jsonl` | Results file (JSON Lines) |
| `--state-file FILE` | `<output>.state.db` | Resume state |
| `--fresh` | off | Discard saved state and start over (results are appended to the output file) |
| `--log-file FILE` | `crawl.log` | Log file (`""` to disable) |
| `--firebase-key FILE` | | Store in Firestore instead of a file |
| `--proxy URL` | | Proxy; onion mode auto-detects local Tor |
| `--user-agent TEXT` | from `config.py` | Override the User-Agent |
| `--quiet` | off | One line per page |

Defaults live in `config.py`.

## Resuming

The queue and every visited URL are stored in a small SQLite file next to your output (`results.state.db` for `results.jsonl`). Every page is saved to the results file first, then marked done in one transaction, so stopping at any moment (Ctrl+C, closed laptop, crash) is safe.

```bash
python Webcrawler.py --max-pages 100     # stops at 100
python Webcrawler.py --max-pages 300     # carries on to 300 total
```

- A URL that was in flight when the crawl stopped is simply fetched again.
- Resuming a state file created with a different `--mode` is refused; use `--fresh` or a different `--output`.
- If you delete the results file but keep the state file, the crawler warns you, because those pages will not be re-crawled.
- In the unlikely event of a crash between writing a record and marking it done, that page can appear twice in the results; `search.py` keeps the latest record per URL.

## Reliability

- **Retries:** timeouts, connection errors, `408/425/429/500/502/503/504` are retried up to `--retries` times, waiting 1s, 2s, 4s... (with jitter, capped at 60s). A `Retry-After` header is honoured. `404`, `403`, bad certificates and invalid URLs are not retried.
- **Failures are recorded:** each failed URL is logged (`crawl.log`), kept in the state file with its error and attempt count, and listed in the final summary.
- **Skips:** non-HTML responses and `robots.txt`-blocked URLs are skipped and counted.
- **Parsing problems** on one page never stop the crawl.
- **Pages are capped** at 5 MB.

Example summary:

```
=======================================================
CRAWL SUMMARY
=======================================================
Mode:         news
This run:     48 succeeded, 2 failed, 1 skipped, 5 retries
Whole crawl:  148 done, 2 failed, 1 skipped, 5230 still queued
Elapsed:      00:02:31 (0.32 pages/s)
Stopped:      page limit reached (50)
...
Failed URLs (2):
  - https://example.com/broken
      HTTP 503 (after 4 attempts)
```

## Data storage

Each line of `results.jsonl` is one page:

| Field | Meaning |
|---|---|
| `page_number`, `url`, `title`, `headings`, `heading_count`, `scraped_at` | as before |
| `summary` | introductory summary (wiki: the lead section; others: meta description or first paragraph) |
| `categories` | wiki categories; news sections/tags; meta keywords |
| `links`, `link_count` | outgoing links that passed the mode's filter (first 500 stored; `link_count` is the true number) |
| `mode`, `depth` | which mode produced it, and how many hops from the start |
| `details` | mode-specific fields from the table above |

Older records without the new fields still load and search fine.

With `--firebase-key`, records go to the `pages` collection instead (see below). Note that the crawler flushes to Firestore after every page (rather than in batches of 20) so the resume state can never be ahead of the stored data, and `search.py` only reads the JSONL file.

## Searching

```bash
python search.py "web scraping"                         # all words must match (title ranks highest)
python search.py --title python                         # title contains
python search.py --heading history --category language  # filters combine with each other and with text
python search.py crawler --limit 5 --json               # machine-readable output
python search.py --links-to Web_crawler                 # pages that link to this one (title or full URL)
python search.py --similar Web_scraping                 # pages with similar content
python search.py --mode news --articles-only --lean right-leaning
python search.py --mode onion --login                   # pages with login forms
python search.py --file news.jsonl "budget"             # a different results file
```

Text search matches word prefixes, ignores case, and looks at title, headings, categories, keywords, summary and URL. Exit code is `0` with results, `1` with none.

## Tests
```bash
pip install -r requirements-dev.txt
python -m pytest
```
The tests cover URL filtering, link extraction, parsing for every mode (using saved HTML in `tests/fixtures/`), storage, resume state, retry/backoff, robots.txt, the crawl loop (including interrupt-and-resume) and the search tool. HTTP is replaced by a fake session, so they never touch the network.

## Adding a mode
Subclass `Mode` in `modes.py`, override what you need (`should_skip_url`/`skip_path`, `extract_summary`, `extract_links`, `extract_details`...), and add it to `MODES`. It then shows up in `--mode`.

## Firebase setup
1. Open the [Firebase Console](https://console.firebase.google.com/) and create a project.
2. Navigate to **Build → Firestore Database** and create a database.
3. Open **Project settings → Service accounts** and generate a new private key.
4. Save the downloaded JSON key as `serviceAccount.json` in the project directory (it is in `.gitignore`; never commit it).
5. Run the crawler with the Firebase key argument:
   ```bash
   python Webcrawler.py --firebase-key serviceAccount.json
   ```
6. Check the `pages` collection in Firestore to view the stored records.

## Project layout

| File | Purpose |
|---|---|
| `Webcrawler.py` | Command line entry point |
| `crawler.py` | Fetching with retries, robots.txt, the crawl loop and summary |
| `modes.py` | Wiki / news / onion / generic URL rules and extraction |
| `analysis.py` | Keyword, political-lean, login-form and page-type helpers |
| `state.py` | SQLite queue and visited-URL state for resuming |
| `storage.py` | JSONL and Firestore storage, record format |
| `search.py` | Search tool |
| `config.py` | Defaults |
| `tests/` | Test suite and sample HTML |

## Future plans
- Per domain rate limits and parallel fetching.
- A small web interface for searching collected data.
- A better classifier than the keyword heuristics.
- Export of the link graph (for Gephi or networkx).

## Disclaimer
This is a personal learning project. Respect each site's terms and `robots.txt`, use reasonable delays (Wikipedia asks for polite crawling), and follow the laws that apply to you. Onion mode is for research and discovery; the crawler only reads public pages, never logs in, and never fetches files or images. I have tried to outline as much as possible in this page.

---

*Rags-Webscraper — a work in progress.*
 _____              _____  _   _____
|  __ \     /\     / ____|( ) / ____|
| |__) |   /  \   | |  __ |/ | (___
|  _  /   / /\ \  | | |_ |    \___ \
| | \ \  / ____ \ | |__| |    ____) |
|_|  \_\/_/    \_\ \_____|   |_____/

__          __ ______  ____     _____  _____            __          __ _       ______  _____
\ \        / /|  ____||  _ \   / ____||  __ \     /\    \ \        / /| |     |  ____||  __ \
 \ \  /\  / / | |__   | |_) | | |     | |__) |   /  \    \ \  /\  / / | |     | |__   | |__) |
  \ \/  \/ /  |  __|  |  _ <  | |     |  _  /   / /\ \    \ \/  \/ /  | |     |  __|  |  _  /
   \  /\  /   | |____ | |_) | | |____ | | \ \  / ____ \    \  /\  /   | |____ | |____ | | \ \
    \/  \/    |______||____/   \_____||_|  \_\/_/    \_\    \/  \/    |______||______||_|  \_\ (Version 2.5.0)

