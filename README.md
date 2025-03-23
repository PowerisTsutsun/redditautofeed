# Discord Reddit Bot

This Discord bot fetches posts from Reddit and automatically posts them to specified channels. It supports manual commands to fetch a random post, add/remove subreddits from the monitored list, toggle auto-feed on/off, and set custom channels for auto feeds. The bot uses Async PRAW for asynchronous Reddit API access and discord.py for Discord integration.

## Features

- **Manual Post Fetching:**  
  Use `^reddit <subreddit>` to manually fetch a random post from a monitored subreddit with image previews if available.

- **Subreddit Management:**  
  - `^addreddit <subreddit>`: Add a subreddit to the monitored list.  
  - `^removereddit <subreddit>`: Remove a subreddit from the monitored list.  
  - `^listreddit`: List all monitored subreddits.

- **Auto Feed Toggle:**  
  Use `^reddit <subreddit> on` or `^reddit <subreddit> off` to enable or disable automatic posting for a subreddit every 2 minutes.

- **Channel Configuration:**  
  Use `^tochannel #channel <subreddit>` to set the Discord channel where auto-feed posts for a specific subreddit will be sent.

## Setup

### 1. Clone the Repository

```
git clone <repository-url>
cd <repository-directory>



2. Create a Virtual Environment (Optional)

python -m venv venv
Activate the environment:

Linux/Mac:


source venv/bin/activate
Windows:


venv\Scripts\activate
3. Install Dependencies

pip install -r requirements.txt
4. Create a .env File
In the project root, create a file named .env with the following content:

DISCORD_TOKEN=your-discord-bot-token
REDDIT_CLIENT_ID=your-reddit-client-id
REDDIT_CLIENT_SECRET=your-reddit-client-secret
REDDIT_USER_AGENT=discord:yourbotname:v1.0.0 (by /u/yourusername)
Replace the placeholder values with your actual credentials.

5. Run the Bot

python bot.py


#Commands
^addreddit <subreddit>
Adds a subreddit to the monitored list.

^removereddit <subreddit>
Removes a subreddit from the monitored list.

^listreddit
Lists all monitored subreddits along with their auto-feed status and channel configuration.

^reddit <subreddit>
Manually fetches a random post from a monitored subreddit.

^reddit <subreddit> on/off
Toggles auto-feed for the specified subreddit on or off.

^tochannel #channel <subreddit>
Sets the channel for auto-feed posts for the specified subreddit.

License
This project is licensed under the MIT License.

Contributing
Feel free to fork the repository and submit pull requests if you have any improvements or new features.


---

You can now include these files in your repository on GitHub. Enjoy sharing your Discord Reddit Bot!
