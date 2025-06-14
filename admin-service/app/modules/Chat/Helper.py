from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field
from typing import Literal
import re
import requests
from typing import TypedDict, Annotated
import os

from langgraph.graph import add_messages
from langchain_ollama import ChatOllama
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver

llm = ChatOllama(model="qwen3:1.7B", temperature=0.7)
memory = MemorySaver()
config = RunnableConfig({"configurable": {"thread_id": "123"}})


class State(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str | None

class IntentClassifier(BaseModel):
    intent: Literal["after_service", "issue", "faq"] = Field(
        description="Classify user's intent based on their input."
    )
class OrderClassifier(BaseModel):
    intent: Literal["purchase", "information"] = Field(
        description="Classify user's intent based on their input. Whether they are providing information to complete purchasement or making a purchase"
    )
classifier_llm = llm.with_structured_output(IntentClassifier)

order_llm = llm.with_structured_output(OrderClassifier)
    

class Helper:
    def __init__(self):
        self.instruction = "Answer in Vietnamese. You are a helpful assistant! Your name is VexererAI. We are company providing traveling services, focusing on selling transportation tickets. Your job is to provide information about our ticket services, and take orders, then extract data from the user to place orders. You are provided with function signatures. You may call one one more functions to assist with the user query. Don't make assumptions about what values to plug into functions. Use pydantic model json schema corresponding to each tool call you make." # /no_think"

    def prompt_from_vectors(self, question):
        '''
        Query vectors from vector database to answer questions related medical fields
        '''
        # Vector search
        api_url = f'http://127.0.0.1:{os.getenv("PORT")}/vector/query'
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(api_url, json={'user_input':question}, headers=headers)
        if response.status_code != 200:
            raise Exception(f"API call failed with status code {response.status_code}. Msg: {response.json()}")

        items = response.json().get('items', [])
        prompts_array = []
        for doc, score in items:
            if score < float(os.getenv('VECTOR_CONFIDENCE')):
                continue
            parts = ["Question: " + doc.get('metadata', {}).get("question", "") + " | " + "Answer: " + doc.get('metadata', {}).get("answer", "")]

            prompts_array.append("".join(parts))

        context = "\n\n".join(prompts_array)
        return f"""You are a helpful assistant. Use the following documents to answer the question.\nContext:\n{context}\nQuestion:\n{question}"""

    def classify_intent(self, state: State):
        last_message = state["messages"][-1]
        print(f"==>> last_message: {last_message}")
        result = classifier_llm.invoke([
            {
                "role": "system",
                "content": """
                You are an intent classifier. Based on the user's input, classify it into one of the following categories:
                - 'after_service': for after_service-related queries (change booking hour, change booking destination, etc.).
                - 'faq': for general info (how a product works, usage, pricing).
                """
                # - 'issue': for problems with a product (defects, wrong item, return).
            },
            {"role": "user", "content": last_message.content},
        ])
        print(f"==>> Routing intent: {result.intent}")
        return {"intent": result.intent}

    def faq_agent(self, state: State):
        last_message = state["messages"][-1]
        data = self.prompt_from_vectors(last_message.content)
        messages = [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": str(data) + last_message.content},
        ]

        responses = llm.invoke(messages)
        return {"messages": [{"role": "assistant", "content": responses.content}]}

    def after_service_agent(self, state: State):
        last_message = state["messages"][-1]
        
        messages = [
            {"role": "system", "content": self.instruction + (
                                                            "Based on the user input, please extract for me the new booking information as JSON:"
                                                            "\n```{\"type\": \"<What do they want to change for their booking>\", \"value\":\"<The new value to be changed>\"}```")},
            {"role": "user", "content": last_message.content},
        ]
        
        responses = llm.invoke(messages)
        return {"messages": [{"role": "assistant", "content": responses.content}]}
