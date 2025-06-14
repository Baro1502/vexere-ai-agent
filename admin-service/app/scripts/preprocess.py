
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet,stopwords
import nltk
import re
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt_tab')

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def lemmatize_text(text: str) -> str:
    tokens = nltk.word_tokenize(text)
    lemmatized = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized)

def remove_stopwords(text: str) -> str:
    # Tokenize text
    words = nltk.word_tokenize(text)
    # Remove stopwords
    filtered_text = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_text)

def normalize_text(text) -> str:
    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)  # collapse multiple spaces
    text = re.sub(r"[^\w\s,.;:()\-\/]+", "", text)  # remove special chars
    return text.strip()

def clean_field(text, keep_caps=False) -> str:
    text = str(text)
    if not keep_caps:
        text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip(" ,.;:")
    return text

def preprocess_row(row):
    row["drug_name"] = clean_field(row["drug_name"], keep_caps=True)
    row["medical_condition"] = clean_field(row["medical_condition"])
    row["side_effects"] = normalize_text(row["side_effects"])
    row["generic_name"] = clean_field(row["generic_name"])
    row["drug_classes"] = clean_field(row["drug_classes"])
    row["brand_names"] = clean_field(row["brand_names"], keep_caps=True)
    
    return row
def format_record(row):
    return f"drug: {row['drug_name']} || condition: {row['medical_condition']} || side effects: {row['side_effects']} || generic name: {row['generic_name']} || drug class: {row['drug_classes']} || brand names: {row['brand_names']}"