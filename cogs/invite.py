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
    """Dialog view for invites."""
    def __init__(
        self, interaction: discord.Interaction,
        target_guild: discord.Guild, invite_url: str, expires_timestamp: int
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
                f"This invite expires <t:{expires_timestamp}:R>."
            )
        )
        container.add_item(discord.ui.Separator())
        details = discord.ui.TextDisplay(
            f"## {target_guild.name}\n{ONLINE_MEMBER_INDICATOR}{online_members} Online  "
            f"{TOTAL_MEMBER_INDICATOR}{total_members} Members\n"
            f"Est. {target_guild.created_at.strftime('%b')} {target_guild.created_at.year}\n"
            f"{guild_description}"
        )

        if target_guild.icon:
            section = discord.ui.Section(details, accessory=discord.ui.Thumbnail(target_guild.icon.url))
        else:
            section = details

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
        # Track active invites per user {user_id: (invite_object, cleanup_task, interaction)}
        self.active_invites = {}
        # Track invite code to intended user mapping {invite_code: user_id}
        self.invite_to_user = {}

    async def _cleanup_invite(self, user_id: int, invite: discord.Invite) -> None:
        """Clean up an invite after the timeout."""
        await asyncio.sleep(INVITE_TIMEOUT)
        if user_id in self.active_invites:
            stored_invite, _, _ = self.active_invites[user_id]
            if stored_invite == invite:
                try:
                    await invite.delete(reason="Invite expired")
                except (discord.HTTPException, discord.NotFound):
                    pass
                finally:
                    self.active_invites.pop(user_id, None)
                    # Also remove from invite mapping
                    self.invite_to_user.pop(invite.code, None)

    async def _create_invite_for_user(
            self, user_id: int, reason: str, interaction: discord.Interaction = None
    ) -> discord.Invite:
        """Create a new invite for a specific user.

        Returns the created invite object or None if creation failed.
        """
        target_guild = self.bot.get_guild(TARGET_GUILD)
        if not target_guild:
            return None

        invite_channel = target_guild.get_channel(TARGET_CHANNEL)
        if not invite_channel:
            return None

        if not invite_channel.permissions_for(target_guild.me).create_instant_invite:
            return None

        try:
            # Create the invite with specified parameters
            invite = await invite_channel.create_invite(
                max_age=INVITE_TIMEOUT,
                max_uses=1,
                unique=True,
                reason=reason
            )

            # Track the invite and schedule cleanup
            task = asyncio.create_task(self._cleanup_invite(user_id, invite))
            self.active_invites[user_id] = (invite, task, interaction)
            # Map invite code to intended user
            self.invite_to_user[invite.code] = user_id

            return invite
        except (discord.Forbidden, discord.HTTPException):
            return None

    @app_commands.command(
        name="join",
        description="Get a personal invite link to join the target server"
    )
    @app_commands.guilds(*([discord.Object(id=SYNC_GUILD)] if SYNC_GUILD else []))
    async def join_command(self, interaction: discord.Interaction) -> None:
        """Generate a personal invite link to the target server."""
        # Defer response since invite creation might take a moment
        await interaction.response.defer(ephemeral=True)

        user_id = interaction.user.id
        # Spam prevention: Check if the user already has an active invite
        if user_id in self.active_invites:
            await interaction.followup.send(
                "You already have an active invite link. "
                "Please wait for it to expire before requesting a new one.",
                ephemeral=True
            )
            return

        # Validate configuration
        if not TARGET_GUILD or not TARGET_CHANNEL:
            await interaction.followup.send(
                "Target server or channel is not configured. "
                "Please contact the bot administrator.",
                ephemeral=True
            )
            return

        # Get the target guild
        target_guild = self.bot.get_guild(TARGET_GUILD)
        if not target_guild:
            await interaction.followup.send(
                "I cannot find the target server. Make sure I'm added to it.",
                ephemeral=True
            )
            return

        # Check if the user is already in the target server
        if target_guild.get_member(user_id):
            await interaction.followup.send(
                "You are already a member of the target server.",
                ephemeral=True
            )
            return

        # Get the specific channel to create the invite from
        invite_channel = target_guild.get_channel(TARGET_CHANNEL)
        if not invite_channel:
            await interaction.followup.send(
                "I cannot find the configured channel in the target server.",
                ephemeral=True
            )
            return

        # Check if the bot has permission to create invites in this channel
        if not invite_channel.permissions_for(target_guild.me).create_instant_invite:
            await interaction.followup.send(
                "I don't have permission to create invites in the configured channel.",
                ephemeral=True
            )
            return

        try:
            # Create the invite with specified parameters
            invite = await self._create_invite_for_user(
                user_id,
                f"Invite link for {interaction.user} (User ID: {user_id})",
                interaction
            )

            if not invite:
                await interaction.followup.send(
                    "Failed to create an invite. Please try again later.",
                    ephemeral=True
                )
                return

            expires_timestamp = int(interaction.created_at.timestamp()) + INVITE_TIMEOUT

            # Send the invite as an ephemeral message
            await interaction.followup.send(
                view=InviteDialog(interaction, target_guild, invite.url, expires_timestamp),
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create invites in the target server.",
                ephemeral=True
            )
        except Exception as e:
            await interaction.followup.send(
                f"An error occurred while creating the invite: {e}",
                ephemeral=True
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        """Handle member join events to verify invite usage."""
        # Only check joins to the target guild
        if member.guild.id != TARGET_GUILD:
            return

        # Skip if we have no tracked invites
        if not self.invite_to_user:
            return

        # Get all current invites in the guild
        try:
            current_invites = await member.guild.invites()
        except (discord.Forbidden, discord.HTTPException):
            # Can't check invites if we don't have permission
            return

        # Build a set of current invite codes
        current_invite_codes = {inv.code for inv in current_invites}

        # Check which of our tracked invites is missing (was used)
        # We only check tracked invites that are missing to avoid false positives
        used_invite_code = None
        intended_user_id = None

        for invite_code, user_id in list(self.invite_to_user.items()):
            # If this tracked invite is no longer in the current invites, it might have been used
            if invite_code not in current_invite_codes:
                # Double-check: this invite should have been in active_invites
                # If it's not, it was already cleaned up (expired/deleted) and this is a false alarm
                if user_id in self.active_invites:
                    stored_invite, _, _ = self.active_invites[user_id]
                    if stored_invite.code == invite_code:
                        # This is a legitimate tracked invite that was just used
                        used_invite_code = invite_code
                        intended_user_id = user_id
                        break
                else:
                    # This invite was already cleaned up, remove it from tracking
                    self.invite_to_user.pop(invite_code, None)

        # If we found a used invite, verify the user
        if used_invite_code and intended_user_id:
            # Get the stored interaction before cleaning up
            _, task, stored_interaction = self.active_invites.get(intended_user_id, (None, None, None))

            # Clean up the tracking for the old invite first
            self.invite_to_user.pop(used_invite_code, None)
            if intended_user_id in self.active_invites:
                stored_invite, task, _ = self.active_invites[intended_user_id]
                if stored_invite.code == used_invite_code:
                    task.cancel()  # Cancel the cleanup task
                    self.active_invites.pop(intended_user_id, None)

            # Check if the member who joined is the intended user
            if member.id != intended_user_id:
                # This is impersonation - kick the member
                try:
                    await member.kick(
                        reason=f"Unauthorized use of invite link intended for user ID {intended_user_id}"
                    )
                    self.bot.logger.warning(
                        "Kicked user %s (User ID: %s) for using invite intended for User ID %s",
                        member, member.id, intended_user_id
                    )
                except (discord.Forbidden, discord.HTTPException) as e:
                    self.bot.logger.error(
                        "Failed to kick user %s (User ID: %s) for impersonation: %s",
                        member, member.id, e
                    )

                # Create a new invite for the intended user since theirs was consumed
                new_invite = await self._create_invite_for_user(
                    intended_user_id,
                    f"Replacement invite for User ID {intended_user_id} after impersonation attempt",
                    stored_interaction
                )

                if new_invite and stored_interaction:
                    # Try to send followup message to the original interaction
                    try:
                        target_guild = self.bot.get_guild(TARGET_GUILD)
                        expires_timestamp = int(discord.utils.utcnow().timestamp()) + INVITE_TIMEOUT
                        await stored_interaction.followup.send(
                            f"⚠️ Someone tried to use your invite link to **{target_guild.name}**. "
                            f"They have been kicked and a new invite has been created for you.\n\n"
                            f"Your new invite link: {new_invite.url}\n"
                            f"This invite expires <t:{expires_timestamp}:R>.",
                            ephemeral=True
                        )
                        self.bot.logger.info(
                            "Created replacement invite for User ID %s and sent followup notification",
                            intended_user_id
                        )
                    except (discord.HTTPException, discord.NotFound) as e:
                        # If followup fails, log it
                        self.bot.logger.warning(
                            "Created replacement invite for User ID %s but could not send followup: %s",
                            intended_user_id, e
                        )
                else:
                    self.bot.logger.error(
                        "Failed to create replacement invite for User ID %s after impersonation",
                        intended_user_id
                    )
            else:
                # Correct user joined - log success
                self.bot.logger.info(
                    "User %s (User ID: %s) successfully joined using their invite",
                    member, member.id
                )

async def setup(bot: commands.Bot) -> None:
    """Load the Invite cog."""
    await bot.add_cog(Invite(bot))
