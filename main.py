import json
import os
from scraper.blog_scraper import scrape_blog
from scraper.youtube_scraper import scrape_youtube
from scraper.pubmed_scraper import scrape_pubmed
from scoring.trust_score import calculate_trust_score

OUTPUT_DIR = "output"

BLOG_SOURCES = [
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

YOUTUBE_SOURCES = [
    {
        "url": "https://www.youtube.com/watch?v=i1wiT43nt48",
        "author": "Stanford CME",
        "published_date": "2024-10-15"
    },
    {
        "url": "https://www.youtube.com/watch?v=0v1TNq8cWiQ",
        "author": "Psych2Go",
        "published_date": "2025-05-17"
    },
]

def save_json(data, filename):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Saved → {filepath}")

def score_and_append(item, results_list):
    scored = calculate_trust_score(item)
    item["trust_score"]          = scored["trust_score"]
    item["trust_breakdown"]      = scored["breakdown"]
    item["language_detected"]    = scored["language_detected"]
    item["spam_penalty_applied"] = scored["spam_penalty_applied"]
    results_list.append(item)

def run_pipeline():
    print("=" * 65)
    print("   AI & Mental Health — Scraping + Trust Scoring Pipeline")
    print("=" * 65)

    all_results = []

    print("\n[1/3] Scraping blogs...")
    blogs = []
    for source in BLOG_SOURCES:
        try:
            result = scrape_blog(source["url"])
            if result:
                result["author"]         = source["author"]
                result["published_date"] = source["published_date"]
                score_and_append(result, blogs)
                print(f"  ✓ {source['author']}")
        except Exception as e:
            print(f"  ERROR scraping {source['url']}: {e}")
    save_json(blogs, "blogs.json")
    print(f"  Blogs collected: {len(blogs)}")
    all_results.extend(blogs)

   
    print("\n[2/3] Scraping YouTube...")
    videos = []
    for source in YOUTUBE_SOURCES:
        try:
            result = scrape_youtube(source["url"])
            if result:
                if not result.get("author") or result["author"] == "Unknown":
                    result["author"] = source["author"]
                if not result.get("published_date") or result["published_date"] == "Unknown":
                    result["published_date"] = source["published_date"]
                score_and_append(result, videos)
                print(f"  ✓ {source['author']}")
        except Exception as e:
            print(f"  ERROR scraping {source['url']}: {e}")
    save_json(videos, "youtube.json")
    print(f"  Videos collected: {len(videos)}")
    all_results.extend(videos)

    
    print("\n[3/3] Scraping PubMed...")
    papers = []
    try:
        result = scrape_pubmed(query="artificial intelligence chatbot mental health therapy clinical trial")
        if result:
            score_and_append(result, papers)
            print(f"  ✓ {result.get('author', 'Unknown')}")
    except Exception as e:
        print(f"  ERROR in PubMed scraper: {e}")
    save_json(papers, "pubmed.json")
    print(f"  Papers collected: {len(papers)}")
    all_results.extend(papers)

   
    print("\n[4/4] Saving combined output...")
    save_json(all_results, "all_sources.json")

    print("\n" + "=" * 65)
    print("   TRUST SCORE SUMMARY")
    print("=" * 65)
    print(f"{'Source':<33} {'Type':<9} {'Score':<8} {'Lang':<6} {'Spam?'}")
    print("-" * 65)

    sorted_results = sorted(all_results, key=lambda x: x.get("trust_score", 0), reverse=True)
    for item in sorted_results:
        title = item.get("title", "Unknown")[:31]
        stype = item.get("source_type", "?")[:7]
        score = item.get("trust_score", "N/A")
        lang  = item.get("language_detected", "?")
        spam  = "⚠ YES" if item.get("spam_penalty_applied") else "no"
        print(f"{title:<33} {stype:<9} {score:<8} {lang:<6} {spam}")

    print("=" * 65)
    print(f"\nDone. {len(all_results)} sources processed.")
    print(f"Outputs saved to: ./{OUTPUT_DIR}/")

if __name__ == "__main__":
    run_pipeline()