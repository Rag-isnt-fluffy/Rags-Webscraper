from collections import deque
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

# Queue of URLs to scrape
starting_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"

# Tracking variables
discovered_urls = set()
queue = deque([starting_url])
pages_scraped = 0
max_pages = 10

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
    
    # Extract the page title
    title = soup.title.get_text(strip=True) if soup.title else "No title found"
    
    # Extract all main headings
    headings = [
        heading.get_text(strip=True) 
        for heading in soup.find_all(["h1", "h2", "h3"])
    ]
    
    pages_scraped += 1
    print("URL:", url)
    print("Title:", title)
    print("Headings:", headings)
    print("-" * 40)
    
    if pages_scraped >= max_pages:
        print(f"Reached the maximum limit of {max_pages} pages scraped.")
        break

    links = soup.find_all("a", href=True)
    for link in links:
        full_url = urljoin(url, link["href"])
        
        if full_url.startswith("https://en.wikipedia.org/wiki/"):
            if full_url not in discovered_urls:
                queue.append(full_url)
