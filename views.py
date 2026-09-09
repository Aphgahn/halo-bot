import discord
from discord.ui import UserSelect, View

from github_storage import get_roster, save_roster
from roster_display import update_roster


# ----------------------------
# GENERIC SELECT VIEW
# ----------------------------

class SelectView(View):

    def __init__(self, selector):
        super().__init__(timeout=300)

        self.add_item(selector)


# ----------------------------
# CAPTAIN
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

        data = await get_roster()

        data["captain"] = user.id

        await save_roster(
            data,
            f"Captain changed to {user.id}"
        )

        await update_roster(
            interaction.client
        )

        await interaction.response.send_message(
            f"👑 Captain set to {user.mention}",
            ephemeral=True
        )


# ----------------------------
# CO-CAPTAIN
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

        data = await get_roster()

        data["co_captain"] = user.id

        await save_roster(
            data,
            f"Co-Captain changed to {user.id}"
        )

        await update_roster(
            interaction.client
        )

        await interaction.response.send_message(
            f"⭐ Co-Captain set to {user.mention}",
            ephemeral=True
        )


# ----------------------------
# PLAYER SELECT
# ----------------------------

async def open_player_select(
    interaction,
    slot
):

    class PlayerSelect(UserSelect):

        def __init__(self):
            super().__init__(
                placeholder=f"Select player for slot {slot + 1}",
                min_values=1,
                max_values=1
            )

        async def callback(
            self,
            interaction
        ):

            user = self.values[0]

            data = await get_roster()

            data["players"][slot] = user.id

            await save_roster(
                data,
                f"Player slot {slot + 1} changed to {user.id}"
            )

            await update_roster(
                interaction.client
            )

            await interaction.response.send_message(
                f"👥 Slot {slot + 1} set to {user.mention}",
                ephemeral=True
            )

    await interaction.response.send_message(
        f"Choose player for slot {slot + 1}",
        view=SelectView(
            PlayerSelect()
        ),
        ephemeral=True
    )


# ----------------------------
# PLAYER SLOT BUTTONS
# ----------------------------

class PlayerSlots(View):

    def __init__(self):
        super().__init__(timeout=300)

    async def open_slot(
        self,
        interaction,
        slot
    ):
        await open_player_select(
            interaction,
            slot
        )

    @discord.ui.button(
        label="Slot 1",
        style=discord.ButtonStyle.primary
    )
    async def slot1(
        self,
        interaction,
        button
    ):
        await self.open_slot(
            interaction,
            0
        )

    @discord.ui.button(
        label="Slot 2",
        style=discord.ButtonStyle.primary
    )
    async def slot2(
        self,
        interaction,
        button
    ):
        await self.open_slot(
            interaction,
            1
        )

    @discord.ui.button(
        label="Slot 3",
        style=discord.ButtonStyle.primary
    )
    async def slot3(
        self,
        interaction,
        button
    ):
        await self.open_slot(
            interaction,
            2
        )

    @discord.ui.button(
        label="Slot 4",
        style=discord.ButtonStyle.primary
    )
    async def slot4(
        self,
        interaction,
        button
    ):
        await self.open_slot(
            interaction,
            3
        )

    @discord.ui.button(
        label="Slot 5",
        style=discord.ButtonStyle.primary
    )
    async def slot5(
        self,
        interaction,
        button
    ):
        await self.open_slot(
            interaction,
            4
        )

    @discord.ui.button(
        label="Slot 6",
        style=discord.ButtonStyle.primary
    )
    async def slot6(
        self,
        interaction,
        button
    ):
        await self.open_slot(
            interaction,
            5
        )


# ----------------------------
# REMOVE PLAYER SLOTS
# ----------------------------

class RemovePlayers(View):

    def __init__(self):
        super().__init__(timeout=300)

    async def remove_slot(
        self,
        interaction,
        slot
    ):

        data = await get_roster()

        data["players"][slot] = None

        await save_roster(
            data,
            f"Removed player from slot {slot + 1}"
        )

        await update_roster(
            interaction.client
        )

        await interaction.response.send_message(
            f"🗑 Slot {slot + 1} removed.",
            ephemeral=True
        )

    @discord.ui.button(
        label="Remove Slot 1",
        style=discord.ButtonStyle.danger
    )
    async def remove1(
        self,
        interaction,
        button
    ):
        await self.remove_slot(
            interaction,
            0
        )

    @discord.ui.button(
        label="Remove Slot 2",
        style=discord.ButtonStyle.danger
    )
    async def remove2(
        self,
        interaction,
        button
    ):
        await self.remove_slot(
            interaction,
            1
        )

    @discord.ui.button(
        label="Remove Slot 3",
        style=discord.ButtonStyle.danger
    )
    async def remove3(
        self,
        interaction,
        button
    ):
        await self.remove_slot(
            interaction,
            2
        )

    @discord.ui.button(
        label="Remove Slot 4",
        style=discord.ButtonStyle.danger
    )
    async def remove4(
        self,
        interaction,
        button
    ):
        await self.remove_slot(
            interaction,
            3
        )

    @discord.ui.button(
        label="Remove Slot 5",
        style=discord.ButtonStyle.danger
    )
    async def remove5(
        self,
        interaction,
        button
    ):
        await self.remove_slot(
            interaction,
            4
        )

    @discord.ui.button(
        label="Remove Slot 6",
        style=discord.ButtonStyle.danger
    )
    async def remove6(
        self,
        interaction,
        button
    ):
        await self.remove_slot(
            interaction,
            5
        )


# ----------------------------
# PLAYER ACTION MENU
# ----------------------------

class PlayerActionMenu(View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="➕ Change Player",
        style=discord.ButtonStyle.primary
    )
    async def change(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Choose slot:",
            view=PlayerSlots(),
            ephemeral=True
        )

    @discord.ui.button(
        label="🗑 Remove Player",
        style=discord.ButtonStyle.danger
    )
    async def remove(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Choose slot to remove:",
            view=RemovePlayers(),
            ephemeral=True
        )


# ----------------------------
# LOOKING AT - ADD
# ----------------------------

class LookingAdd(UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select player interested",
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        user = self.values[0]

        data = await get_roster()

        if user.id not in data["looking_at"]:

            data["looking_at"].append(
                user.id
            )

            await save_roster(
                data,
                f"Added {user.id} to scouting list"
            )

            message = (
                f"🔍 Added {user.mention} "
                "to the Scouting List."
            )

        else:

            message = (
                f"ℹ️ {user.mention} "
                "is already on the Scouting List."
            )

        await update_roster(
            interaction.client
        )

        await interaction.response.send_message(
            message,
            ephemeral=True
        )


# ----------------------------
# LOOKING AT - REMOVE
# ----------------------------

class LookingRemove(UserSelect):

    def __init__(self):
        super().__init__(
            placeholder="Select player to remove",
            min_values=1,
            max_values=1
        )

    async def callback(
        self,
        interaction
    ):

        user = self.values[0]

        data = await get_roster()

        if user.id in data["looking_at"]:

            data["looking_at"].remove(
                user.id
            )

            await save_roster(
                data,
                f"Removed {user.id} from scouting list"
            )

            await update_roster(
                interaction.client
            )

            await interaction.response.send_message(
                f"🗑 Removed {user.mention} "
                "from the Scouting List.",
                ephemeral=True
            )

        else:

            await interaction.response.send_message(
                f"ℹ️ {user.mention} "
                "is not on the Scouting List.",
                ephemeral=True
            )


# ----------------------------
# LOOKING AT MENU
# ----------------------------

class LookingMenu(View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="➕ Add Player",
        style=discord.ButtonStyle.success
    )
    async def add(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Choose player:",
            view=SelectView(
                LookingAdd()
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="🗑 Remove Player",
        style=discord.ButtonStyle.danger
    )
    async def remove(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Choose player to remove:",
            view=SelectView(
                LookingRemove()
            ),
            ephemeral=True
        )


# ----------------------------
# REMOVE CAPTAIN / CO-CAPTAIN
# ----------------------------

class RemoveRoles(View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="🗑 Remove Captain",
        style=discord.ButtonStyle.danger
    )
    async def captain(
        self,
        interaction,
        button
    ):

        data = await get_roster()

        data["captain"] = None

        await save_roster(
            data,
            "Removed Captain"
        )

        await update_roster(
            interaction.client
        )

        await interaction.response.send_message(
            "🗑 Captain removed.",
            ephemeral=True
        )

    @discord.ui.button(
        label="🗑 Remove Co-Captain",
        style=discord.ButtonStyle.danger
    )
    async def co(
        self,
        interaction,
        button
    ):

        data = await get_roster()

        data["co_captain"] = None

        await save_roster(
            data,
            "Removed Co-Captain"
        )

        await update_roster(
            interaction.client
        )

        await interaction.response.send_message(
            "🗑 Co-Captain removed.",
            ephemeral=True
        )


# ----------------------------
# MAIN ROSTER UPDATE MENU
# ----------------------------

class RosterMenu(View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="👑 Captain",
        style=discord.ButtonStyle.primary
    )
    async def captain(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Select Captain:",
            view=SelectView(
                CaptainSelect()
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="⭐ Co-Captain",
        style=discord.ButtonStyle.primary
    )
    async def co_captain(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Select Co-Captain:",
            view=SelectView(
                CoCaptainSelect()
            ),
            ephemeral=True
        )

    @discord.ui.button(
        label="👥 Players",
        style=discord.ButtonStyle.success
    )
    async def players(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Choose action:",
            view=PlayerActionMenu(),
            ephemeral=True
        )

    @discord.ui.button(
        label="🔍 Looking At",
        style=discord.ButtonStyle.secondary
    )
    async def looking(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Looking At menu:",
            view=LookingMenu(),
            ephemeral=True
        )

    @discord.ui.button(
        label="🗑 Remove Roles",
        style=discord.ButtonStyle.danger
    )
    async def remove_roles(
        self,
        interaction,
        button
    ):

        await interaction.response.send_message(
            "Choose removal:",
            view=RemoveRoles(),
            ephemeral=True
        )
