import discord
from discord.ui import UserSelect, View
import json


# ----------------------------
# Roster File Handling
# ----------------------------

def load_roster():
    with open("roster.json", "r") as f:
        return json.load(f)


def save_roster(data):
    with open("roster.json", "w") as f:
        json.dump(data, f, indent=4)


# ----------------------------
# Captain Selector
# ----------------------------

class CaptainSelect(UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select the Captain",
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction: discord.Interaction):

        user = self.values[0]

        data = load_roster()

        data["captain"] = user.id

        save_roster(data)

        await interaction.response.send_message(
            f"👑 Captain updated to {user.mention}",
            ephemeral=True
        )


# ----------------------------
# Co Captain Selector
# ----------------------------

class CoCaptainSelect(UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select the Co-Captain",
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction: discord.Interaction):

        user = self.values[0]

        data = load_roster()

        data["co_captain"] = user.id

        save_roster(data)

        await interaction.response.send_message(
            f"⭐ Co-Captain updated to {user.mention}",
            ephemeral=True
        )


# ----------------------------
# Generic Selector View
# ----------------------------

class SelectView(View):

    def __init__(self, selector):
        super().__init__(timeout=300)
        self.add_item(selector)



# ----------------------------
# Player Slot Menu
# ----------------------------

class PlayerSlots(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)


    @discord.ui.button(
        label="Slot 1",
        style=discord.ButtonStyle.primary
    )
    async def slot1(self, interaction, button):
        await open_player_select(interaction, 0)


    @discord.ui.button(
        label="Slot 2",
        style=discord.ButtonStyle.primary
    )
    async def slot2(self, interaction, button):
        await open_player_select(interaction, 1)


    @discord.ui.button(
        label="Slot 3",
        style=discord.ButtonStyle.primary
    )
    async def slot3(self, interaction, button):
        await open_player_select(interaction, 2)


    @discord.ui.button(
        label="Slot 4",
        style=discord.ButtonStyle.primary
    )
    async def slot4(self, interaction, button):
        await open_player_select(interaction, 3)


    @discord.ui.button(
        label="Slot 5",
        style=discord.ButtonStyle.primary
    )
    async def slot5(self, interaction, button):
        await open_player_select(interaction, 4)


    @discord.ui.button(
        label="Slot 6",
        style=discord.ButtonStyle.primary
    )
    async def slot6(self, interaction, button):
        await open_player_select(interaction, 5)



# ----------------------------
# Main Roster Menu
# ----------------------------

class RosterMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)


    @discord.ui.button(
        label="👑 Captain",
        style=discord.ButtonStyle.primary
    )
    async def captain(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Choose the Captain:",
            view=SelectView(CaptainSelect()),
            ephemeral=True
        )


    @discord.ui.button(
        label="⭐ Co-Captain",
        style=discord.ButtonStyle.primary
    )
    async def co_captain(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Choose the Co-Captain:",
            view=SelectView(CoCaptainSelect()),
            ephemeral=True
        )


    @discord.ui.button(
        label="👥 Players",
        style=discord.ButtonStyle.success
    )
    async def players(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Choose a player slot:",
            view=PlayerSlots(),
            ephemeral=True
        )


    @discord.ui.button(
        label="🔍 Looking At",
        style=discord.ButtonStyle.secondary
    )
    async def looking(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Looking At menu coming next.",
            ephemeral=True
        )



# ----------------------------
# Player Selection
# ----------------------------

async def open_player_select(
    interaction,
    slot
):

    class PlayerSelect(discord.ui.UserSelect):

        def __init__(self):
            super().__init__(
                placeholder=f"Select player for slot {slot + 1}",
                min_values=1,
                max_values=1
            )


        async def callback(self, interaction):

            user = self.values[0]

            data = load_roster()

            data["players"][slot] = user.id

            save_roster(data)

            await interaction.response.send_message(
                f"👥 Slot {slot + 1} updated to {user.mention}",
                ephemeral=True
            )


    await interaction.response.send_message(
        f"Choose player for slot {slot + 1}:",
        view=SelectView(PlayerSelect()),
        ephemeral=True
    )
