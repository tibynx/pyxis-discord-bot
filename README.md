# 🧭 Pyxis

Pyxis is a versatile Discord bot designed to streamline member invitations and enhance server security. It allows your server members to create one-time-use invite links that they can only use. It's perfect for creating a secure private server, ban appeals, or games. Additionally, it provides powerful management tools to lock down your server in case of raids or other security concerns.

## Features

- **Secure One-Time Invites**: Generates unique, one-time-use invite links for specific users.
- **Impersonation Protection**: Automatically detects and kicks unauthorized users who attempt to join using someone else's invite link.
- **Server Lockdown Mode**: Instantly pause invites and DMs between members to protect against raids.
- **Bulk Invite Purging**: Quickly clear all active invites on the server with a single command.
- **Configurable Timeout & Indicators**: Customize invite expiration times and status emojis.

## Commands

| Command         | Description                                                                |
|-----------------|----------------------------------------------------------------------------|
| `/join`         | Generates an invite link for the configured server.                        |
| `/purgeinvites` | Deletes all server invites.                                                |
| `/lockserver`   | Enables security actions. Disables server invites and DMs between members. |
| `/unlockserver` | Disables security actions.                                                 |

## Setup and Configuration

Create an application on the [Discord Developer Portal](https://discord.com/developers/applications), and copy the application ID and the bot token for later.
Under the "Bot" tab, enable the "Server Members Intent" and "Presence Intent" options for the bot.
In your Discord client, enable Developer Mode in User Settings > Advanced. This is needed for setup. Right-click on a server icon or channel and select "Copy ID" to get the IDs.

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

|        Variable         | Description                                                                                  |
|:-----------------------:|----------------------------------------------------------------------------------------------|
|        BOT_TOKEN        | Your bot token. Do not share this with anyone!                                               |
|       SYNC_GUILD        | The ID of the server where the `/join` command will be available.                            |
|      TARGET_GUILD       | The ID of the server where the invites will be created.                                      |
|     TARGET_CHANNEL      | The ID of the channel where the invites will be created. This has to be in the TARGET_GUILD. |
|     INVITE_TIMEOUT      | (Optional) The time in seconds before the invites expire. The default is 5 minutes.          |
| ONLINE_MEMBER_INDICATOR | (Optional) The emoji used to indicate online members in the invite message.                  |
| TOTAL_MEMBER_INDICATOR  | (Optional) The emoji used to indicate total members in the invite message.                   |

The emoji format can be either a Unicode emoji (e.g., 👥) or a custom emoji in the format `<a:name:id>` (e.g., `<a:people:733395207222984794>`). The bot must be in the server where the custom emoji is from or added to the bot on the Discord Developer Portal to use it.

## Usage

After setting up, invite your bot to the servers using this premade link! It already contains the proper permissions. Replace `<app-id>` with your bot's application ID.
Make sure to invite the bot to both the `SYNC_GUILD` and `TARGET_GUILD` servers!

```sh
https://discord.com/oauth2/authorize?client_id=<app-id>&permissions=35&integration_type=0&scope=bot+applications.commands
```

> [!TIP]
> * You can restrict the `/join` command to specific roles or channels in the "Integrations" tab in your server settings!.
