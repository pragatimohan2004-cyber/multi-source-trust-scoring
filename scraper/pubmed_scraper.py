from Bio import Entrez
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.chunking import chunk_text
from utils.tagging import extract_tags

Entrez.email = "your_email@example.com"

def scrape_pubmed(query="artificial intelligence chatbot mental health therapy clinical trial", max_results=5):
    try:
    
        search_handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance",
            datetype="pdat",
            mindate="2022",
            maxdate="2024"
        )
        search_results = Entrez.read(search_handle)
        search_handle.close()

        ids = search_results["IdList"]
        if not ids:
            print("No results found.")
            return None

    
        fetch_handle = Entrez.efetch(db="pubmed", id=ids[0], rettype="xml", retmode="xml")
        records = Entrez.read(fetch_handle)
        fetch_handle.close()

        article = records["PubmedArticle"][0]
        medline = article["MedlineCitation"]
        article_data = medline["Article"]


        title = str(article_data.get("ArticleTitle", "Unknown"))

        authors = []
        if "AuthorList" in article_data:
            for author in article_data["AuthorList"]:
                last = author.get("LastName", "")
                fore = author.get("ForeName", "")
                if last:
                    authors.append(f"{fore} {last}".strip())
        author_str = ", ".join(authors) if authors else "Unknown"

        
        journal = str(article_data["Journal"]["Title"]) if "Journal" in article_data else "Unknown"

        
        pub_year = "Unknown"
        try:
            pub_year = str(article_data["Journal"]["JournalIssue"]["PubDate"].get("Year", "Unknown"))
        except Exception:
            pass

     
        abstract = ""
        if "Abstract" in article_data:
            abstract_texts = article_data["Abstract"].get("AbstractText", [])
            if isinstance(abstract_texts, list):
                abstract = " ".join([str(t) for t in abstract_texts])
            else:
                abstract = str(abstract_texts)

       
        pmid = str(medline["PMID"])
        source_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        content = f"{title}. {abstract}"

        return {
            "source_url": source_url,
            "source_type": "pubmed",
            "title": title,
            "author": author_str,
            "published_date": pub_year,
            "language": "en",
            "region": "Unknown",
            "domain": "pubmed.ncbi.nlm.nih.gov",
            "journal": journal,
            "topic_tags": extract_tags(content),
            "content_chunks": chunk_text(abstract),
            "raw_content": abstract
        }

    except Exception as e:
        print(f"PubMed scraping error: {e}")
        return None


if __name__ == "__main__":
    result = scrape_pubmed(query="artificial intelligence chatbot mental health therapy clinical trial")
    if result:
        print(f"Title: {result['title']}")
        print(f"Author: {result['author']}")
        print(f"Journal: {result['journal']}")
        print(f"Date: {result['published_date']}")
        print(f"URL: {result['source_url']}")
        print(f"Tags: {result['topic_tags']}")
        print(f"Chunks: {len(result['content_chunks'])}")