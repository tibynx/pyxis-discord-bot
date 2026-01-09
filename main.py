import os
import discord
from discord.ext import commands
from config import BOT_TOKEN, SYNC_GUILD

# Set intents
intents = discord.Intents.default()

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        # No prefix since we use app commands
        super().__init__(command_prefix="", intents=intents)

    # Load cogs
    async def load_cogs(self) -> None:
        for file in os.listdir(os.path.join(os.path.realpath(os.path.dirname(__file__)), "cogs")):
            if file.endswith(".py"): # Only load python files
                extension = file[:-3]
                try:
                    await self.load_extension(f"cogs.{extension}")
                    print(f"Loaded extension '{extension}'")
                except Exception as error:
                    print(f"Failed to load extension '{extension}'")
                    print(error)


    async def setup_hook(self) -> None:
        print(f"Logged in as {self.user.name}#{self.user.discriminator} (User ID: {self.user.id})")
        print(f"discord.py version: {discord.__version__}")
        print("-------------------")
        await self.load_cogs()

        # Sync global commands
        try:
            synced_global = await self.tree.sync()
            print(f"Synced {len(synced_global)} global commands.")
        except Exception as e:
            print(f"Failed to sync global commands: {e}")

        # Sync specific guild commands
        guild = discord.Object(id=SYNC_GUILD)
        try:
            synced_guild = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced_guild)} commands to Guild ID {guild.id}.")
        except Exception as e:
            print(f"Failed to sync guild commands: {e}")


# Run the bot
bot = DiscordBot()
bot.run(BOT_TOKEN)