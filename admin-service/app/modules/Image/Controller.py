from flask import request, Response
from app.system import BaseController
import os
import base64
from .Helper import Helper
import threading

gpu_lock = threading.Lock()

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage


# Define Controller class
class Controller(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = Helper()
        self.prompt()
    
    def prompt(self):
        self.SYSTEM_PROMPT = ("Answer in language Vietnamese"
                              "You are a helpful assistant! Your name is VexererAI. We are company providing traveling services, focusing on selling transportation tickets. Your job is to provide information about our ticket services, and take orders, then extract data from the user to place orders. You are provided with function signatures. You may call one one more functions to assist with the user query. Don't make assumptions about what values to plug into functions. Use pydantic model json schema corresponding to each tool call you make." # /no_think"
                              )
    

    def _build_chain(self, text = None, image_base64 = None, system_prompt = ''):
        # Build parts
        contents = []
        if image_base64:

            contents.append({
                "type": "image_url",
                "image_url": image_base64
            })
        if text:
            contents.append({
                "type": "text",
                "text": text
            })

        message = [system_prompt, HumanMessage(content=contents)]
        with gpu_lock:
            chain = ChatOllama(model=os.environ.get('VISION_MODEL'), temperature=0.5)
            for chunk in chain.stream(message):
                yield chunk.content
            del chain
    
    def create(self):
        try:
            print(f"==>> request.files: {request.files}")
            if "file" not in request.files:
                return self.res({"error": "'file' fields are required"}, 400)

            user_input = request.form.get("user_input",None)
            system_prompt = SystemMessage(content=self.SYSTEM_PROMPT)

            print(f"==>> user_input: {user_input}")
            file = request.files["file"]
            image_bytes = file.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            mime_type = file.mimetype or "image/jpeg"
            image_base64 = f"data:{mime_type};base64,{image_b64}"
            answer = self._build_chain(user_input, image_base64, system_prompt)

            return Response(answer, content_type="application/json")
        except Exception as e:
            print(f"==>> {__name__} e: {e}")
            return self.res({'error': str(e)}, 500)
            
    
#------------------------------------------------------------------------------------------------  
# Get the name of the current folder
parent_directory = os.path.dirname(__file__)
# Instantiate the Controller class
controller = Controller(os.path.basename(parent_directory).lower(), __name__)
