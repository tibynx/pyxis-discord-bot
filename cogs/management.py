"""Cog for guild management commands."""
from datetime import timedelta
import discord
from discord.ext import commands
from discord import app_commands

class Management(commands.Cog):
    """Management related commands"""
    def __init__(self, bot: commands.Bot):
        """Initialize the Management cog."""
        self.bot = bot

    # Pause guild invites and DMs
    @app_commands.command(
        name="lockserver",
        description="Pause server invites and DMs between members. "
                    "Doesn't restrict DMs for friends, mods, or apps."
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    @app_commands.choices(duration=[
        discord.app_commands.Choice(name="30 minutes", value=1800),
        discord.app_commands.Choice(name="1 hour", value=3600),
        discord.app_commands.Choice(name="2 hours", value=7200),
        discord.app_commands.Choice(name="4 hours", value=14400),
        discord.app_commands.Choice(name="6 hours", value=21600),
        discord.app_commands.Choice(name="12 hours", value=43200),
        discord.app_commands.Choice(name="1 day", value=86400)
    ])
    @app_commands.describe(
        duration="The duration enable security actions for"
    )
    async def enable_security_actions(
            self, interaction: discord.Interaction,
            duration: discord.app_commands.Choice[int]
    ) -> None:
        """Pause invites and DMs for the specified duration."""
        time = discord.utils.utcnow() + timedelta(seconds=duration.value)
        try:
            await interaction.guild.edit(
                invites_disabled_until=time,
                dms_disabled_until=time,
                reason=f"Enabled security actions by {interaction.user} (User ID: {interaction.user.id})"
            )
            await interaction.response.send_message(
                f"Enabled security actions until <t:{int(time.timestamp())}:f>.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to enable security actions.",
                ephemeral=True
            )

    # Resume guild invites and DMs
    @app_commands.command(
        name="unlockserver",
        description="Resume accepting invites and private messages between members."
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def disable_security_actions(self, interaction: discord.Interaction) -> None:
        """Resume accepting invites and private messages between members."""
        if not interaction.guild.invites_paused() and not interaction.guild.dms_paused():
            await interaction.response.send_message(
                "Security actions are not enabled.",
                ephemeral=True
            )
            return
        try:
            await interaction.guild.edit(
                invites_disabled_until=None,
                dms_disabled_until=None,
                reason=f"Invites resumed by {interaction.user} (User ID: {interaction.user.id})"
            )
            await interaction.response.send_message(
                "Disabled security actions.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to disable security actions.",
                ephemeral=True
            )

    # Purge all invites
    @app_commands.command(
        name="purgeinvites",
        description="Purge all server invites."
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def purge_invites(self, interaction: discord.Interaction):
        """Purge all server invites."""
        await interaction.response.defer(ephemeral=True)
        try:
            for invite in await interaction.guild.invites():
                await invite.delete(
                    reason=f"Invites purged by {interaction.user} (User ID: {interaction.user.id})"
                )
            await interaction.followup.send(
                "All server invites have been deleted.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to delete invites.",
                ephemeral=True
            )

async def setup(bot: commands.Bot) -> None:
    """Load the Management cog."""
    await bot.add_cog(Management(bot))