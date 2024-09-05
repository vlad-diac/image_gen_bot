import gradio as gr
from market_bot import Chatbot, OPENAI_API_KEY, ImageGenerator
import random
import logging
from pprint import pformat, pprint
import json
import os

# Create a 'logs' directory if it doesn't exist
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

# Set up logging
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'bot_ui.log')
os.makedirs(os.path.dirname(log_file), exist_ok=True)

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=log_file,
                    filemode='a')
logger = logging.getLogger(__name__)

# Initialize your custom Chatbot
ai_chatbot = Chatbot(api_key=OPENAI_API_KEY, model="gpt-4o")
try:
    with open("market_bot_system_prompt.txt", "r") as f:
        system_prompt = f.read()
    ai_chatbot.set_system_prompt(system_prompt)
    logger.info("System prompt loaded successfully")
except FileNotFoundError:
    logger.error("System prompt file not found")
except Exception as e:
    logger.error(f"Error loading system prompt: {str(e)}")

generator = ImageGenerator()

def generate_images(prompts):
    images = []
    for prompt in prompts:
        image = generator.generate_image(
            prompt=prompt,
            cfg=1.5,
            steps=25,
            seed=random.randint(0, 4294967295)
        )
        images.append(image) 
    print("generate_images output:")
    pprint(images)
    return images

def chat(message, history):
    print(f"Received message: {message}")
    print(f"Current history: {history}")
    functions = [
        {
            "type": "function",
            "function": {
                "name": "generate_images",
                "description": "Generate multiple images based on a list of prompts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompts": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "The prompts for image generation"
                        },
                        "dates": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "The dates for each image"
                        },
                        "content_descriptions": {
                            "type": "array",
                            "items": {
                                "type": "string",
                            },
                            "description": "The content descriptions for each image"
                        },
                    },
                    "required": ["prompts", "dates", "content_descriptions"],
                    "additionalProperties": False
                },
            },
        },
    ]
    
    response = ai_chatbot.send_message(message, functions=functions)
    print("response:")
    pprint(response)

    if isinstance(response, dict) and "function_call" in response:
        function_name = response["function_call"]
        
        if function_name == "generate_images":
            function_args = response["arguments"]
            generated_images = generate_images(function_args["prompts"])
            
            # Create a markdown formatted message
            markdown_message = "### Generated Images\n\n"
            for i, prompt in enumerate(function_args["prompts"]):
                markdown_message += f"**Image {i+1}:**\n"
                markdown_message += f"- Date: {function_args['dates'][i]}\n"
                markdown_message += f"- Content Description: {function_args['content_descriptions'][i]}\n"
                markdown_message += f"- Prompt: {prompt}\n\n"
            
            return {
                "type": "image_generation",
                "message": markdown_message,
                "images": generated_images,
                "prompts": function_args["prompts"]
            }
    else:
        return {
            "type": "text",
            "message": response
        }


with gr.Blocks() as demo:
    gr.Markdown("# Marketing Chatbot with Image Generation")
    
    with gr.Row():
        with gr.Column(scale=1):
            chatbot = gr.Chatbot()
            msg = gr.Textbox(label="Enter your message")
            send = gr.Button("Send")
        
        with gr.Column(scale=1):
            image_gallery = gr.Gallery(label="Generated Images", show_label=True)
    
    def respond(message, chat_history):
        response = chat(message, chat_history)
        print("Chat response:")
        pprint(response)
        print("Chat History:")
        pprint(chat_history)
        if response["type"] == "image_generation":
            image_objects = [(img["filename"], prompt) for img, prompt in zip(response["images"], response["prompts"])]
            chat_history.append((message, response["message"]))
            return "", chat_history, image_objects
        else:
            chat_history.append((message, response["message"]))
            return "", chat_history, []

    send.click(respond, [msg, chatbot], [msg, chatbot, image_gallery])
    msg.submit(respond, [msg, chatbot], [msg, chatbot, image_gallery])
    
demo.launch(server_name="0.0.0.0", server_port=7860)


