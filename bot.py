import json
import discord
from discord.ext import commands
from discord import app_commands
import os

# ----------------------------
# Load config
# ----------------------------

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = os.getenv("TOKEN")
OWNER_ID = config["owner_id"]

# ----------------------------
# Bot
# ----------------------------

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ----------------------------
# Helpers
# ----------------------------

def load_roster():
    with open("roster.json", "r") as f:
        return json.load(f)


def save_roster(data):
    with open("roster.json", "w") as f:
        json.dump(data, f, indent=4)

# ----------------------------
# Roster Command
# ----------------------------

def format_player(guild, user_id):
    if user_id is None:
        return "[VACANT]"

    member = guild.get_member(user_id)

    if member:
        return member.mention

    return "[UNKNOWN USER]"


@bot.tree.command(
    name="roster",
    description="Display the current HALO roster"
)
async def roster(interaction: discord.Interaction):

    data = load_roster()

    captain = format_player(
        interaction.guild,
        data["captain"]
    )

    co_captain = format_player(
        interaction.guild,
        data["co_captain"]
    )


    message = (
        "🟢 **HALO Roster:**\n\n"
        f"👑 **[Captain]** {captain}\n"
        f"⭐ **[Co-Captain]** {co_captain}\n\n"
    )


    # Players

    for player in data["players"]:
        message += f"{format_player(interaction.guild, player)}\n"


    message += "\n\n"
    message += "🟢 **Players Wanted / Looking At:**\n\n"


    # Looking at list

    if len(data["looking_at"]) == 0:
        message += "[NONE]"

    else:
        for player in data["looking_at"]:
            message += f"{format_player(interaction.guild, player)}\n"


    await interaction.response.send_message(message)

# ----------------------------
# Events
# ----------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()

    print("----------------------")
    print(f"Logged in as {bot.user}")
    print("Slash commands synced.")
    print("----------------------")


bot.run(TOKEN)
