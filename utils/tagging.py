MENTAL_HEALTH_AI_KEYWORDS = [
    "artificial intelligence", "machine learning", "deep learning", "neural network",
    "natural language processing", "nlp", "algorithm", "model", "prediction",
    "mental health", "depression", "anxiety", "psychiatric", "psychology",
    "therapy", "therapist", "counseling", "diagnosis", "treatment",
    "cognitive", "behavioral", "emotion", "stress", "wellbeing",
    "clinical", "patient", "healthcare", "medical", "intervention",
    "chatbot", "virtual assistant", "digital health", "telemedicine",
    "screening", "assessment", "symptom", "disorder", "suicide", "self-harm"
]

def extract_tags(text, max_tags=6):
    """
    Extracts topic tags from text using keyword frequency.
    Returns the most frequently occurring relevant keywords.
    """
    if not text or not text.strip():
        return []

    text_lower = text.lower()
    keyword_counts = {}

    for keyword in MENTAL_HEALTH_AI_KEYWORDS:
        count = text_lower.count(keyword)
        if count > 0:
            keyword_counts[keyword] = count

    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)

    return [kw for kw, _ in sorted_keywords[:max_tags]]