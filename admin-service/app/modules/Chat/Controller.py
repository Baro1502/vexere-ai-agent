from flask import request, Response
from app.system import BaseController
import os
from .Helper import Helper

from langchain_core.messages import HumanMessage, AIMessage

from langchain_core.runnables import RunnableConfig
from langgraph.graph import StateGraph, START, END, MessagesState
import re

# Define Controller class
class Controller(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = Helper()
        self.agent_graph()
    #     self.prompt()

    # def prompt(self):
    #     self.SYSTEM_PROMPT = ("Answer in language Vietnamese")

    def agent_graph(self):
        # === Graph Setup ===

        graph_builder = StateGraph(state_schema=MessagesState)

        # Add nodes
        graph_builder.add_node("classify_intent", self.helper.classify_intent)
        graph_builder.add_node("faq_agent", self.helper.faq_agent)
        graph_builder.add_node("after_service_agent", self.helper.after_service_agent)

        # Define flow
        graph_builder.add_edge(START, "classify_intent")

        # Conditional branching based on intent
        graph_builder.add_conditional_edges("classify_intent", 
                                            lambda state: state.get("intent"), 
                                            {
                                                "faq": "faq_agent",
                                                "after_service": "after_service_agent",
                                            })


        self.graph = graph_builder.compile()
        self.config = RunnableConfig({"configurable": {"thread_id": "123"}})
        
        # with open("langgraph_flow.png", "wb") as f:
        #     f.write(self.graph.get_graph().draw_png())

    def create(self):
        try:
            data = request.get_json()
            if not data or "user_input" not in data:
                return self.res({"error": "Missing 'user_input'"}, 400)

            query = data["user_input"]
            history = data.get('history', [])

            history_messages = {"messages": [], "intent": None}
            for h in history:
                role = h.get("role")
                content = h.get("message")
                if role.split('.')[-1] == "user":
                    history_messages['messages'].append(HumanMessage(content=content))
                elif role.split('.')[-1] == "assistant":
                    history_messages['messages'].append(AIMessage(content=content))
            

            history_messages['messages'].append(HumanMessage(content=f"Question:\n{query}"))
            def run_agent(message):

                state = self.graph.invoke(message, self.config)
                last_message = state["messages"][-1]

                final_response = re.sub(r'<think>.*?</think>', '', last_message.content, flags=re.DOTALL)

                # print(f"Assistant: {state}\n\n\n")
                print("-"*10)
                yield from [m for m in final_response]
            _gen = run_agent(history_messages)
            return Response(_gen, content_type="text/plain")
        except Exception as e:
            print(f"==>> {__name__} e: {e}")
            return self.res({'error': str(e)}, 500)

#------------------------------------------------------------------------------------------------  
# Get the name of the current folder
parent_directory = os.path.dirname(__file__)
# Instantiate the Controller class
controller = Controller(os.path.basename(parent_directory).lower(), __name__)
