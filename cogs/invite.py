import discord
from discord.ext import commands
from discord import app_commands
from config import SYNC_GUILD

guild = discord.Object(id=SYNC_GUILD)

class Invite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # This command will ONLY appear in the specified guild
    @app_commands.command(name="test", description="A server-specific command")
    @app_commands.guilds(guild)
    async def test_command(self, interaction: discord.Interaction):
        await interaction.response.send_message("tesing", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Invite(bot))