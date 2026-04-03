import random
import re
import io
import PyPDF2
import docx

def extract_text_from_file(file_obj, filename):
    text = ""
    if filename.endswith('.txt'):
        text = file_obj.read().decode('utf-8')
    elif filename.endswith('.pdf'):
        reader = PyPDF2.PdfReader(file_obj)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    elif filename.endswith('.docx'):
        doc = docx.Document(io.BytesIO(file_obj.read()))
        text = "\n".join([para.text for para in doc.paragraphs])
    return text.strip()

import hashlib

def analyze_text_mock(text):
    # Split into sentences naively
    sentences = re.split(r'(?<=[.!?]) +', text)
    if not sentences or not sentences[0]:
        return {
            'ai_probability': 0,
            'perplexity': 0,
            'burstiness': 0,
            'heatmap_data': []
        }
    
    heatmap_data = []
    
    # Calculate word counts for variance (burstiness)
    word_counts = [len(s.split()) for s in sentences]
    if len(word_counts) > 1:
        mean_length = sum(word_counts) / len(word_counts)
        variance = sum((x - mean_length) ** 2 for x in word_counts) / len(word_counts)
    else:
        variance = 0
        mean_length = word_counts[0] if word_counts else 0

    # Burstiness: higher variance means more human-like (bound between 10-100)
    burstiness = min(100.0, max(10.0, variance * 2))
    
    # Perplexity proxy: unique words ratio (simplified)
    words = text.lower().split()
    unique_words = len(set(words))
    total_words = len(words)
    if total_words > 0:
        perplexity = min(100.0, max(10.0, (unique_words / total_words) * 100 * 1.5))
    else:
        perplexity = 0

    total_ai_score = 0
    
    for sentence in sentences:
        s_words = sentence.split()
        length = len(s_words)
        
        # Base AI score
        base_score = 50
        
        # AI often uses medium-length consistent sentences
        if 10 <= length <= 20: 
            base_score += 15
        elif length > 25 or length < 6:
            base_score -= 20
        
        # Use hashlib to create a deterministic "noise" based on sentence text
        # This ensures the exact same text ALWAYS gets the exact same score
        hash_val = int(hashlib.md5(sentence.encode('utf-8')).hexdigest(), 16)
        noise = (hash_val % 41) - 20 # -20 to +20
        
        # Adjust score based on global burstiness and perplexity
        # Low burstiness (AI-like) increases AI score
        if burstiness < 30:
            base_score += 15
        # High perplexity (Human-like) decreases AI score
        if perplexity > 70:
            base_score -= 15
            
        score = min(100, max(0, base_score + noise))
        total_ai_score += score
        
        # Color coding: Bright Red (High AI Confidence), Amber (Likely AI), Emerald Green (Human)
        if score > 70:
            color = 'red'
        elif score > 40:
            color = 'amber'
        else:
            color = 'emerald'
            
        heatmap_data.append({
            'text': sentence,
            'score': int(score),
            'color': color
        })
        
    avg_ai_prob = total_ai_score / len(sentences)
    
    return {
        'ai_probability': round(avg_ai_prob, 1),
        'perplexity': round(perplexity, 2),
        'burstiness': round(burstiness, 2),
        'heatmap_data': heatmap_data
    }
