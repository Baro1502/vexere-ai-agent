import re
import json
import os
import sys
import tiktoken

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, dir_path)
from py_vncorenlp import  VnCoreNLP

class Helper:
    def __init__(self):
        save_dir = os.path.join(dir_path, 'VnCoreNLP')
        self.model = VnCoreNLP(annotators=["wseg"],save_dir=save_dir)
        
    def format_history_for_similarity_search(self,history, limit_pairs = 1):
        recent_history = history[-limit_pairs*2:]

        formatted_history = ""
        for entry in recent_history:
            role = entry['role']
            message = entry['message']
            formatted_history += f"{role}: {message}\n"
        return formatted_history


    def num_tokens_from_string(self,string: str, encoding_name: str = "text-embedding-ada-002") -> int:
        encoding = tiktoken.encoding_for_model(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def normalize_text(self,text: str) -> str:
        # Remove hashtags
        text = re.sub(r'#\w+', '', text)
        
        # Remove non-alphanumeric characters except for common punctuation
        text = re.sub(r'[^\w\s.,:;!?-]', '', text)

        # Trim multiple \n sequences to a maximum of 2 \n
        text = re.sub(r'\n\s*', '\n', text)
        
        text = text.strip().lower().capitalize()

        return text

    def write_json(self,df, filename):
        data = []
        for i, row in df.iterrows():
            dicts = {}
            for key in row.keys():
                dicts[key] = row[key]
            data.append(dicts)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)     


    def combine_words(self,text):
        combined = self.model.annotate_text(text)
        concatenated_text = ''

        for sentence in combined.values():
            for word_info in sentence:
                word_form = word_info['wordForm']
                concatenated_text += word_form + ' '
        return concatenated_text.strip()

    def preprocessing(self,text):
        # LoadVnCoreNLP().load_vncorenlp()
        norm = self.normalize_text(text)
        combined_words = self.combine_words(norm)
        return combined_words
