from typing import Literal
from dotenv import load_dotenv
load_dotenv();
import os
import re
import requests
import discord
from discord import app_commands
import openai

openai.api_key = os.getenv("OPENAI_API_KEY")

def setup_messages():
    system = "Your are a discord bot, that is chatting with multiple people and you are trying to learn from the conversations."
    with open("system.txt", "r") as f:
        system = f.read()
    return [{
        "role": "system", "content": system
    }]

messages = setup_messages();
user_text = messages
message_lock = False

CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
TENOR_KEY = os.getenv("TENOR_KEY")

MY_GUILD = discord.Object(os.getenv("GUILD_ID"))

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)
client = MyClient()

async def openai_query(channel):
    global message_lock
    message_lock = True
    async with channel.typing():
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            n=1,
        )
        messages.append(response["choices"][0]["message"])
    
    text = messages[-1]["content"]
    gif_regex = r"\[GIF: ([^\]]+)\]";
    gifs = re.findall(gif_regex, text)
    for gif in gifs:
        print("Searching for gif: " + gif)
        response = requests.get(f"https://tenor.googleapis.com/v2/search", params = {"q": gif, "key": TENOR_KEY, "limit": 1, "client_id": "ThreadGPT", "media_filter": "tinygif", "random": "true"})
        if response.status_code == 200:
            gifs = response.json()["results"]
            if len(gifs) > 0:
                text = text.replace(f"[GIF: {gif}]", gifs[0]["url"] + " **(via Tenor)**")
            else:
                text = text.replace(f"[GIF: {gif}]", "https://media.tenor.com/DiUjye_MGoAAAAAM/not-found-404error.gif")
    await channel.send(text)
    message_lock = False

async def initial_message(client: discord.Client):
    text = f"Write a hello message to the channel."
    messages.append({"role": "user", "content": text})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )
    text = response["choices"][0]["message"]
    messages.append(text)
    await client.get_channel(CHANNEL_ID).send(text["content"])

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    await initial_message(client)

@client.event
async def on_message(message):
    if (message.channel.id != CHANNEL_ID or message.author.id == client.user.id):
        return
    elif (message_lock):
        await message.delete()
        return
    text = f"Message from {message.author} contains: {message.content}"
    messages.append({"role": "user", "content": text})
    
    await openai_query(message.channel)

@client.event
async def on_reaction_add(reaction, user):
    if (reaction.message.channel.id != CHANNEL_ID or user.id == client.user.id):
        return
    elif (message_lock):
        reaction.remove(user)
        return
    text = f"Reaction from {user} contains: {reaction.emoji} on message: {reaction.message.content}"
    messages.append({"role": "user", "content": text})
    
    await openai_query(reaction.message.channel)

@client.tree.command(name="reset", description="Reset the conversation.")
@app_commands.describe(state="System text")
async def reset_command(interaction: discord.Interaction, state: Literal["trunk", "user"]):
    global messages, user_text
    if state == "trunk":
        messages = setup_messages();
    elif state == "user":
        messages = user_text;
    await interaction.response.send_message("Conversation reset")
    await initial_message(client)

@client.tree.command(name="system", description="Set the system text")
@app_commands.describe(text="The system text")
async def system_command(interaction: discord.Interaction, text: str):
    global messages, user_text
    user_text[0]["content"] = text
    messages = user_text
    await interaction.response.send_message("Reset with new system text.")
    await initial_message(client)

client.run(os.getenv("DISCORD_TOKEN"))