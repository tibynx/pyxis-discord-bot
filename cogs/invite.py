"""Cog for invite related commands"""
import discord
from discord.ext import commands
from discord import app_commands
from config import SYNC_GUILD, TARGET_GUILD

guild = discord.Object(id=SYNC_GUILD)


class Invite(commands.Cog):
    """Invite related commands"""
    def __init__(self, bot):
        """Initialize the Invite cog."""
        self.bot = bot

    @app_commands.command(
        name="join",
        description="Get a personal invite link to join the target server"
    )
    @app_commands.guilds(guild)
    async def join_command(self, interaction: discord.Interaction) -> None:
        """Generate a personal invite link to the target server."""
        # Defer response since invite creation might take a moment
        await interaction.response.defer(ephemeral=True)

        # Validate TARGET_GUILD is configured
        if not TARGET_GUILD:
            await interaction.followup.send(
                "Target server is not configured. "
                "Please contact the bot administrator.",
                ephemeral=True
            )
            return

        # Get the target guild
        target_guild = self.bot.get_guild(int(TARGET_GUILD))
        if not target_guild:
            await interaction.followup.send(
                "I cannot find the target server. "
                "Make sure I'm added to it.",
                ephemeral=True
            )
            return

        # Find a suitable channel to create the invite from
        # Prefer the first text channel where the bot has create_instant_invite
        invite_channel = None
        for channel in target_guild.text_channels:
            if channel.permissions_for(target_guild.me).create_instant_invite:
                invite_channel = channel
                break

        if not invite_channel:
            await interaction.followup.send(
                "I don't have permission to create invites "
                "in the target server.",
                ephemeral=True
            )
            return

        # Create the invite with specified parameters
        try:
            invite = await invite_channel.create_invite(
                max_age=600,  # Expires in 10 minutes (600 seconds)
                max_uses=1,  # One-time use only
                unique=True,  # Generate a unique invite
                reason=f"Personal invite for {interaction.user} "
                       f"(ID: {interaction.user.id})"
            )

            # Send the invite as an ephemeral message
            await interaction.followup.send(
                f"Here's your personal invite link to **{target_guild.name}**:\n"
                f"{invite.url}\n\n"
                f"This link expires in 10 minutes and can only be used once.",
                ephemeral=True,
                delete_after=600  # Delete the message after 10 minutes
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create invites "
                "in the target server.",
                ephemeral=True
            )
        except discord.HTTPException as e:
            await interaction.followup.send(
                f"Failed to create invite: {e}",
                ephemeral=True
            )


async def setup(bot):
    """Load the Invite cog."""
    await bot.add_cog(Invite(bot))
