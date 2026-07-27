import discord
import json

HALO_EMOJI = "<:HALO:1529461747411451974>"

def load_roster():
    with open("roster.json", "r") as f:
        return json.load(f)



def save_roster(data):
    with open("roster.json", "w") as f:
        json.dump(data, f, indent=4)



async def create_roster_text(bot):

    data = load_roster()


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


    text += f"\n\n{HALO_EMOJI} **Players Wanted / Looking At:**\n\n"


    if len(data["looking_at"]) == 0:
        text += "None"

    else:
        for player in data["looking_at"]:
            text += f"{mention(player)}\n"


    return text



async def update_roster(bot):

    data = load_roster()

    if not data["roster_channel"]:
        return


    channel = bot.get_channel(
        data["roster_channel"]
    )


    if not channel:
        return


    message = None


    if data["roster_message"]:

        try:
            message = await channel.fetch_message(
                data["roster_message"]
            )

        except:
            pass



    content = await create_roster_text(bot)



    if message:

        await message.edit(
            content=content
        )


    else:

        message = await channel.send(
            content
        )

        data["roster_message"] = message.id

        save_roster(data)
