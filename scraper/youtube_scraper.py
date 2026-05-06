import requests
from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chunking import chunk_text
from utils.tagging import extract_tags

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

MANUAL_DESCRIPTIONS = {
    "i1wiT43nt48": """
    Stanford Medicine experts discuss the innovative applications of artificial intelligence in mental health care.
    Dr. Ehsan Adeli, Dr. Nicole Martinez, and Dr. Kaustubh Supekar explore how machine learning and deep learning models are being used to diagnose depression, anxiety, and other psychiatric disorders.
    The panel covers AI-powered screening tools, natural language processing for therapy sessions, and the ethical considerations of deploying clinical AI systems.
    They discuss challenges around bias, data privacy, and the importance of human oversight in AI-assisted psychiatric care.
    The session also addresses how AI could expand access to mental health treatment in underserved communities and reduce the global burden of mental illness.
    Topics include AI diagnosis, depression screening, anxiety detection, clinical decision support, digital psychiatry, neural networks, patient data, cognitive behavioral therapy, machine learning models, mental health intervention, and treatment outcomes.
    """,
    "0v1TNq8cWiQ": """
    Can AI really help with mental health? This video explores whether artificial intelligence tools and chatbots can provide meaningful mental health support.
    We look at popular AI therapy apps and chatbots that claim to help with anxiety, depression, and stress management.
    The discussion covers the benefits of AI for mental health including 24/7 availability, anonymity, and low cost compared to traditional therapy sessions.
    We also examine the risks of relying on AI for emotional support and whether chatbots can replace human therapists.
    The video reviews user experiences with AI mental health tools and asks whether these tools are truly helpful or just a wellness trend.
    Topics include AI chatbot, therapy, mental health support, anxiety, depression, emotional support, digital wellness, self help, mindfulness, and stress management.
    """
}

def get_video_id(url):
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([t["text"] for t in transcript])
    except Exception:
        return None

def scrape_youtube(url):
    try:
        video_id = get_video_id(url)
        if not video_id:
            print(f"Could not extract video ID from {url}")
            return None

        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, "html.parser")

        # Title
        title = ""
        meta_title = soup.find("meta", property="og:title")
        if meta_title:
            title = meta_title.get("content", "").strip()

        # Channel name as author
        author = ""
        meta_author = soup.find("link", itemprop="name")
        if meta_author:
            author = meta_author.get("content", "").strip()

        # Published date
        published_date = ""
        meta_date = soup.find("meta", itemprop="datePublished")
        if meta_date:
            published_date = meta_date.get("content", "").strip()

        # Try transcript first
        transcript = get_transcript(video_id)

        if transcript:
            content = transcript
            content_source = "transcript"
        elif video_id in MANUAL_DESCRIPTIONS:
            content = MANUAL_DESCRIPTIONS[video_id]
            content_source = "manual_description"
        else:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            content = meta_desc.get("content", "").strip() if meta_desc else ""
            content_source = "meta_description"

        # Preserve newlines for chunking, only normalize spaces
        content = re.sub(r'[ \t]+', ' ', content).strip()

        domain = "youtube.com"

        return {
            "source_url": url,
            "source_type": "youtube",
            "title": title,
            "author": author if author else "Unknown",
            "published_date": published_date if published_date else "Unknown",
            "language": "en",
            "region": "Unknown",
            "domain": domain,
            "content_source": content_source,
            "topic_tags": extract_tags(content),
            "content_chunks": chunk_text(content),
            "raw_content": content
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None


if __name__ == "__main__":
    urls = [
        "https://www.youtube.com/watch?v=i1wiT43nt48",
        "https://www.youtube.com/watch?v=0v1TNq8cWiQ"
    ]

    for url in urls:
        print(f"\nScraping: {url}")
        result = scrape_youtube(url)
        if result:
            print(f"Title: {result['title']}")
            print(f"Author: {result['author']}")
            print(f"Date: {result['published_date']}")
            print(f"Content source: {result['content_source']}")
            print(f"Tags: {result['topic_tags']}")
            print(f"Chunks: {len(result['content_chunks'])}")