import discord
from discord.ext import commands, tasks
import os
import datetime
import random
import asyncpraw
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")

if not (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET and REDDIT_USER_AGENT):
    raise ValueError("Reddit credentials are not set in your environment variables.")

# Initialize Async PRAW client
reddit = asyncpraw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

def build_embed_from_post(post) -> discord.Embed:
    """Build a Discord embed for a Reddit post, including image preview if available."""
    embed = discord.Embed(
        title=post.title,
        url=post.url,
        timestamp=datetime.datetime.utcfromtimestamp(post.created_utc)
    )

    # Truncate selftext if it exists
    if post.selftext:
        embed.description = post.selftext[:200] + ("..." if len(post.selftext) > 200 else "")

    # Attempt to set an image preview
    if ("i.redd.it" in post.url) or post.url.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
        embed.set_image(url=post.url)
    else:
        if hasattr(post, "preview"):
            images = post.preview.get("images", [])
            if images:
                image_url = images[0]["source"]["url"]
                embed.set_image(url=image_url)

    embed.set_footer(text=f"Posted by u/{post.author}")
    return embed

class RedditPostCallout(commands.Cog):
    """
    A cog supporting:
    - add/remove/list subreddits
    - manual random fetch: ^reddit <subreddit>
    - toggle auto feed on/off: ^reddit <subreddit> on/off
    - set feed channel: ^tochannel #channel <subreddit>
    - auto-post loop every 2 minutes
    """

    def __init__(self, bot):
        self.bot = bot
        # Dictionary to track all monitored subreddits
        # Key: subreddit_name (str), Value: dict with fields:
        #   "enabled" (bool), "channel_id" (int or None), "posted_ids" (set)
        self.monitored_subreddits = {}

        # Start the auto-post loop
        self.auto_post_loop.start()

    def cog_unload(self):
        self.auto_post_loop.cancel()

    @tasks.loop(minutes=2)
    async def auto_post_loop(self):
        """Automatically fetch and post new items from subreddits that have auto-feed enabled."""
        for subreddit_name, data in self.monitored_subreddits.items():
            if not data["enabled"]:
                continue  # skip if auto feed is off
            channel_id = data["channel_id"]
            if not channel_id:
                continue  # no channel set
            channel = self.bot.get_channel(channel_id)
            if not channel:
                continue  # invalid or inaccessible channel

            try:
                sub = await reddit.subreddit(subreddit_name)
                async for post in sub.new(limit=5):
                    if post.id not in data["posted_ids"]:
                        embed = build_embed_from_post(post)
                        await channel.send(embed=embed)
                        data["posted_ids"].add(post.id)
            except Exception as e:
                print(f"[auto_post_loop] Error fetching from r/{subreddit_name}: {e}")

    @auto_post_loop.before_loop
    async def before_auto_post_loop(self):
        await self.bot.wait_until_ready()

    # ---------------------
    #  ADMIN SUBREDDIT MGMT
    # ---------------------

    @commands.hybrid_command(name="addreddit", description="Add a subreddit to the monitored list.")
    @commands.has_permissions(administrator=True)
    async def addreddit(self, ctx, subreddit: str):
        """^addreddit <subreddit>"""
        subreddit = subreddit.strip().lower().lstrip("r/")
        if subreddit in self.monitored_subreddits:
            await ctx.send(f"r/{subreddit} is already being monitored.")
        else:
            self.monitored_subreddits[subreddit] = {
                "enabled": False,
                "channel_id": None,
                "posted_ids": set()
            }
            await ctx.send(f"Added r/{subreddit} to the monitored list.")

    @commands.hybrid_command(name="removereddit", description="Remove a subreddit from the monitored list.")
    @commands.has_permissions(administrator=True)
    async def removereddit(self, ctx, subreddit: str):
        """^removereddit <subreddit>"""
        subreddit = subreddit.strip().lower().lstrip("r/")
        if subreddit in self.monitored_subreddits:
            del self.monitored_subreddits[subreddit]
            await ctx.send(f"Removed r/{subreddit} from the monitored list.")
        else:
            await ctx.send(f"r/{subreddit} is not in the monitored list.")

    @commands.hybrid_command(name="listreddit", description="List all monitored subreddits.")
    async def listreddit(self, ctx):
        """^listreddit"""
        if not self.monitored_subreddits:
            return await ctx.send("No subreddits are currently being monitored.")
        
        lines = []
        for name, data in self.monitored_subreddits.items():
            status = "ON" if data["enabled"] else "OFF"
            chan_info = f"<#{data['channel_id']}>" if data["channel_id"] else "No channel set"
            lines.append(f"**r/{name}** — Enabled: **{status}**, Channel: {chan_info}")
        msg = "\n".join(lines)
        await ctx.send(msg)

    # -----------------------
    #   TOGGLE AUTO FEED & CHANNEL
    # -----------------------

    @commands.hybrid_command(name="reddit", description="Manually fetch a random post OR toggle auto feed on/off.")
    async def reddit_command(self, ctx, subreddit: str, toggle: str = None):
        """
        Usage:
          ^reddit <subreddit>              -> Fetch a random post manually
          ^reddit <subreddit> on/off       -> Toggle auto feed
        """
        subreddit = subreddit.lower().lstrip("r/")
        # Check if the subreddit is being monitored
        if subreddit not in self.monitored_subreddits:
            return await ctx.send(f"r/{subreddit} is not being monitored. Add it using ^addreddit.")

        # If user provided 'on' or 'off', toggle auto feed
        if toggle is not None:
            toggle = toggle.lower()
            if toggle not in ["on", "off"]:
                return await ctx.send("Invalid toggle. Use '^reddit <subreddit> on' or '^reddit <subreddit> off'.")
            is_on = (toggle == "on")
            self.monitored_subreddits[subreddit]["enabled"] = is_on
            await ctx.send(f"Auto feed for r/{subreddit} is now **{'ON' if is_on else 'OFF'}**.")
            return

        # Otherwise, fetch a random post manually
        try:
            sub = await reddit.subreddit(subreddit)
            posts = []
            async for post in sub.new(limit=10):
                posts.append(post)
            if not posts:
                return await ctx.send(f"No posts found in r/{subreddit} at this time.")

            chosen_post = random.choice(posts)
            embed = build_embed_from_post(chosen_post)
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"Error fetching post from r/{subreddit}: {e}")

    @commands.hybrid_command(name="tochannel", description="Set the channel for a subreddit's auto feed.")
    @commands.has_permissions(administrator=True)
    async def tochannel_command(self, ctx, channel: discord.TextChannel, subreddit: str):
        """
        ^tochannel #channel <subreddit>
        Example: ^tochannel #general Python
        """
        subreddit = subreddit.lower().lstrip("r/")
        if subreddit not in self.monitored_subreddits:
            return await ctx.send(f"r/{subreddit} is not being monitored. Add it using ^addreddit.")

        self.monitored_subreddits[subreddit]["channel_id"] = channel.id
        await ctx.send(f"r/{subreddit} auto feed channel set to {channel.mention}.")

async def setup(bot):
    await bot.add_cog(RedditPostCallout(bot))
