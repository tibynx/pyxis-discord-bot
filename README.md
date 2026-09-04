# 🧭 Pyxis

Pyxis is a versatile Discord bot designed to streamline member invitations and enhance server security.

It allows your server members to create one-time-use invite links that they can only use. It's perfect for creating a secure private server, ban appeals, or games. Additionally, it provides powerful management tools to lock down your server in case of raids or other security concerns.

## Features

- Generate unique, one-time-use invite links for specific users.
- Automatically detects and kicks unauthorized users who attempt to join using someone else's invite link.
- Instantly pause invites and DMs between members to protect against raids.
- Quickly clear all active invites on the server with a single command.

## Setup

### Prequisites

1. Create an application on the [Discord Developer Portal](https://discord.com/developers/applications)
    - Click "New Application" and give it a name.
    - Note down the Application ID for later.
    - Go to the "Bot" tab and click "Add Bot".
    - Under "TOKEN", click "Copy" to copy your bot token. (You might need to reset it to see it.)
    - Enable the "Server Members Intent" and "Presence Intent" options.
2. Enable developer mode in Discord to copy guild and channel IDs
    - Go to User Settings > Advanced > Developer Mode and enable it.
3. Invite the bot to two Discord servers. One where you want your members to join from, and one where they gonna join to. You can use the premade link in the usage section.

Now choose one of the following methods to run the bot!

### Docker

1. Pull the latest image from Docker Hub
    ```sh
    docker pull tibynx/pyxis:latest
    ```
2. Run the container with the required environment variables and volume mounts
    - See the configuration section below for details! Only required options are included in this example.
    - On Discord, right-click on the server icon or channel and select "Copy ID" to get their IDs.
    - Change `/path/to/logs` to a directory on your host where you want to store the logs.
    ```sh
    docker run -d \
        --name=pyxis \
        -e BOT_TOKEN="your_bot_token_here" \
        -e SYNC_GUILD="your_server_id_here" \
        -e TARGET_GUILD="your_server_id_here" \
        -e TARGET_CHANNEL="your_channel_id_here" \
        -v /path/to/logs:/app/logs \
        tibynx/pyxis:latest
    ```

### Source

1. Install **[Python 3.14 or newer](https://www.python.org/downloads/)**
2. Clone the repository and install all required packages!
    ```sh
    git clone https://github.com/tibynx/pyxis.git
    cd pyxis
    ```
    ```sh
    pip install -r requirements.txt
    ```
3. Copy `.env.example` to `.env` and configure your settings.
    - See the configuration section below for details!
    - On Discord, right-click on the server icon or channel and select "Copy ID" to get their IDs.
    - **Do not share your `.env` file publicly!**
4. Invite the bot to a Discord server
   - You can use the premade link in the usage section.
5. Start the bot
   ```sh
   python main.py
   ```

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

### Set custom description for /join

Using the `COMMAND_DESCRIPTION` variable, you can set a custom description for the `/join` command that can be seen by users in Discord. The description can be between **1 and 100** characters long.

## Usage

### Invite

Invite your bot to the servers using this premade link! It already contains the proper permissions. Replace `YOUR_APP_ID` with your bot's Application ID.
**Make sure to invite the bot to both the `SYNC_GUILD` and `TARGET_GUILD` servers!**

```text
https://discord.com/oauth2/authorize?client_id=YOUR_APP_ID&permissions=35&integration_type=0&scope=bot+applications.commands
```

### Commands

| Command         | Description                                                                |
|-----------------|----------------------------------------------------------------------------|
| `/join`         | Generates an invite link for the configured server.                        |
| `/purgeinvites` | Deletes all server invites.                                                |
| `/lockserver`   | Enables security actions. Disables server invites and DMs between members. |
| `/unlockserver` | Disables security actions.                                                 |
| `/enablejoin`   | Enables members to join the `TARGET_SERVER` via the `/join` command.       |
| `/disablejoin`  | Disables members from joining the `TARGET_SERVER` via the `/join` command. |

> [!NOTE]
> `/lockserver`, `/unlockserver`, and `/purgeinvites` operate on whichever server they are executed in.

> [!TIP]
> * You can restrict the `/join` command to specific roles or channels using the "Integrations" tab in your server settings!
