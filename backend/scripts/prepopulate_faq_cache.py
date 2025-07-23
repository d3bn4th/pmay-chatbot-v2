import sys
import os
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from core.redis_cache import set_faq_answer

# Paths to the markdown FAQ files
FAQ_MD_PATHS = [
    os.path.join(os.path.dirname(__file__), '..', 'docs_new', 'cahed_faqs.md'),
    os.path.join(os.path.dirname(__file__), '..', 'docs_new', 'cahed_faqs_hindi.md')
]


def extract_faqs_from_markdown(md_path):
    try:
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Warning: File not found at {md_path}. Skipping.")
        return []

    # Regex to match questions: lines like '# 1. What is PMAY?' or '## 1. PMAY क्या है?'
    # and capture the question and its answer (until the next question or end of file)
    pattern = re.compile(r'^#+ (\d+)\. (.+?)\n(.*?)(?=^#+ (\d+)\. |\Z)', re.DOTALL | re.MULTILINE)
    faqs = []
    for match in pattern.finditer(content):
        qnum = match.group(1)
        question = match.group(2).strip()
        answer = match.group(3).strip()
        faqs.append((question, answer))
    return faqs

def main():
    for path in FAQ_MD_PATHS:
        print(f"\nProcessing FAQ file: {os.path.basename(path)}")
        faqs = extract_faqs_from_markdown(path)
        if not faqs:
            print("No FAQs extracted.")
            continue
        for question, answer in faqs:
            set_faq_answer(question, answer)
            print(f"Cached: '{question}' -> '{answer[:60]}...'")

if __name__ == "__main__":
    main() 