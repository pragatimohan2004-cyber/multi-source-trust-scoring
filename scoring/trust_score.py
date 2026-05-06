import re
from datetime import datetime


DOMAIN_AUTHORITY = {
    "pubmed.ncbi.nlm.nih.gov": 1.0,
    "www.psychologytoday.com": 0.75,
    "theconversation.com": 0.6,
    "www.calm.com": 0.5,
    "youtube.com": 0.5,
}


KNOWN_CREDIBLE_AUTHORS = [
    "ph.d", "m.d", "dr.", "professor", "stanford", "harvard",
    "university", "institute", "psychiatry", "clinical"
]

SEO_SPAM_SIGNALS = [
    "click here", "buy now", "limited offer", "best price",
    "top 10 ways", "you won't believe", "shocking truth",
    "miracle cure", "guaranteed results", "lose weight fast"
]

FAKE_AUTHOR_PATTERNS = [
    r"^admin$", r"^user\d*$", r"^author$",
    r"^anonymous$", r"^staff$", r"^editor$",
    r"^webmaster$", r"^\w{1}$"
]



def detect_language(content):
   
    if not content:
        return "unknown"
    ascii_chars = sum(1 for c in content if ord(c) < 128)
    ratio = ascii_chars / len(content)
    return "en" if ratio > 0.85 else "non-en"


def score_author_credibility_single(author, source_type):
   
    if source_type == "pubmed":
        return 1.0   
    if not author or author.lower() == "unknown":
        return 0.2

    author_lower = author.lower().strip()

  
    for pattern in FAKE_AUTHOR_PATTERNS:
        if re.match(pattern, author_lower):
            return 0.1

    for keyword in KNOWN_CREDIBLE_AUTHORS:
        if keyword in author_lower:
            return 1.0

    if len(author.split()) >= 2:
        return 0.6

    return 0.4


def resolve_multiple_authors(author_str, source_type):
   
    if not author_str or author_str.lower() == "unknown":
        return 0.2

    parts = [p.strip() for p in author_str.split(",") if p.strip()]

    # Treat as single author if only one part, or total words < 4
    # (catches "Name, Credential" patterns like "Thomas Rutledge, Ph.D.")
    if len(parts) <= 1 or len(author_str.split()) < 4:
        return score_author_credibility_single(author_str, source_type)

    scores = [score_author_credibility_single(p, source_type) for p in parts]
    return round(sum(scores) / len(scores), 3)



def score_author_credibility(author, source_type="blog"):
   
    return resolve_multiple_authors(author, source_type)


def score_domain_authority(domain):
    
    for key in DOMAIN_AUTHORITY:
        if key in domain:
            return DOMAIN_AUTHORITY[key]
    return 0.3


def score_recency(published_date):
    
    if not published_date or published_date == "Unknown":
        return 0.2

    try:
        match = re.search(r"(\d{4})-(\d{2})-(\d{2})", published_date)
        if match:
            date = datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        else:
            year_match = re.search(r"(20\d{2})", published_date)
            if not year_match:
                return 0.2
            date = datetime(int(year_match.group(1)), 7, 1)

        years_old = (datetime.now() - date).days / 365
        if years_old < 1:   return 1.0
        elif years_old < 2: return 0.8
        elif years_old < 3: return 0.6
        elif years_old < 5: return 0.4
        else:               return 0.2

    except Exception:
        return 0.2


def score_citations(content, source_type):
    
    if source_type == "pubmed":
        return 1.0
    if not content:
        return 0.0
    content_lower = content.lower()
    citation_signals = ["doi", "et al", "references", "study", "research", "journal", "published"]
    count = sum(1 for signal in citation_signals if signal in content_lower)
    return round(min(count / len(citation_signals), 1.0), 3)


def score_medical_disclaimer(content):
    
    if not content:
        return 0.0
    content_lower = content.lower()
    disclaimer_signals = [
        "not a substitute", "consult a professional", "seek professional",
        "medical advice", "not intended to", "disclaimer", "licensed therapist",
        "speak with a doctor", "healthcare provider"
    ]
    for signal in disclaimer_signals:
        if signal in content_lower:
            return 1.0
    return 0.0


def detect_seo_spam(content):
    
    if not content:
        return 1.0
    content_lower = content.lower()
    hits = sum(1 for signal in SEO_SPAM_SIGNALS if signal in content_lower)
    return 0.8 if hits >= 2 else 1.0



def calculate_trust_score(source):
  
    author         = source.get("author", "Unknown")
    domain         = source.get("domain", "")
    published_date = source.get("published_date", "Unknown")
    source_type    = source.get("source_type", "blog")
    content        = source.get("raw_content", "")

    language     = detect_language(content)
    author_score = score_author_credibility(author, source_type)
    domain_score = score_domain_authority(domain)
    recency_score    = score_recency(published_date)
    citation_score   = score_citations(content, source_type)
    disclaimer_score = score_medical_disclaimer(content)
    spam_penalty     = detect_seo_spam(content)

    raw_score = (
        0.30 * author_score +
        0.25 * domain_score +
        0.20 * recency_score +
        0.15 * citation_score +
        0.10 * disclaimer_score
    )

    final_score = round(raw_score * spam_penalty, 3)

    return {
        "trust_score":          final_score,
        "language_detected":    language,
        "spam_penalty_applied": spam_penalty < 1.0,
        "breakdown": {
            "author_credibility": round(author_score, 3),
            "domain_authority":   round(domain_score, 3),
            "recency":            round(recency_score, 3),
            "citation_count":     round(citation_score, 3),
            "medical_disclaimer": round(disclaimer_score, 3),
            "seo_spam_penalty":   spam_penalty
        }
    }


if __name__ == "__main__":
    test_sources = [
   
        {
            "author": "Thomas Rutledge, Ph.D.",
            "domain": "www.psychologytoday.com",
            "published_date": "2024-12-30",
            "source_type": "blog",
            "raw_content": "AI mental health study research journal published. consult a professional if you need medical advice."
        },
        {
            "author": "Calm Editorial Team",
            "domain": "www.calm.com",
            "published_date": "2023-10-23",
            "source_type": "blog",
            "raw_content": "AI therapy chatbot mental health support wellness tips. research study published journal."
        },
        {
            "author": "Jesse Hauk, Monash University",
            "domain": "theconversation.com",
            "published_date": "2026-01-14",
            "source_type": "blog",
            "raw_content": "chatbot therapy mental health research study."
        },
        {
            "author": "Stanford CME",
            "domain": "youtube.com",
            "published_date": "2024-10-15",
            "source_type": "youtube",
            "raw_content": "AI mental health stanford university research clinical."
        },
        {
            "author": "Psych2Go",
            "domain": "youtube.com",
            "published_date": "2025-05-17",
            "source_type": "youtube",
            "raw_content": "can ai help mental health therapy tips."
        },
        {
            "author": "Wenjun Zhong, Jianghua Luo, Hong Zhang",
            "domain": "pubmed.ncbi.nlm.nih.gov",
            "published_date": "2023",
            "source_type": "pubmed",
            "raw_content": "systematic review meta-analysis chatbot depression anxiety doi et al references journal published."
        },
      
        {
            "author": "Unknown",
            "domain": "randomhealthblog.com",
            "published_date": "Unknown",
            "source_type": "blog",
            "raw_content": ""
        },
        {
            "author": "admin",
            "domain": "spamblog.net",
            "published_date": "2019-01-01",
            "source_type": "blog",
            "raw_content": "click here buy now limited offer best price miracle cure guaranteed results top 10 ways you won't believe"
        },
        {
            "author": "Dr. Jane Smith, Prof. Alan Brown, Mary Johnson",
            "domain": "www.psychologytoday.com",
            "published_date": "2025-03-10",
            "source_type": "blog",
            "raw_content": "research study published journal. consult a professional."
        },
    ]

    print(f"\n{'Source':<35} {'Score':<8} {'Author':<8} {'Domain':<8} {'Recency':<8} {'Cite':<8} {'Discl':<8} {'Spam?'}")
    print("-" * 100)
    for s in test_sources:
        result = calculate_trust_score(s)
        b = result["breakdown"]
        spam = "YES" if result["spam_penalty_applied"] else "no"
        print(f"{s['author'][:33]:<35} {result['trust_score']:<8} {b['author_credibility']:<8} {b['domain_authority']:<8} {b['recency']:<8} {b['citation_count']:<8} {b['medical_disclaimer']:<8} {spam}")