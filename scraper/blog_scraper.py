import requests
from bs4 import BeautifulSoup
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chunking import chunk_text
from utils.tagging import extract_tags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_blog(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for tag in soup(["nav", "footer", "script", "style", "aside", "form", "header"]):
            tag.decompose()

       
        title = ""
        if soup.find("h1"):
            title = soup.find("h1").get_text(strip=True)

        
        if not title:
            meta_title = soup.find("meta", property="og:title")
            if meta_title:
                title = meta_title.get("content", "").strip()

       
        author = ""
        author_candidates = [
            soup.find("a", rel="author"),
            soup.find(class_=lambda c: c and "author" in c.lower()),
            soup.find(attrs={"data-testid": lambda v: v and "author" in v.lower()}),
            soup.find("span", class_=lambda c: c and "byline" in c.lower()),
            soup.find(attrs={"itemprop": "author"}),
            soup.find(attrs={"name": "author"}),
        ]
        for candidate in author_candidates:
            if candidate:
                text = candidate.get_text(strip=True)
                if text and len(text) < 80 and "\n" not in text:
                    author = text
                    break

        # Published date
        published_date = ""
        date_candidates = [
            soup.find("time"),
            soup.find(attrs={"datetime": True}),
            soup.find(attrs={"itemprop": "datePublished"}),
            soup.find(class_=lambda c: c and "date" in c.lower()),
            soup.find(class_=lambda c: c and "publish" in c.lower()),
        ]
        for candidate in date_candidates:
            if candidate:
                dt = candidate.get("datetime") or candidate.get("content") or candidate.get_text(strip=True)
                if dt and len(dt) < 50:
                    published_date = dt
                    break

        
        content = ""
        content_candidates = [
            soup.find("article"),
            soup.find(class_=lambda c: c and "article" in c.lower()),
            soup.find(class_=lambda c: c and "content" in c.lower()),
            soup.find("main"),
        ]
        for candidate in content_candidates:
            if candidate:
                content = candidate.get_text(separator="\n", strip=True)
                break

        if not content:
            content = soup.get_text(separator="\n", strip=True)

        content = " ".join(content.split())
        language = "en"
        domain = url.split("/")[2]

        return {
            "source_url": url,
            "source_type": "blog",
            "title": title,
            "author": author if author else "Unknown",
            "published_date": published_date if published_date else "Unknown",
            "language": language,
            "region": "Unknown",
            "domain": domain,
            "topic_tags": extract_tags(content),
            "content_chunks": chunk_text(content),
            "raw_content": content
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


if __name__ == "__main__":
    sources = [
        {
            "url": "https://www.psychologytoday.com/us/blog/the-healthy-journey/202412/ai-mental-health-is-coming-are-you-ready",
            "author": "Thomas Rutledge, Ph.D.",
            "published_date": "2024-12-30"
        },
        {
            "url": "https://www.calm.com/blog/ai-mental-health",
            "author": "Calm Editorial Team",
            "published_date": "2023-10-23"
        },
        {
            "url": "https://theconversation.com/the-ai-therapist-will-see-you-now-can-chatbots-really-improve-mental-health-259360",
            "author": "Jesse Hauk, Monash University",
            "published_date": "2026-01-14"
        },
    ]

    for source in sources:
        print(f"\nScraping: {source['url']}")
        result = scrape_blog(source['url'])
        if result:
            result['author'] = source['author']
            result['published_date'] = source['published_date']
            print(f"Title: {result['title']}")
            print(f"Author: {result['author']}")
            print(f"Date: {result['published_date']}")
            print(f"Tags: {result['topic_tags']}")
            print(f"Chunks: {len(result['content_chunks'])}")