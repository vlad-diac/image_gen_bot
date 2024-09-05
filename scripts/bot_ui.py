import gradio as gr
from market_bot import Chatbot, OPENAI_API_KEY, ImageGenerator
import random
import logging
from pprint import pformat
import json

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename='bot_ui.log',
                    filemode='a')
logger = logging.getLogger(__name__)

# Initialize your custom Chatbot
ai_chatbot = Chatbot(api_key=OPENAI_API_KEY, model="gpt-4")
system_prompt = open("market_bot_system_prompt.txt", "r").read()
ai_chatbot.set_system_prompt(system_prompt)

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
        images.append(image)  # Assuming 'image' is already a PIL Image object
    return images

def chat(message, history):
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
    
    if isinstance(response, dict) and "function_call" in response:
        function_name = response["function_call"]
        function_args = json.loads(response["arguments"])
        
        if function_name == "generate_images":
            generated_images = generate_images(function_args["prompts"])
            
            # Create a markdown formatted message
            markdown_message = "### Generated Images\n\n"
            for i, prompt in enumerate(function_args["prompts"]):
                markdown_message += f"**Image {i+1}:**\n"
                markdown_message += f"- Date: {function_args['dates'][i]}\n"
                markdown_message += f"- Content Description: {function_args['content_descriptions'][i]}\n"
                markdown_message += f"- Prompt: {prompt}\n\n"
            
            # Add the function call response to the conversation
            ai_chatbot.send_message(f"Function 'generate_images' was called. {markdown_message}")
            
            return markdown_message, generated_images
    else:
        return response, []

def format_chat_history(history):
    formatted_history = []
    for human, bot in history:
        formatted_history.append(f"Human: {human}")
        formatted_history.append(f"AI: {bot}")
    return "\n".join(formatted_history)

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
        bot_message, images = chat(message, chat_history)
        logger.info(f"Bot message:\n{pformat(bot_message)}")
        if isinstance(bot_message, dict) and "function_call" in bot_message:
            # Handle function call
            if bot_message['function_call'] == 'generate_images':
                prompts = bot_message['arguments']['prompts']

                generated_images = generate_images(prompts)
                logger.info(f"Generated images:\n{pformat(generated_images)}")
                # Create a list of (image, label) tuples
                image_objects = [(img['image'], prompt) for img, prompt in zip(generated_images, prompts)]
                
                # Create a markdown formatted message
                markdown_message = "### Generated Images\n\n"
                for i, prompt in enumerate(prompts):
                    markdown_message += f"**Image {i+1}:**\n"
                    markdown_message += f"- Date: {bot_message['arguments']['dates'][i]}\n"
                    markdown_message += f"- Content Description: {bot_message['arguments']['content_descriptions'][i]}\n"
                    markdown_message += f"- Prompt: {prompt}\n\n"
                chatbot_history_response = bot_message['arguments']
                
                chat_history.append((message, markdown_message))
                return "", chat_history, image_objects
        else:
            # Handle regular text response
            chat_history.append((message, bot_message))
        return "", chat_history, []

    send.click(respond, [msg, chatbot], [msg, chatbot, image_gallery])
    msg.submit(respond, [msg, chatbot], [msg, chatbot, image_gallery])
    
demo.launch(server_name="0.0.0.0", server_port=7860)


