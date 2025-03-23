# bot.py

import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN is not set in .env")

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

# Create bot instance
bot = commands.Bot(command_prefix="^", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

async def main():
    # Load your Reddit cog
    try:
        await bot.load_extension("redditpostcallout")
        print("RedditPostCallout cog loaded successfully.")
    except Exception as e:
        print(f"Error loading RedditPostCallout cog: {e}")

    # Start the bot
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
