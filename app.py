import os
from openai import AsyncOpenAI
import asyncio

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

from chainlit.auth import create_jwt
from chainlit.server import app
from chainlit.logger import logger
import chainlit as cl
from fastapi.responses import FileResponse
from typing import Optional, Dict


client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])

settings = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1,
    "frequency_penalty": 0,
    "presence_penalty": 0,
}

expected_token = "expected_token"
@cl.header_auth_callback
def header_auth_callback(headers: Dict) -> Optional[cl.User]:
    auth_header = headers.get("Authorization")
    if auth_header:
        token_type, _, token = auth_header.partition(' ')
        if token_type.lower() != "bearer":
            logger.info("Invalid token type. Expected Bearer token.")
        elif token != expected_token:
            logger.info("Invalid token")
        else:
            return cl.User(identifier="admin", metadata={"role": "admin", "provider": "header"})
    else:
        logger.info("Authorization header not found.")
    return None

#{"requireLogin": False, "PasswordAuth": False, "headerAuth": False, "oauthProviders": []}
@app.get("/custom-auth")
async def custom_auth():
    # Verify the user's identity with custom logic.
    token = create_jwt(cl.User(identifier="Test User"))
    return JSONResponse({"token": token})

@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )
    #await cl.Message(content="Connected to Chainlit!").send()


lorem_ipsum = '''
Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Nullam tincidunt quam ac justo tincidunt, id euismod tortor hendrerit. Duis et neque vel metus dapibus ullamcorper. Suspendisse potenti. Nulla facilisi.
\n
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin vel ante eget velit ultricies luctus vitae id tellus. Fusce tristique massa sed quam eleifend, vitae sollicitudin dui euismod. Mauris ullamcorper purus id neque suscipit, at cursus quam bibendum.
'''

@cl.on_message
async def on_message(message: cl.Message):
    token_list = [lorem_ipsum + "\n" for i in range(1, 3)]
    msg = cl.Message(content="You said: " + message.content + "\n")
    for token in token_list:
        await msg.stream_token(token)
        await asyncio.sleep(3)  # Add a 2-second sleep

    # Send back an image
    image_path = "/path/to/your/image.jpg"  # Replace with the actual path to your image
    return FileResponse(image_path, media_type="image/jpeg")

# Image

# Plotly

# Prompt

# Tabular data