sentences = '''
what are size effects of aczone?
'''


# ----------
from langchain_ollama import OllamaEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os
model = OllamaEmbeddings(
    # model="nomic-embed-text"
    model="bge-m3"
)

embeddings = model.embed_query(sentences)
# print(','.join(map(str, embeddings)))


pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

index_name = "thesis" 

index = pc.Index(index_name)
vector_store = PineconeVectorStore(index=index, embedding=model)
results = vector_store.similarity_search_with_score(query="qux",k=1)
print(f"==>> results: {results}")
