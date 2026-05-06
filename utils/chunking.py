def chunk_text(text, max_words=250):
    if not text or not text.strip():
        return []

    
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]

   
    if len(paragraphs) <= 1:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]

    
    if len(paragraphs) <= 1:
        words = text.split()
        paragraphs = []
        for i in range(0, len(words), max_words):
            paragraphs.append(' '.join(words[i:i + max_words]))

    chunks = []
    current_chunk = []
    current_word_count = 0

    for paragraph in paragraphs:
        word_count = len(paragraph.split())
        if current_word_count + word_count > max_words and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [paragraph]
            current_word_count = word_count
        else:
            current_chunk.append(paragraph)
            current_word_count += word_count

    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks