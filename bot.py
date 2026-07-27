import json
import discord
from discord.ext import commands
from discord import app_commands
import os
from views import RosterMenu
from flask import Flask
from threading import Thread
from roster_display import update_roster, create_roster_text

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

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

@bot.tree.command(
    name="rosterupdate",
    description="Open the roster editor"
)
async def rosterupdate(interaction: discord.Interaction):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "❌ You cannot use this command.",
            ephemeral=True
        )
        return


    view = RosterMenu()

    await interaction.response.send_message(
        "🟢 **HALO Roster Editor**\n\n"
        "Choose what you want to edit:",
        view=view,
        ephemeral=True
    )

@bot.tree.command(
    name="setroster",
    description="Create the live roster message"
)
async def setroster(
    interaction: discord.Interaction
):

    if interaction.user.id != OWNER_ID:
        await interaction.response.send_message(
            "❌ You cannot use this.",
            ephemeral=True
        )
        return


    data = load_roster()


    data["roster_channel"] = interaction.channel.id

    save_roster(data)


    await interaction.response.send_message(
        "✅ Creating roster...",
        ephemeral=True
    )


    await update_roster(bot)

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

keep_alive()
bot.run(TOKEN)
