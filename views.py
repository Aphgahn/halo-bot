import discord
from discord.ui import UserSelect, View
import json


# ----------------------------
# File handling
# ----------------------------

def load_roster():
    with open("roster.json", "r") as f:
        return json.load(f)


def save_roster(data):
    with open("roster.json", "w") as f:
        json.dump(data, f, indent=4)



# ----------------------------
# Generic selector
# ----------------------------

class SelectView(View):

    def __init__(self, selector):
        super().__init__(timeout=300)
        self.add_item(selector)



# ----------------------------
# Captain
# ----------------------------

class CaptainSelect(UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select Captain",
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction):

        user = self.values[0]

        data = load_roster()
        data["captain"] = user.id
        save_roster(data)

        await interaction.response.send_message(
            f"👑 Captain set to {user.mention}",
            ephemeral=True
        )



# ----------------------------
# Co Captain
# ----------------------------

class CoCaptainSelect(UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select Co-Captain",
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction):

        user = self.values[0]

        data = load_roster()
        data["co_captain"] = user.id
        save_roster(data)

        await interaction.response.send_message(
            f"⭐ Co-Captain set to {user.mention}",
            ephemeral=True
        )



# ----------------------------
# Player selector
# ----------------------------

async def open_player_select(interaction, slot):


    class PlayerSelect(UserSelect):

        def __init__(self):
            super().__init__(
                placeholder=f"Slot {slot+1}",
                min_values=1,
                max_values=1
            )


        async def callback(self, interaction):

            user = self.values[0]

            data = load_roster()

            data["players"][slot] = user.id

            save_roster(data)

            await interaction.response.send_message(
                f"👥 Slot {slot+1} updated to {user.mention}",
                ephemeral=True
            )


    await interaction.response.send_message(
        f"Select player for slot {slot+1}",
        view=SelectView(PlayerSelect()),
        ephemeral=True
    )



# ----------------------------
# Player slots
# ----------------------------

class PlayerSlots(View):

    def __init__(self):
        super().__init__(timeout=300)


    async def slot_button(
        self,
        interaction,
        slot
    ):

        await open_player_select(
            interaction,
            slot
        )


    @discord.ui.button(label="Slot 1", style=discord.ButtonStyle.primary)
    async def slot1(self, interaction, button):
        await self.slot_button(interaction,0)


    @discord.ui.button(label="Slot 2", style=discord.ButtonStyle.primary)
    async def slot2(self, interaction, button):
        await self.slot_button(interaction,1)


    @discord.ui.button(label="Slot 3", style=discord.ButtonStyle.primary)
    async def slot3(self, interaction, button):
        await self.slot_button(interaction,2)


    @discord.ui.button(label="Slot 4", style=discord.ButtonStyle.primary)
    async def slot4(self, interaction, button):
        await self.slot_button(interaction,3)


    @discord.ui.button(label="Slot 5", style=discord.ButtonStyle.primary)
    async def slot5(self, interaction, button):
        await self.slot_button(interaction,4)


    @discord.ui.button(label="Slot 6", style=discord.ButtonStyle.primary)
    async def slot6(self, interaction, button):
        await self.slot_button(interaction,5)



# ----------------------------
# Looking At Add
# ----------------------------

class LookingAdd(UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Add player looking at",
            min_values=1,
            max_values=1
        )


    async def callback(self, interaction):

        user = self.values[0]

        data = load_roster()

        if user.id not in data["looking_at"]:
            data["looking_at"].append(user.id)

        save_roster(data)

        await interaction.response.send_message(
            f"🔍 Added {user.mention}",
            ephemeral=True
        )



# ----------------------------
# Looking At menu
# ----------------------------

class LookingMenu(View):

    def __init__(self):
        super().__init__(timeout=300)


    @discord.ui.button(
        label="➕ Add Player",
        style=discord.ButtonStyle.success
    )
    async def add(self, interaction, button):

        await interaction.response.send_message(
            "Select player:",
            view=SelectView(LookingAdd()),
            ephemeral=True
        )



# ----------------------------
# Main menu
# ----------------------------

class RosterMenu(View):

    def __init__(self):
        super().__init__(timeout=300)


    @discord.ui.button(
        label="👑 Captain",
        style=discord.ButtonStyle.primary
    )
    async def captain(self, interaction, button):

        await interaction.response.send_message(
            "Choose Captain:",
            view=SelectView(CaptainSelect()),
            ephemeral=True
        )


    @discord.ui.button(
        label="⭐ Co-Captain",
        style=discord.ButtonStyle.primary
    )
    async def co(self, interaction, button):

        await interaction.response.send_message(
            "Choose Co-Captain:",
            view=SelectView(CoCaptainSelect()),
            ephemeral=True
        )


    @discord.ui.button(
        label="👥 Players",
        style=discord.ButtonStyle.success
    )
    async def players(self, interaction, button):

        await interaction.response.send_message(
            "Choose slot:",
            view=PlayerSlots(),
            ephemeral=True
        )


    @discord.ui.button(
        label="🔍 Looking At",
        style=discord.ButtonStyle.secondary
    )
    async def looking(self, interaction, button):

        await interaction.response.send_message(
            "Looking At:",
            view=LookingMenu(),
            ephemeral=True
        )
