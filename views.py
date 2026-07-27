import discord
from discord.ui import UserSelect, View
import json


def load_roster():
    with open("roster.json", "r") as f:
        return json.load(f)


def save_roster(data):
    with open("roster.json", "w") as f:
        json.dump(data, f, indent=4)


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



class SelectView(View):

    def __init__(self, selector):
        super().__init__(timeout=300)
        self.add_item(selector)



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
            "Players menu coming next.",
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
