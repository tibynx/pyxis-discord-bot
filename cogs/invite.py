"""Cog for invite related commands"""
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from config import (
    SYNC_GUILD, TARGET_GUILD, TARGET_CHANNEL, INVITE_TIMEOUT,
    ONLINE_MEMBER_INDICATOR, TOTAL_MEMBER_INDICATOR
)

# Invite dialog
class InviteDialog(discord.ui.LayoutView):
    def __init__(
        self, interaction: discord.Interaction,
        target_guild: discord.Guild, invite_url: str
    ):
        """Initialize the invite dialog view."""
        super().__init__(timeout=INVITE_TIMEOUT + 2.5)
        self.interaction = interaction
        self.target_guild = target_guild
        self.invite_url = invite_url

        # Count guild members
        total_members = (
            target_guild.member_count
            if target_guild.member_count is not None
            else len(target_guild.members)
        )
        online_members = len([
            member for member in target_guild.members
            if member.status != discord.Status.offline
        ])

        # Get guild description
        # Due to a Discord bug, guild descriptions are sometimes empty
        if target_guild.description:
            guild_description = f"\n{target_guild.description}"
        else:
            guild_description = ""

        container = discord.ui.Container()
        container.add_item(
            discord.ui.TextDisplay(
                f"-# You have been invited to join **{target_guild.name}**! "
                f"This invite expires "
                f"<t:{int(self.interaction.created_at.timestamp()) + INVITE_TIMEOUT + 2}:R>."
            )
        )
        container.add_item(discord.ui.Separator())
        section = discord.ui.Section(
            discord.ui.TextDisplay(
                f"## {target_guild.name}\n{ONLINE_MEMBER_INDICATOR}{online_members} Online  "
                f"{TOTAL_MEMBER_INDICATOR}{total_members} Members\n"
                f"Est. {target_guild.created_at.strftime('%b')} {target_guild.created_at.year}\n"
                f"{guild_description}"
            ),
            accessory=discord.ui.Thumbnail(
                target_guild.icon.url if target_guild.icon else None
                )
        )
        invite_button = discord.ui.ActionRow(discord.ui.Button(
            label="Join Server", style=discord.ButtonStyle.link, url=invite_url
        ))
        container.add_item(section)
        container.add_item(invite_button)
        self.add_item(container)

    async def on_timeout(self):
        """Handle timeout by deleting the dialog message."""
        try:
            await self.interaction.delete_original_response()
        except (discord.HTTPException, discord.NotFound):
            pass


class Invite(commands.Cog):
    """Invite related commands"""
    def __init__(self, bot: commands.Bot):
        """Initialize the Invite cog."""
        self.bot = bot
        # Track active invites per user {user_id: (invite, task)}
        self.active_invites = {}

    async def _cleanup_invite(self, user_id: int, delay: int) -> None:
        """Clean up an invite after the specified delay."""
        await asyncio.sleep(delay)
        if user_id in self.active_invites:
            invite, _ = self.active_invites[user_id]
            try:
                await invite.delete(reason="Invite expired")
            except (discord.HTTPException, discord.NotFound):
                pass
            finally:
                self.active_invites.pop(user_id, None)

    @app_commands.command(
        name="join",
        description="Get a personal invite link to join the target server"
    )
    @app_commands.guilds(*([discord.Object(id=SYNC_GUILD)] if SYNC_GUILD else []))
    async def join_command(self, interaction: discord.Interaction) -> None:
        """Generate a personal invite link to the target server."""
        # Defer response since invite creation might take a moment
        await interaction.response.defer(ephemeral=True)

        # Check if user already has an active invite
        if interaction.user.id in self.active_invites:
            await interaction.followup.send(
                "You already have an active invite link. "
                "Please wait for it to expire before requesting a new one.",
                ephemeral=True
            )
            return

        # Validate TARGET_GUILD is configured
        if not TARGET_GUILD:
            await interaction.followup.send(
                "Target server is not configured. "
                "Please contact the bot administrator.",
                ephemeral=True
            )
            return

        # Validate TARGET_CHANNEL is configured
        if not TARGET_CHANNEL:
            await interaction.followup.send(
                "Target channel is not configured. "
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

        # Get the specific channel to create the invite from
        invite_channel = target_guild.get_channel(int(TARGET_CHANNEL))
        if not invite_channel:
            await interaction.followup.send(
                "I cannot find the configured channel "
                "in the target server.",
                ephemeral=True
            )
            return

        # Check if bot has permission to create invites in this channel
        if not invite_channel.permissions_for(target_guild.me).create_instant_invite:
            await interaction.followup.send(
                "I don't have permission to create invites "
                "in the configured channel.",
                ephemeral=True
            )
            return

        # Create the invite with specified parameters
        try:
            invite = await invite_channel.create_invite(
                max_age=INVITE_TIMEOUT,  # One-time use invite timeout
                max_uses=1,  # One-time use only
                unique=True,  # Generate a unique invite
                reason=f"Invite link for {interaction.user} (User ID: {interaction.user.id})")

            # Track the invite and schedule cleanup
            cleanup_task = asyncio.create_task(
                self._cleanup_invite(interaction.user.id, INVITE_TIMEOUT)
            )
            self.active_invites[interaction.user.id] = (invite, cleanup_task)

            # Send the invite as an ephemeral message
            await interaction.followup.send(
                view=InviteDialog(interaction, target_guild, invite.url),
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create invites "
                "in the target server.",
                ephemeral=True
            )

async def setup(bot: commands.Bot) -> None:
    """Load the Invite cog."""
    await bot.add_cog(Invite(bot))
