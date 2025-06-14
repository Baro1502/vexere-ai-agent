from flask import request
from app.system import BaseController
from .Helper import Helper

import os
from langchain_pinecone import PineconeVectorStore
from langchain_ollama import OllamaEmbeddings
from pinecone import Pinecone

# Define Controller class
class Controller(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = Helper()

        self.embedding = OllamaEmbeddings(
                    # model="nomic-embed-text"
                    model="bge-m3"
                )
        pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))


        index = pc.Index(os.environ.get("INDEX_NAME"))
        self.vector_store = PineconeVectorStore(index=index, embedding=self.embedding)

    def query(self):
        try:
            param = request.json
            results = self.vector_store.similarity_search_with_score(query=self.helper.preprocessing(
                                                                                                param.get('user_input')
                                                                                                ),
                                                                     k=param.get('num',3))
            # print(f"==>> results: {[results[0][0],results[0][1]]}")
            
            return self.res({'items': [(dict(r[0]),r[1]) for r in results], 'status': 'success'}, 200)
        except ValueError as ve:
            return self.res({'error': str(ve)}, 400)
        except Exception as e:
            return self.res({'error': str(e)}, 500)


#------------------------------------------------------------------------------------------------  
# Get the name of the current folder
parent_directory = os.path.dirname(__file__)
# Instantiate the Controller class
controller = Controller(os.path.basename(parent_directory).lower(), __name__)