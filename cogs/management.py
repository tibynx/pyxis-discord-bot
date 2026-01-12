"""Cog for guild management commands."""
from datetime import timedelta
import discord
from discord.ext import commands
from discord import app_commands

class Management(commands.Cog):
    """Cog for guild management and security commands."""
    def __init__(self, bot: commands.Bot) -> None:
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
        app_commands.Choice(name="30 minutes", value=1800),
        app_commands.Choice(name="1 hour", value=3600),
        app_commands.Choice(name="2 hours", value=7200),
        app_commands.Choice(name="4 hours", value=14400),
        app_commands.Choice(name="6 hours", value=21600),
        app_commands.Choice(name="12 hours", value=43200),
        app_commands.Choice(name="1 day", value=86400)
    ])
    @app_commands.describe(
        duration="The duration to enable security actions for"
    )
    async def lock_server(
            self, interaction: discord.Interaction,
            duration: int
    ) -> None:
        """Pause invites and DMs for the specified duration."""
        until = discord.utils.utcnow() + timedelta(seconds=duration)
        try:
            await interaction.guild.edit(
                invites_disabled_until=until,
                dms_disabled_until=until,
                reason=f"Security actions enabled by {interaction.user} (ID: {interaction.user.id})"
            )
            await interaction.response.send_message(
                f"Security actions enabled until <t:{int(until.timestamp())}:f>.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to modify guild security settings.",
                ephemeral=True
            )

    # Resume guild invites and DMs
    @app_commands.command(
        name="unlockserver",
        description="Resume accepting invites and private messages between members."
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def unlock_server(self, interaction: discord.Interaction) -> None:
        """Resume accepting invites and private messages between members."""
        guild = interaction.guild
        now = discord.utils.utcnow()

        invites_paused = guild.invites_disabled_until and guild.invites_disabled_until > now
        dms_paused = guild.dms_disabled_until and guild.dms_disabled_until > now

        if not invites_paused and not dms_paused:
            await interaction.response.send_message(
                "Security actions are not currently active.",
                ephemeral=True
            )
            return
        try:
            await guild.edit(
                invites_disabled_until=None,
                dms_disabled_until=None,
                reason=f"Security actions disabled by {interaction.user} (ID: {interaction.user.id})"
            )
            await interaction.response.send_message(
                "Successfully disabled security actions.",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "I don't have permission to modify guild security settings.",
                ephemeral=True
            )

    # Purge all invites
    @app_commands.command(
        name="purgeinvites",
        description="Purge all active server invites."
    )
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def purge_invites(self, interaction: discord.Interaction) -> None:
        """Purge all server invites."""
        await interaction.response.defer(ephemeral=True)
        try:
            invites = await interaction.guild.invites()
            if not invites:
                await interaction.followup.send("No active invites found to delete.", ephemeral=True)
                return

            count = 0
            for invite in invites:
                await invite.delete(
                    reason=f"Purge requested by {interaction.user} (ID: {interaction.user.id})"
                )
                count += 1

            await interaction.followup.send(
                f"Successfully deleted {count} server {'invite' if count == 1 else 'invites'}.",
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