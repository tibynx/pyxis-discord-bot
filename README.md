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
| `/enablejoin`   | Enables members to join the `TARGET_SERVER` via the `/join` command.       |
| `/disablejoin`  | Disables members from joining the `TARGET_SERVER` via the `/join` command. |

## Setup

1. Clone the repository and install all required packages! Python 3.14 is recommended!
    ```sh
    git clone https://github.com/tibynx/pyxis.git
    cd pyxis/
    pip install -r requirements.txt
    ```
2. Create an application on the [Discord Developer Portal](https://discord.com/developers/applications)
    - Click "New Application" and give it a name.
    - Note down the Application ID for later.
    - Go to the "Bot" tab and click "Add Bot".
    - Under "TOKEN", click "Copy" to copy your bot token. (You might need to reset it to see it.)
    - Enable the "Server Members Intent" and "Presence Intent" options.
3. Enable developer mode in Discord to copy guild and channel IDs
    - Go to User Settings > Advanced > Developer Mode and enable it.
4. Copy `.env.example` to `.env` and configure your settings.
    - See the configuration section below for details!
    - On Discord, right-click on the server icon or channel and select "Copy ID" to get the IDs.
    - **Do not share your `.env` file publicly!**
5. Invite the bot to both Discord servers using the premade link in the usage section.
6. Run `python main.py` to start the bot.

## Configuration

|         Variable          | Description                                                                                    |
|:-------------------------:|------------------------------------------------------------------------------------------------|
|        `BOT_TOKEN`        | Your bot token. Do not share this with anyone!                                                 |
|       `SYNC_GUILD`        | The ID of the server where the `/join` command will be available.                              |
|      `TARGET_GUILD`       | The ID of the server where the invites will be created.                                        |
|     `TARGET_CHANNEL`      | The ID of the channel where the invites will be created. This has to be in the `TARGET_GUILD`. |
|   `COMMAND_DESCRIPTION`   | (Optional) Custom description for the `/join` command.                                         |
|     `INVITE_TIMEOUT`      | (Optional) The time in seconds before the invites expire. (Default: 5 minutes)                 |
| `ONLINE_MEMBER_INDICATOR` | (Optional) The emoji used to indicate online members in the invite message.                    |
| `TOTAL_MEMBER_INDICATOR`  | (Optional) The emoji used to indicate total members in the invite message.                     |

The emoji format can be either a Unicode emoji (e.g., 👥) or a custom emoji in the format `<a:name:id>` (e.g., `<a:people:733395207222984794>`). The bot must be in the server where the custom emoji is from or added to the bot on the Discord Developer Portal to use it.

## Usage

Invite your bot to the servers using this premade link! It already contains the proper permissions. Replace `YOUR_APP_ID` with your bot's Application ID.
Make sure to invite the bot to both the `SYNC_GUILD` and `TARGET_GUILD` servers!

```text
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&permissions=35&integration_type=0&scope=bot+applications.commands
```

> [!TIP]
> * You can restrict the `/join` command to specific roles or channels using the "Integrations" tab in your server settings!.
> * You can also change the description of the `/join` command using the `COMMAND_DESCRIPTION` variable.
