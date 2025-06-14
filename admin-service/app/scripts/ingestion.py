from langchain_ollama import OllamaEmbeddings
import pandas as pd
import os
from tqdm import tqdm
from langchain_pinecone import PineconeVectorStore
from utils import preprocessing
from langchain.docstore.document import Document


index_name = "vexere-dev"


if __name__ == '__main__':

    embeddings_model = OllamaEmbeddings(
        # model="nomic-embed-text"
        model="bge-m3"
    )
    
    df = pd.read_csv("data/faq_data.csv")
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # print(df.head(3))
    # df = df.sample(frac=.01)
    # # Apply to side effects & description only
    df = df.fillna('')\
            # .apply(lemmatize_text)\
            # .apply(remove_stopwords)
            # .aplpy(preprocess_row)

    df['question'] = df['question'].fillna('').apply(preprocessing)
    print(f"==>> df: {df}")

    vector_store = PineconeVectorStore.from_documents([], embeddings_model, index_name=index_name)

    batch_size = 100
    for i in tqdm(range(0, len(df), batch_size)):
        batch = df.iloc[i:i+batch_size]
        texts = [row['question'] for _,row in batch.iterrows()]

        doc = [Document(page_content=text, metadata=row.to_dict()) for text, (_, row) in zip(texts, batch.iterrows())]
        
        vector_store.add_documents(doc)

    print("✅ Done pushing to Pinecone.")
