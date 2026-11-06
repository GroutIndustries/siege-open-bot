import discord
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Storage for the teams (resets when the bot restarts)
team1 = []
team2 = []

class TeamView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    # Role required to join/leave teams
    REQUIRED_ROLE = "Match Host"   # ← Change this if needed

    async def update_embed(self, interaction: discord.Interaction):
        # Keep the original match info fields when updating
        embed = interaction.message.embeds[0]

        # Update only the team fields
        embed.set_field_at(4, name=f"TEAM 1 ({len(team1)}/5)", value="\n".join([f"• {name}" for name in team1]) if team1 else "*Empty*", inline=True)
        embed.set_field_at(5, name=f"TEAM 2 ({len(team2)}/5)", value="\n".join([f"• {name}" for name in team2]) if team2 else "*Empty*", inline=True)

        await interaction.message.edit(embed=embed, view=self)

    def has_required_role(self, member: discord.Member) -> bool:
        return any(role.name == self.REQUIRED_ROLE for role in member.roles)

    @discord.ui.button(label="TEAM 1", style=discord.ButtonStyle.primary, custom_id="join_team1")
    async def join_team1(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_required_role(interaction.user):
            await interaction.response.send_message(
                f"You need the **{self.REQUIRED_ROLE}** role to join a team.",
                ephemeral=True
            )
            return

        user = interaction.user.display_name

        if user in team1:
            await interaction.response.send_message("You are already on **TEAM 1**.", ephemeral=True)
            return
        if user in team2:
            await interaction.response.send_message("You are already on **TEAM 2**. Sign off first.", ephemeral=True)
            return
        if len(team1) >= 5:
            await interaction.response.send_message("**TEAM 1** is full (5/5).", ephemeral=True)
            return

        team1.append(user)
        await interaction.response.defer()
        await self.update_embed(interaction)

    @discord.ui.button(label="TEAM 2", style=discord.ButtonStyle.danger, custom_id="join_team2")
    async def join_team2(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_required_role(interaction.user):
            await interaction.response.send_message(
                f"You need the **{self.REQUIRED_ROLE}** role to join a team.",
                ephemeral=True
            )
            return

        user = interaction.user.display_name

        if user in team2:
            await interaction.response.send_message("You are already on **TEAM 2**.", ephemeral=True)
            return
        if user in team1:
            await interaction.response.send_message("You are already on **TEAM 1**. Sign off first.", ephemeral=True)
            return
        if len(team2) >= 5:
            await interaction.response.send_message("**TEAM 2** is full (5/5).", ephemeral=True)
            return

        team2.append(user)
        await interaction.response.defer()
        await self.update_embed(interaction)

    @discord.ui.button(label="SIGN OFF", style=discord.ButtonStyle.secondary, custom_id="sign_off")
    async def sign_off(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.has_required_role(interaction.user):
            await interaction.response.send_message(
                f"You need the **{self.REQUIRED_ROLE}** role to use this.",
                ephemeral=True
            )
            return

        user = interaction.user.display_name

        if user in team1:
            team1.remove(user)
            await interaction.response.defer()
            await self.update_embed(interaction)
            return

        if user in team2:
            team2.remove(user)
            await interaction.response.defer()
            await self.update_embed(interaction)
            return

        await interaction.response.send_message("You are not on any team.", ephemeral=True)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


@bot.tree.command(name="post-match", description="Post a new match signup panel")
@app_commands.checks.has_role("Match Host")
@app_commands.describe(
    date="Date of the match (example: November 10)",
    time="Time of the match (example: 8:00 PM)",
    timezone="Timezone (example: EST)",
    min_rank="Minimum rank required (example: Gold)"
)
async def post_match(
    interaction: discord.Interaction,
    date: str,
    time: str,
    timezone: str,
    min_rank: str
):
    embed = discord.Embed(
        title="Siege Open • Match Signup",
        description="Click a button to join a team or sign off.\nMax **5 players** per team.",
        color=discord.Color.blue()
    )

    # Match Info
    embed.add_field(name="Date", value=date, inline=True)
    embed.add_field(name="Time", value=f"{time} {timezone}", inline=True)
    embed.add_field(name="Min Rank", value=min_rank, inline=True)

    embed.add_field(name="\u200b", value="\u200b", inline=False)  # Spacer

    embed.add_field(name="TEAM 1 (0/5)", value="*Empty*", inline=True)
    embed.add_field(name="TEAM 2 (0/5)", value="*Empty*", inline=True)

    view = TeamView()
    await interaction.response.send_message(embed=embed, view=view)


@post_match.error
async def post_match_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message(
            "You need the **Match Host** role to use this command.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message("Something went wrong.", ephemeral=True)


@bot.tree.command(name="clearteams", description="Clear both teams")
@app_commands.checks.has_permissions(administrator=True)
async def clearteams(interaction: discord.Interaction):
    global team1, team2
    team1.clear()
    team2.clear()
    await interaction.response.send_message("Both teams have been cleared.", ephemeral=True)


bot.run("MTU2ODEwNzM3MTAzMTY5OTU2MA.G8MvJ4.x29FGMX9PJUpZoDsNE1eByZZVJNOn5Nfki8Mm0")