import json
import os
import discord

from discord.ext import commands

from views import RosterMenu
from flask import Flask
from threading import Thread

from github_storage import (
    get_roster,
    save_roster
)

from roster_display import (
    update_roster,
    create_roster_text
)


# ----------------------------
# RENDER KEEP-ALIVE SERVER
# ----------------------------

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running!"


def run():
    port = int(
        os.getenv(
            "PORT",
            "10000"
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )


def keep_alive():
    thread = Thread(
        target=run,
        daemon=True
    )

    thread.start()


# ----------------------------
# CONFIG
# ----------------------------

with open(
    "config.json",
    "r"
) as f:

    config = json.load(f)


TOKEN = os.getenv("TOKEN")

OWNER_ID = config["owner_id"]


if not TOKEN:
    raise RuntimeError(
        "TOKEN environment variable is not set."
    )


# ----------------------------
# BOT
# ----------------------------

intents = discord.Intents.default()

intents.members = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# ----------------------------
# ROSTER COMMAND
# ----------------------------

@bot.tree.command(
    name="roster",
    description="Display the current HALO roster"
)
async def roster(
    interaction: discord.Interaction
):

    try:

        message = await create_roster_text(
            bot
        )

        await interaction.response.send_message(
            message
        )

    except Exception as e:

        print(
            f"[Roster] Error: {e}"
        )

        await interaction.response.send_message(
            "❌ Failed to load the roster.",
            ephemeral=True
        )


# ----------------------------
# ROSTER UPDATE COMMAND
# ----------------------------

@bot.tree.command(
    name="rosterupdate",
    description="Open the roster editor"
)
async def rosterupdate(
    interaction: discord.Interaction
):

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


# ----------------------------
# SET LIVE ROSTER
# ----------------------------

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


    data = await get_roster()


    data["roster_channel"] = (
        interaction.channel.id
    )

    # Reset message ID so a fresh live
    # roster message is created here.
    data["roster_message"] = None


    await save_roster(
        data,
        "Set roster channel"
    )


    await interaction.response.send_message(
        "✅ Creating live roster...",
        ephemeral=True
    )


    await update_roster(
        bot
    )


# ----------------------------
# BOT READY
# ----------------------------

@bot.event
async def on_ready():

    await bot.tree.sync()


    print(
        "----------------------"
    )

    print(
        f"Logged in as {bot.user}"
    )

    print(
        "Slash commands synced."
    )

    print(
        "GitHub roster storage enabled."
    )

    print(
        "----------------------"
    )


    # If a live roster already exists,
    # refresh it after Render restarts.
    try:

        await update_roster(
            bot
        )

    except Exception as e:

        print(
            f"[Roster] Startup update failed: {e}"
        )


# ----------------------------
# START
# ----------------------------

keep_alive()

bot.run(
    TOKEN
)
