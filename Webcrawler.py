import argparse
import time
from collections import deque
from urllib.parse import urldefrag, urljoin
import requests
from bs4 import BeautifulSoup
import config
from storage import FirestoreStorage, JsonlStorage, make_record

def fetch_page(session, url):
    try:
        response = session.get(url, timeout=config.TIMEOUT)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None
def parse_page(html):
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else "No title found"
    headings = [
        h.get_text(strip=True)
        for h in soup.find_all("h2")
        if h.get_text(strip=True) and h.get_text(strip=True) != "Contents"
    ]
    return title, headings, soup
def extract_links(soup, base_url):
    links = []
    for a in soup.find_all("a", href=True):
        full_url, _ = urldefrag(urljoin(base_url, a["href"]))
        if not config.should_skip_url(full_url):
            links.append(full_url)
    return links
def print_page(page_number, max_pages, title, url, headings):
    print("\n" + "=" * 55)
    print(f"PAGE {page_number}/{max_pages}")
    print("=" * 55)
    print(f"Title: {title}")
    print(f"URL:   {url}")
    print(f"\nHeadings found: {len(headings)}")
    for number, text in enumerate(headings, start=1):
        print(f"  {number:02}. {text}")
    print("=" * 55)
def crawl(start_url, max_pages, delay, storage):
    session = requests.Session()
    session.headers.update({"User-Agent": config.USER_AGENT})
    queue = deque([start_url])
    queued_urls = {start_url}
    pages_scraped = 0
    try:
        while queue and pages_scraped < max_pages:
            url = queue.popleft()

            response = fetch_page(session, url)
            time.sleep(delay)
            if response is None:
                continue

            title, headings, soup = parse_page(response.content)
            pages_scraped += 1
            print_page(pages_scraped, max_pages, title, url, headings)
            storage.save(make_record(pages_scraped, url, title, headings))
            for link in extract_links(soup, url):
                if link not in queued_urls:
                    queue.append(link)
                    queued_urls.add(link)
    except KeyboardInterrupt:
        print("\nInterrupted - saving what we have...")
    finally:
        storage.close()
    print(f"\nDone. Scraped {pages_scraped} pages.")


def parse_args():
    p = argparse.ArgumentParser(description="Rag's Wikipedia crawler")
    p.add_argument("--start", default=config.STARTING_URL)
    p.add_argument("--max-pages", type=int, default=config.MAX_PAGES)
    p.add_argument("--delay", type=float, default=config.REQUEST_DELAY)
    p.add_argument(
        "--firebase-key",
        help="Path to Firebase service account JSON. If omitted, results go to results.jsonl",)
    return p.parse_args()
def main():
    args = parse_args()
    if args.firebase_key:
        storage = FirestoreStorage(
            args.firebase_key, config.FIRESTORE_COLLECTION, config.FIRESTORE_BATCH_SIZE)
        print(f"Saving to Firestore collection '{config.FIRESTORE_COLLECTION}'")
    else:
        storage = JsonlStorage("results.jsonl")
        print("No --firebase-key given, saving to results.jsonl")
    crawl(args.start, args.max_pages, args.delay, storage)


if __name__ == "__main__":
    main()