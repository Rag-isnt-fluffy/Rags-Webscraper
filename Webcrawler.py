from collections import deque
from urllib.parse import urljoin
from urllib.parse import urldefrag
from urllib.parse import parse_qs
from bs4 import BeautifulSoup
from config import should_skip_url
import requests

#queue of URLs
starting_url = "https://en.wikipedia.org/wiki/West_Asia"

#veriables
discovered_urls = set()
queue = deque([starting_url])
queued_urls = {starting_url}
pages_scraped = 0
max_pages = 1000

while queue and pages_scraped < max_pages:
        url = queue.popleft()
        if url in discovered_urls:
                continue
    
        try:
              response = requests.get(
                        url,
                        timeout=10,
                        headers={"User-Agent": "Mozilla/5.0"}
                )
              response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch {url}: {e}")
            continue
        discovered_urls.add(url)
        soup = BeautifulSoup(response.content, "html.parser")
        #extract (Title)
        title = soup.title.get_text(strip=True) if soup.title else "No title found"

        #heading
        headings = soup.find_all("h2")
        heading_texts = []

        for heading in headings:
            heading_text = heading.get_text(strip=True)

            if heading_text and heading_text != "Contents":
                heading_texts.append(heading_text)

        pages_scraped += 1

        print("\n" + "=" * 55)
        print(f"PAGE {pages_scraped}/{max_pages}")
        print("=" * 55)
        print(f"Title: {title}")
        print(f"URL:   {url}")
        print(f"\nHeadings found: {len(heading_texts)}")

        for number, heading_text in enumerate(heading_texts, start=1):
            print(f"  {number:02}. {heading_text}")

        print("=" * 55)

        if pages_scraped >= max_pages:
               print(f"Reached the maximum limit of {max_pages} pages scraped.")
               break
        
        links = soup.find_all("a", href=True)

        for link in links:
            full_url = urljoin(url, link["href"])
            full_url, fragment = urldefrag(full_url)

            if should_skip_url(full_url):
                continue
            if (
                full_url not in discovered_urls
                and full_url not in queued_urls
            ):
                queue.append(full_url)
                queued_urls.add(full_url)

