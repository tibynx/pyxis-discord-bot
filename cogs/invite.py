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
        target_guild: discord.Guild, invite_msg: str, invite_url: str, expires_timestamp: int
    ):
        """Initialize the invite dialog view."""
        super().__init__(timeout=INVITE_TIMEOUT + 2.5)
        self.interaction = interaction
        self.target_guild = target_guild
        self.invite_url = invite_url

        # Count guild members
        # total_members = target_guild.member_count # member_count is more reliable than len(members)
        total_members = target_guild.member_count or len(target_guild.members)
        
        online_members = sum(
            1 for member in target_guild.members
            if member.status != discord.Status.offline
        )

        # Get guild description
        # Due to a Discord bug, guild descriptions are sometimes empty
        if target_guild.description:
            guild_description = f"\n{target_guild.description}"
        else:
            guild_description = ""

        # Customizable message
        message = discord.ui.TextDisplay(invite_msg)

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
            section = discord.ui.Section(
                details, accessory=discord.ui.Thumbnail(target_guild.icon.url)
            )
        else:
            section = details

        invite_button = discord.ui.ActionRow(discord.ui.Button(
            label="Join Server", style=discord.ButtonStyle.link, url=invite_url
        ))
        container.add_item(section)
        container.add_item(invite_button)
        self.add_item(message)
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
        # Track active invites per user {user_id: {'invite': invite_object, 'task': cleanup_task, 'interaction': interaction}}
        self.active_invites = {}
        # Track invite code to intended user mapping {invite_code: user_id}
        self.invite_to_user = {}
        # Lock for on_member_join to prevent race conditions
        self._join_lock = asyncio.Lock()

    async def _cleanup_invite(self, user_id: int, invite_code: str) -> None:
        """Clean up an invite after the timeout."""
        await asyncio.sleep(INVITE_TIMEOUT)
        async with self._join_lock:
            if user_id in self.active_invites:
                data = self.active_invites[user_id]
                if data['invite'].code == invite_code:
                    try:
                        await data['invite'].delete(reason="Invite expired")
                    except (discord.HTTPException, discord.NotFound):
                        pass
                    finally:
                        self.active_invites.pop(user_id, None)
                        self.invite_to_user.pop(invite_code, None)

    async def _create_invite_for_user(
            self, user_id: int, reason: str, interaction: discord.Interaction = None
    ) -> discord.Invite | None:
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
            task = asyncio.create_task(self._cleanup_invite(user_id, invite.code))
            self.active_invites[user_id] = {
                'invite': invite,
                'task': task,
                'interaction': interaction
            }
            # Map invite code to intended user
            self.invite_to_user[invite.code] = user_id

            return invite
        except (discord.Forbidden, discord.HTTPException):
            return None

    @app_commands.command(
        name="join",
        description="Get an invite link to join the server"
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
                "Please contact a moderator.",
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
                f"You are already a member of the **{target_guild.name}**!",
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

            invite_msg = f"Here is your invite to join **{target_guild.name}**!"
            expires_timestamp = int(interaction.created_at.timestamp()) + INVITE_TIMEOUT

            # Send the invite as an ephemeral message
            await interaction.followup.send(
                view=InviteDialog(
                    interaction, target_guild, invite_msg,
                    invite.url, expires_timestamp
                ),
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.followup.send(
                "I don't have permission to create invites in the target server.",
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

        async with self._join_lock:
            # We need to find which invite was used. 
            # Since we use max_uses=1, the invite disappears when used.
            try:
                current_invites = await member.guild.invites()
            except (discord.Forbidden, discord.HTTPException) as e:
                self.bot.logger.error("Failed to fetch invites for guild %s: %s", member.guild.id, e)
                return

            current_invite_codes = {inv.code for inv in current_invites}
            
            used_invite_code = None
            intended_user_id = None

            # Look for tracked invites that are no longer in the guild's invite list
            for invite_code, user_id in list(self.invite_to_user.items()):
                if invite_code not in current_invite_codes:
                    # Found a potentially used invite
                    if user_id in self.active_invites:
                        data = self.active_invites[user_id]
                        if data['invite'].code == invite_code:
                            used_invite_code = invite_code
                            intended_user_id = user_id
                            break
                    else:
                        # Stale tracking, remove it
                        self.invite_to_user.pop(invite_code, None)

            if not (used_invite_code and intended_user_id):
                return

            # Retrieve and clean up tracking before processing
            data = self.active_invites.pop(intended_user_id, None)
            self.invite_to_user.pop(used_invite_code, None)
            
            if data and data.get('task'):
                data['task'].cancel()
            
            stored_interaction = data.get('interaction') if data else None

            # Impersonation check
            if member.id != intended_user_id:
                self.bot.logger.warning(
                    "Impersonation detected! User %s (ID: %s) joined using invite intended for ID %s",
                    member, member.id, intended_user_id
                )
                
                try:
                    await member.kick(
                        reason=f"Unauthorized use of invite link intended for User ID {intended_user_id}"
                    )

                # Create a new invite for the intended user since theirs was consumed
                new_invite = await self._create_invite_for_user(
                    intended_user_id,
                    f"Replacement invite for User ID {intended_user_id} "
                    "after impersonation attempt",
                    stored_interaction
                )

                if new_invite and stored_interaction:
                    # Try to send a followup message to the original interaction
                    try:
                        expires_timestamp = int(discord.utils.utcnow().timestamp()) + INVITE_TIMEOUT
                        msg = (f"Hey {stored_interaction.user.display_name}! Your invite was used by "
                               "someone else, so we made a new one for you.")
                        
                        await stored_interaction.followup.send(
                            view=InviteDialog(
                                stored_interaction, member.guild, msg,
                                new_invite.url, expires_timestamp
                            ),
                            ephemeral=True
                        )
                    except (discord.HTTPException, discord.NotFound):
                        pass
            else:
                self.bot.logger.info(
                    "User %s (User ID: %s) successfully joined using their invite",
                    member, member.id
                )

async def setup(bot: commands.Bot) -> None:
    """Load the Invite cog."""
    await bot.add_cog(Invite(bot))
