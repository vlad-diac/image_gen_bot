from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from generate_image import ImageGenerator
import random
from pprint import pprint
load_dotenv()

OpenAI_API_KEY = OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class Chatbot:
    def __init__(self, api_key=None, model="gpt-3.5-turbo"):
        print("Chatbot initialized")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.messages = []
        self.system_prompt = "You are a helpful assistant."

    def set_system_prompt(self, prompt):
        """Set the system prompt for the conversation."""
        self.system_prompt = prompt
        # Reset the messages list with the new system prompt
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def send_message(self, message, functions=None):
        """Send a message to the chatbot and return its response."""
        # Add the user's message to the conversation history
        self.messages.append({"role": "user", "content": message})

        # If there's no system message yet, add it
        if not any(msg["role"] == "system" for msg in self.messages):
            self.messages.insert(0, {"role": "system", "content": self.system_prompt})

        # Prepare the API call parameters
        params = {
            "model": self.model,
            "messages": self.messages,
            "temperature": 0.5,
            "max_tokens": 2500,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }

        # Add functions if provided
        if functions:
            params["tools"] = functions
            params["tool_choice"] = "required"

        # Get the chatbot's response
        print("params")
        pprint(params)
        response = self.client.chat.completions.create(**params)
        print("openai response")
        pprint(response)
        # Extract the response content
        choice = response.choices[0]
        if choice.message.tool_calls:
            # The model wants to call a function
            tool_call = choice.message.tool_calls[0]
            function_call_result_message = {
                "role": "tool",
                "content": json.dumps({"result": "Function executed successfully"}),
                "tool_call_id": tool_call.id
            }
            self.messages.append(choice.message)
            self.messages.append(function_call_result_message)
            return {
                "function_call": tool_call.function.name,
                "arguments": json.loads(tool_call.function.arguments)
            }
        else:
            # Normal text response
            bot_response = choice.message.content
            self.messages.append({"role": "assistant", "content": bot_response})
            return bot_response