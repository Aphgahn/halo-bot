import discord

from github_storage import get_roster, save_roster


HALO_EMOJI = "<:HALO:1529461747411451974>"


async def create_roster_text(bot):
    data = await get_roster()

    def mention(user_id):
        if user_id:
            return f"<@{user_id}>"

        return "VACANT"

    text = (
        f"{HALO_EMOJI} **HALO Roster:**\n\n"
        f"👑 **[Captain]** {mention(data['captain'])}\n"
        f"⭐ **[Co-Captain]** {mention(data['co_captain'])}\n\n"
    )

    for player in data["players"]:
        text += f"{mention(player)}\n"

    text += (
        f"\n\n"
        f"{HALO_EMOJI} **Scouting List**\n\n"
    )

    if not data["looking_at"]:
        text += "None"
    else:
        for player in data["looking_at"]:
            text += f"{mention(player)}\n"

    return text


async def update_roster(bot):
    data = await get_roster()

    if not data.get("roster_channel"):
        return

    channel = bot.get_channel(
        data["roster_channel"]
    )

    if not channel:
        print(
            "[Roster] Could not find roster channel."
        )
        return

    message = None

    if data.get("roster_message"):
        try:
            message = await channel.fetch_message(
                data["roster_message"]
            )

        except discord.NotFound:
            message = None

        except discord.Forbidden:
            print(
                "[Roster] Bot does not have permission "
                "to fetch the roster message."
            )
            return

        except discord.HTTPException as e:
            print(
                f"[Roster] Failed to fetch message: {e}"
            )
            return

    content = await create_roster_text(bot)

    if message:
        try:
            await message.edit(
                content=content
            )

            print("[Roster] Live roster updated.")

        except discord.HTTPException as e:
            print(
                f"[Roster] Failed to edit roster: {e}"
            )

    else:
        try:
            message = await channel.send(
                content
            )

            data["roster_message"] = message.id

            await save_roster(
                data,
                "Set live roster message"
            )

            print(
                "[Roster] Created new live roster message."
            )

        except discord.HTTPException as e:
            print(
                f"[Roster] Failed to create roster message: {e}"
            )
