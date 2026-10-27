import discord
from discord.ui import UserSelect, View, Modal, TextInput, Select

from github_storage import get_roster, save_roster
from roster_display import update_roster


def roster_entries(data):
    entries = [("main", "HALO Main Roster", data.get("players", []))]
    for index, roster in enumerate(data.get("additional_rosters", [])):
        entries.append((f"extra:{index}", roster.get("name", f"Roster {index + 1}"), roster.get("players", [])))
    return entries


def get_players_for_key(data, roster_key):
    if roster_key == "main":
        return data.setdefault("players", [])
    if roster_key.startswith("extra:"):
        index = int(roster_key.split(":", 1)[1])
        rosters = data.setdefault("additional_rosters", [])
        if 0 <= index < len(rosters):
            return rosters[index].setdefault("players", [])
    return []


class SelectView(View):
    def __init__(self, selector):
        super().__init__(timeout=300)
        self.add_item(selector)


class CaptainSelect(UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select Captain", min_values=1, max_values=1)

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        data["captain"] = user.id
        await save_roster(data, f"Captain changed to {user.id}")
        await update_roster(interaction.client)
        await interaction.response.send_message(f"👑 Captain set to {user.mention}", ephemeral=True)


class CoCaptainSelect(UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select Co-Captain", min_values=1, max_values=1)

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        data["co_captain"] = user.id
        await save_roster(data, f"Co-Captain changed to {user.id}")
        await update_roster(interaction.client)
        await interaction.response.send_message(f"⭐ Co-Captain set to {user.mention}", ephemeral=True)


class AddPlayerSelect(UserSelect):
    def __init__(self, roster_key):
        super().__init__(placeholder="Select a player to add", min_values=1, max_values=1)
        self.roster_key = roster_key

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        players = get_players_for_key(data, self.roster_key)
        if user.id in players:
            await interaction.response.send_message(f"ℹ️ {user.mention} is already on this roster.", ephemeral=True)
            return
        players.append(user.id)
        await save_roster(data, f"Added player {user.id} to {self.roster_key}")
        await update_roster(interaction.client)
        await interaction.response.send_message(f"✅ Added {user.mention} to the roster.", ephemeral=True)


class RemovePlayerSelect(UserSelect):
    def __init__(self, roster_key):
        super().__init__(placeholder="Select a roster player to remove", min_values=1, max_values=1)
        self.roster_key = roster_key

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        players = get_players_for_key(data, self.roster_key)
        if user.id not in players:
            await interaction.response.send_message(f"ℹ️ {user.mention} is not on this roster.", ephemeral=True)
            return
        players.remove(user.id)
        await save_roster(data, f"Removed player {user.id} from {self.roster_key}")
        await update_roster(interaction.client)
        await interaction.response.send_message(f"🗑 Removed {user.mention} from the roster.", ephemeral=True)


class RosterNameModal(Modal):
    def __init__(self, mode, roster_key=None, current_name=""):
        super().__init__(title="Create Roster" if mode == "create" else "Rename Roster")
        self.mode = mode
        self.roster_key = roster_key
        self.name_input = TextInput(
            label="Roster name",
            placeholder="e.g. Academy, Reserve, Main Team",
            default=current_name[:45] if current_name else None,
            max_length=45,
            min_length=1
        )
        self.add_item(self.name_input)

    async def on_submit(self, interaction):
        name = str(self.name_input.value).strip()
        if not name:
            await interaction.response.send_message("Please enter a roster name.", ephemeral=True)
            return
        data = await get_roster()
        if self.mode == "create":
            data.setdefault("additional_rosters", []).append({"name": name, "players": []})
            message = f"✅ Created roster **{name}**. Use **/rosterupdate** → **Manage Rosters** to add players."
            commit = f"Created roster: {name}"
        else:
            if self.roster_key == "main":
                data["roster_name"] = name
            else:
                index = int(self.roster_key.split(":", 1)[1])
                rosters = data.setdefault("additional_rosters", [])
                if not 0 <= index < len(rosters):
                    await interaction.response.send_message("That roster could not be found.", ephemeral=True)
                    return
                rosters[index]["name"] = name
            message = f"✅ Roster renamed to **{name}**."
            commit = f"Renamed roster: {name}"
        await save_roster(data, commit)
        await update_roster(interaction.client)
        await interaction.response.send_message(message, ephemeral=True)


class RosterPicker(Select):
    def __init__(self):
        data = None
        # Options are filled by the async factory below.
        super().__init__(placeholder="Select a roster", min_values=1, max_values=1, options=[
            discord.SelectOption(label="HALO Main Roster", value="main")
        ])

    @classmethod
    async def create(cls):
        picker = cls()
        data = await get_roster()
        options = []
        for key, name, _players in roster_entries(data):
            options.append(discord.SelectOption(label=name[:100], value=key))
        picker.options = options[:25]
        return picker

    async def callback(self, interaction):
        await interaction.response.send_message(
            "Manage this roster:",
            view=RosterActions(self.values[0]),
            ephemeral=True
        )


class RosterActions(View):
    def __init__(self, roster_key):
        super().__init__(timeout=300)
        self.roster_key = roster_key

    @discord.ui.button(label="➕ Add Player", style=discord.ButtonStyle.success, row=0)
    async def add_player(self, interaction, button):
        await interaction.response.send_message(
            "Choose the player to add:",
            view=SelectView(AddPlayerSelect(self.roster_key)),
            ephemeral=True
        )

    @discord.ui.button(label="🗑 Remove Player", style=discord.ButtonStyle.danger, row=0)
    async def remove_player(self, interaction, button):
        await interaction.response.send_message(
            "Choose the player to remove:",
            view=SelectView(RemovePlayerSelect(self.roster_key)),
            ephemeral=True
        )

    @discord.ui.button(label="✏️ Rename Roster", style=discord.ButtonStyle.primary, row=1)
    async def rename_roster(self, interaction, button):
        data = await get_roster()
        current_name = next((name for key, name, _ in roster_entries(data) if key == self.roster_key), "")
        await interaction.response.send_modal(RosterNameModal("rename", self.roster_key, current_name))


class RosterManager(View):
    def __init__(self, picker):
        super().__init__(timeout=300)
        self.add_item(picker)

    @discord.ui.button(label="➕ Create Roster", style=discord.ButtonStyle.success, row=1)
    async def create_roster(self, interaction, button):
        await interaction.response.send_modal(RosterNameModal("create"))


class LookingAdd(UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select player interested", min_values=1, max_values=1)

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        if user.id not in data["looking_at"]:
            data["looking_at"].append(user.id)
            await save_roster(data, f"Added {user.id} to scouting list")
            message = f"🔍 Added {user.mention} to the Scouting List."
        else:
            message = f"ℹ️ {user.mention} is already on the Scouting List."
        await update_roster(interaction.client)
        await interaction.response.send_message(message, ephemeral=True)


class LookingRemove(UserSelect):
    def __init__(self):
        super().__init__(placeholder="Select player to remove", min_values=1, max_values=1)

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        if user.id in data["looking_at"]:
            data["looking_at"].remove(user.id)
            await save_roster(data, f"Removed {user.id} from scouting list")
            await update_roster(interaction.client)
            message = f"🗑 Removed {user.mention} from the Scouting List."
        else:
            message = f"ℹ️ {user.mention} is not on the Scouting List."
        await interaction.response.send_message(message, ephemeral=True)


class LookingMenu(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="➕ Add Player", style=discord.ButtonStyle.success)
    async def add(self, interaction, button):
        await interaction.response.send_message("Choose player:", view=SelectView(LookingAdd()), ephemeral=True)

    @discord.ui.button(label="🗑 Remove Player", style=discord.ButtonStyle.danger)
    async def remove(self, interaction, button):
        await interaction.response.send_message("Choose player to remove:", view=SelectView(LookingRemove()), ephemeral=True)


class RemoveRoles(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="🗑 Remove Captain", style=discord.ButtonStyle.danger)
    async def captain(self, interaction, button):
        data = await get_roster()
        data["captain"] = None
        await save_roster(data, "Removed Captain")
        await update_roster(interaction.client)
        await interaction.response.send_message("🗑 Captain removed.", ephemeral=True)

    @discord.ui.button(label="🗑 Remove Co-Captain", style=discord.ButtonStyle.danger)
    async def co(self, interaction, button):
        data = await get_roster()
        data["co_captain"] = None
        await save_roster(data, "Removed Co-Captain")
        await update_roster(interaction.client)
        await interaction.response.send_message("🗑 Co-Captain removed.", ephemeral=True)


class RosterMenu(View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(label="👑 Captain", style=discord.ButtonStyle.primary)
    async def captain(self, interaction, button):
        await interaction.response.send_message("Select Captain:", view=SelectView(CaptainSelect()), ephemeral=True)

    @discord.ui.button(label="⭐ Co-Captain", style=discord.ButtonStyle.primary)
    async def co_captain(self, interaction, button):
        await interaction.response.send_message("Select Co-Captain:", view=SelectView(CoCaptainSelect()), ephemeral=True)

    @discord.ui.button(label="👥 Manage Rosters", style=discord.ButtonStyle.success, row=1)
    async def manage_rosters(self, interaction, button):
        picker = await RosterPicker.create()
        await interaction.response.send_message(
            "Select a roster to add/remove players or rename it. You can also create new rosters.",
            view=RosterManager(picker),
            ephemeral=True
        )

    @discord.ui.button(label="🔍 Looking At", style=discord.ButtonStyle.secondary, row=1)
    async def looking(self, interaction, button):
        await interaction.response.send_message("Looking At menu:", view=LookingMenu(), ephemeral=True)

    @discord.ui.button(label="🗑 Remove Roles", style=discord.ButtonStyle.danger, row=1)
    async def remove_roles(self, interaction, button):
        await interaction.response.send_message("Choose removal:", view=RemoveRoles(), ephemeral=True)
