# Rags-Webscraper

A Python based Wikipedia crawler that collects article titles, URLs, and H2 headings, with support for local storage and Firebase Firestore. This is a personal project I'm using to practise Python, experiment with web scraping, and learn how to organise and store collected data. I might also use it as a testing ground for future web projects.

## Features

- **Wikipedia crawling** — visits Wikipedia pages and discovers links to other articles.
- **Page data extraction** — records article titles, URLs, and H2 headings.
- **Local storage** — saves scraped results to a JSONL file.
- **Firebase integration** — optionally stores results in a Firestore database.
- **Configurable crawling** — adjust the page limit, request delay, and starting URL through command line arguments.
- **URL filtering** — skips unwanted Wikipedia pages to keep the crawler focused on relevant content.

## Setup

Clone the repository and install the required dependencies:
```bash
git clone https://github.com/Rag-isnt-fluffy/Rags-Webscraper.git
cd Rags-Webscraper
pip install -r requirements.txt
```
Edit `USER_AGENT` in `config.py` before running the crawler. Please include appropriate contact details so website administrators can identify the crawler's operator if necessary.

## Running the crawler
Start crawling with the default settings:

```bash
python Webcrawler.py
```
Limit the crawl to 50 pages and wait 2 seconds between requests:
```bash
python Webcrawler.py --max-pages 50 --delay 2
```
Use a custom starting URL:
```bash
python Webcrawler.py --start-url "https://en.wikipedia.org/wiki/Web_scraping"
```
Enable Firebase Firestore storage:
```bash
python Webcrawler.py --firebase-key serviceAccount.json
```
**Note:** On macOS or some Linux systems, you may need to use `python3` instead of `python`.

## Data storage

By default, scraped results are saved locally in `results.jsonl`. Each record contains information about a scraped page, including its title, URL, H2 headings, and timestamp.
If Firebase Firestore is configured, the crawler can also store records in a database under the `pages` collection.

## Firebase setup
1. Open the [Firebase Console](https://console.firebase.google.com/) and create a project.
2. Navigate to **Build → Firestore Database** and create a database.
3. Open **Project settings → Service accounts** and generate a new private key.
4. Save the downloaded JSON key as `serviceAccount.json` in the project directory.
5. Run the crawler with the Firebase key argument:
   ```bash
   python Webcrawler.py --firebase-key serviceAccount.json
   ```
6. Check the `pages` collection in Firestore to view the stored records.

## Future plans

Some ideas for future versions i have include:
- Building a searchable index of scraped Wikipedia articles.
- Developing an article classification system.
- Improving duplicate detection and crawl efficiency.
- Experimenting with a web interface for searching collected data.
- Using this project as a test environment for future web development projects.

## Disclaimer

This is a personal learning project. Please respect Wikipedia's policies, follow applicable usage guidelines, and use reasonable request delays when crawling.

---

*Rags-Webscraper — a work in progress.*
