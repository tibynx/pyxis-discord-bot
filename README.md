# 🧭 Pyxis
Pyxis is a Discord bot to invite members and manage your server.

## Commands

| Command         | Description                                                                |
|-----------------|----------------------------------------------------------------------------|
| `/join`         | Generates an invite link for the configured server.                        |
| `/purgeinvites` | Deletes all server invites.                                                |
| `/lockserver`   | Enables security actions. Disables server invites and DMs between members. |
| `/unlockserver` | Disables security actions.                                                 |

## Setup and Configuration

Create an application on the [Discord Developer Portal](https://discord.com/developers/applications), and copy the application ID and the bot token for later.
In your Discord client, enable Developer Mode in User Settings > Advanced. Right-click on a server icon or channel and select "Copy ID" to get the IDs.

### Source

Clone the repo and install all required packages! Make sure you have at least Python 3.14 installed!

```sh
git clone https://github.com/tibynx/pyxis.git
cd pyxis/
pip install -r requirements.txt
```

In the meantime, create an `.env` file according to the `.env.example` file! Do not share your bot token with anyone!

```sh
BOT_TOKEN="your_bot_token_here"
SYNC_GUILD="your_server_id_here"
TARGET_GUILD="your_server_id_here"
TARGET_CHANNEL="your_channel_id_here"
INVITE_TIMEOUT="300" #optional
ONLINE_MEMBER_INDICATOR="🟢" #optional
TOTAL_MEMBER_INDICATOR="⚪" #optional
```

Then, you can run the bot using the `python main.py` command!

### Environment Variables

|        Variable         | Description                                                                                   |
|:-----------------------:|-----------------------------------------------------------------------------------------------|
|        BOT_TOKEN        | Your bot token. Do not share this with anyone!                                                |
|       SYNC_GUILD        | The ID of the server where the `/join` command will be available.                             |
|      TARGET_GUILD       | The ID of the server where the invites will be created.                                       |
|     TARGET_CHANNEL      | The ID of the channel where the invites will be created. This has to be in the TARGET_GUILD.  |
|     INVITE_TIMEOUT      | (Optional) The time in seconds before the invites expire. Default is 5 minutes (300 seconds). |
| ONLINE_MEMBER_INDICATOR | (Optional) The emoji used to indicate online members in the invite message.                   |
| TOTAL_MEMBER_INDICATOR  | (Optional) The emoji used to indicate total members in the invite message.                    |

The emoji format can be either a Unicode emoji (e.g., 👥) or a custom emoji in the format `<a:name:id>` (e.g., `<a:people:733395207222984794>`). The bot must be in the server where the custom emoji is from or added to the bot on the Discord Developer Portal to use it.