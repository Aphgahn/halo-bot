import discord

from github_storage import get_roster, save_roster

HALO_EMOJI = "<:otherHALO:1547343825981276210>"


async def create_roster_text(bot):
    data = await get_roster()

    def mention(user_id):
        return f"<@{user_id}>" if user_id else "VACANT"

    main_name = data.get("roster_name", "HALO")
    text = (
        f"{HALO_EMOJI} **{main_name} Roster:**\n\n"
        f"👑 **[Captain]** {mention(data.get('captain'))}\n"
        f"⭐ **[Co-Captain]** {mention(data.get('co_captain'))}\n\n"
    )

    players = data.get("players", [])
    text += "\n".join(mention(player) for player in players) if players else "No players added yet."

    for roster in data.get("additional_rosters", []):
        text += (
            f"\\n\\n{HALO_EMOJI} **{roster.get('name', 'Additional Roster')}**\\n\\n"
            f"👑 **[Captain]** {mention(roster.get('captain'))}\\n"
            f"⭐ **[Co-Captain]** {mention(roster.get('co_captain'))}\\n\\n"
        )
        roster_players = roster.get("players", [])
        text += "\\n".join(mention(player) for player in roster_players) if roster_players else "No players added yet."

    text += f"\n\n{HALO_EMOJI} **Tryouts**\n\n"
    text += "\n".join(mention(player) for player in data.get("looking_at", [])) or "None"
    return text


async def update_roster(bot):
    data = await get_roster()
    if not data.get("roster_channel"):
        return

    channel = bot.get_channel(data["roster_channel"])
    if not channel:
        print("[Roster] Could not find roster channel.")
        return

    message = None
    if data.get("roster_message"):
        try:
            message = await channel.fetch_message(data["roster_message"])
        except discord.NotFound:
            message = None
        except discord.Forbidden:
            print("[Roster] Bot does not have permission to fetch the roster message.")
            return
        except discord.HTTPException as e:
            print(f"[Roster] Failed to fetch message: {e}")
            return

    content = await create_roster_text(bot)
    if len(content) > 2000:
        content = content[:1980] + "\n… roster display truncated (Discord message limit)."

    if message:
        try:
            await message.edit(content=content)
            print("[Roster] Live roster updated.")
        except discord.HTTPException as e:
            print(f"[Roster] Failed to edit roster: {e}")
    else:
        try:
            message = await channel.send(content)
            data["roster_message"] = message.id
            await save_roster(data, "Set live roster message")
            print("[Roster] Created new live roster message.")
        except discord.HTTPException as e:
            print(f"[Roster] Failed to create roster message: {e}")
