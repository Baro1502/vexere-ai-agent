import re
import json
import os
import sys
import tiktoken

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, dir_path)
from py_vncorenlp import  VnCoreNLP

def format_history_for_similarity_search(history, limit_pairs = 1):
    recent_history = history[-limit_pairs*2:]

    formatted_history = ""
    for entry in recent_history:
        role = entry['role']
        message = entry['message']
        formatted_history += f"{role}: {message}\n"
    return formatted_history

def num_tokens_from_string(string: str, encoding_name: str = "text-embedding-ada-002") -> int:
    encoding = tiktoken.encoding_for_model(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def normalize_text(text: str) -> str:
    # Remove hashtags
    text = re.sub(r'#\w+', '', text)
    
    # Remove non-alphanumeric characters except for common punctuation
    text = re.sub(r'[^\w\s.,:;!?-]', '', text)

    # Trim multiple \n sequences to a maximum of 2 \n
    text = re.sub(r'\n\s*', '\n', text)
    
    text = text.strip().lower().capitalize()

    return text


'''
def _load_stopwords(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        stopwords = set(file.read().split())
    return stopwords

def _remove_stopwords(text, stopwords):
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stopwords]
    return ' '.join(filtered_words)

def stopword_removal(text):
    stopwords = _load_stopwords('/content/vietnamese-stopwords-dash.txt')
    processed_text = _remove_stopwords(text, stopwords)
    return processed_text
'''

def write_json(df, filename):
    data = []
    for i, row in df.iterrows():
        dicts = {}
        for key in row.keys():
            dicts[key] = row[key]
        data.append(dicts)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)     


parent_dir = os.path.dirname(dir_path)
save_dir=os.path.join(parent_dir,'VnCoreNLP')
model = VnCoreNLP(annotators=["wseg"],save_dir=save_dir)
def combine_words(text):
    combined = model.annotate_text(text)
    concatenated_text = ''

    for sentence in combined.values():
        for word_info in sentence:
            word_form = word_info['wordForm']
            concatenated_text += word_form + ' '
    return concatenated_text.strip()

def preprocessing(text):
    # LoadVnCoreNLP().load_vncorenlp()
    norm = normalize_text(text)
    combined_words = combine_words(norm)
    return combined_words

if __name__ == '__main__':
    print(preprocessing("răng khôn cần được nhổ khi nào?"))