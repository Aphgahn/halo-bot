import discord
from discord.ui import UserSelect, View, Modal, TextInput, Select

from github_storage import get_roster, save_roster
from roster_display import update_roster


def roster_entries(data):
    entries = [("main", data.get("roster_name", "HALO Roster"), data.get("players", []))]
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
    def __init__(self, roster_key="main"):
        super().__init__(placeholder="Select Captain", min_values=1, max_values=1)
        self.roster_key = roster_key

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        if self.roster_key == "main":
            data["captain"] = user.id
        else:
            index = int(self.roster_key.split(":", 1)[1])
            data["additional_rosters"][index]["captain"] = user.id
        await save_roster(data, f"Captain for {self.roster_key} changed to {user.id}")
        await update_roster(interaction.client)
        await interaction.response.send_message(f"👑 Captain set to {user.mention}", ephemeral=True)


class CoCaptainSelect(UserSelect):
    def __init__(self, roster_key="main"):
        super().__init__(placeholder="Select Co-Captain", min_values=1, max_values=1)
        self.roster_key = roster_key

    async def callback(self, interaction):
        user = self.values[0]
        data = await get_roster()
        if self.roster_key == "main":
            data["co_captain"] = user.id
        else:
            index = int(self.roster_key.split(":", 1)[1])
            data["additional_rosters"][index]["co_captain"] = user.id
        await save_roster(data, f"Co-Captain for {self.roster_key} changed to {user.id}")
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
            data.setdefault("additional_rosters", []).append({"name": name, "players": [], "captain": None, "co_captain": None})
            message = f"✅ Created roster **{name}**. Use **/rosterupdate** → **Manage Rosters** to add players."
            commit = f"Created roster: {name}"
        elif self.mode == "rename_tryouts":
            data["looking_at_name"] = name
            message = f"✅ Tryouts heading renamed to **{name}**."
            commit = f"Renamed tryouts heading: {name}"
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


class ConfirmDeleteRoster(View):
    def __init__(self, roster_key, roster_name):
        super().__init__(timeout=60)
        self.roster_key = roster_key
        self.roster_name = roster_name

    @discord.ui.button(label="Yes, Delete Roster", style=discord.ButtonStyle.danger)
    async def confirm_delete(self, interaction, button):
        data = await get_roster()
        try:
            index = int(self.roster_key.split(":", 1)[1])
            rosters = data.setdefault("additional_rosters", [])
        except (ValueError, IndexError):
            await interaction.response.send_message("That roster could not be found.", ephemeral=True)
            return

        if not 0 <= index < len(rosters) or rosters[index].get("name", "Additional Roster") != self.roster_name:
            await interaction.response.send_message("That roster has changed or no longer exists. Please reopen Manage Rosters and try again.", ephemeral=True)
            return

        del rosters[index]
        await save_roster(data, f"Deleted roster: {self.roster_name}")
        await update_roster(interaction.client)
        await interaction.response.edit_message(content=f"🗑️ Roster **{self.roster_name}** has been deleted.", view=None)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_delete(self, interaction, button):
        await interaction.response.edit_message(content="Roster deletion cancelled.", view=None)


class RosterActions(View):
    def __init__(self, roster_key):
        super().__init__(timeout=300)
        self.roster_key = roster_key
        if roster_key == "main":
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.label == "🗑 Delete Roster":
                    item.disabled = True

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

    @discord.ui.button(label="👑 Set Captain", style=discord.ButtonStyle.primary, row=1)
    async def set_captain(self, interaction, button):
        await interaction.response.send_message("Select this roster captain:", view=SelectView(CaptainSelect(self.roster_key)), ephemeral=True)

    @discord.ui.button(label="⭐ Set Co-Captain", style=discord.ButtonStyle.primary, row=1)
    async def set_co_captain(self, interaction, button):
        await interaction.response.send_message("Select this roster co-captain:", view=SelectView(CoCaptainSelect(self.roster_key)), ephemeral=True)

    @discord.ui.button(label="✏️ Rename Roster", style=discord.ButtonStyle.primary, row=2)
    async def rename_roster(self, interaction, button):
        data = await get_roster()
        current_name = next((name for key, name, _ in roster_entries(data) if key == self.roster_key), "")
        await interaction.response.send_modal(RosterNameModal("rename", self.roster_key, current_name))

    @discord.ui.button(label="🗑 Delete Roster", style=discord.ButtonStyle.danger, row=2)
    async def delete_roster(self, interaction, button):
        if self.roster_key == "main":
            await interaction.response.send_message("The main roster cannot be deleted.", ephemeral=True)
            return
        data = await get_roster()
        current_name = next((name for key, name, _ in roster_entries(data) if key == self.roster_key), None)
        if current_name is None:
            await interaction.response.send_message("That roster could not be found. Please reopen Manage Rosters.", ephemeral=True)
            return
        await interaction.response.send_message(
            f"⚠️ Are you sure you want to delete **{current_name}**? This removes its roster entry and player list.",
            view=ConfirmDeleteRoster(self.roster_key, current_name),
            ephemeral=True
        )


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

    @discord.ui.button(label="✏️ Rename Tryouts Heading", style=discord.ButtonStyle.secondary, row=2)
    async def rename_tryouts_heading(self, interaction, button):
        data = await get_roster()
        current_name = data.get("looking_at_name", "Tryouts")
        await interaction.response.send_modal(RosterNameModal("rename_tryouts", current_name=current_name))

    @discord.ui.button(label="🗑 Remove Roles", style=discord.ButtonStyle.danger, row=1)
    async def remove_roles(self, interaction, button):
        await interaction.response.send_message("Choose removal:", view=RemoveRoles(), ephemeral=True)


class DashboardRosterSelect(Select):
    def __init__(self, dashboard, options):
        super().__init__(placeholder="Choose roster", min_values=1, max_values=1, options=options[:25], row=0, custom_id="halo_dashboard_roster")
        self.dashboard = dashboard

    async def callback(self, interaction):
        self.dashboard.roster_key = self.values[0]
        self.dashboard.notice = None
        await self.dashboard.refresh()
        await interaction.response.edit_message(content=self.dashboard.status_text(), view=self.dashboard)


class DashboardActionSelect(Select):
    def __init__(self, dashboard):
        actions = [
            ("Add player", "add"), ("Remove player", "remove"),
            ("Set captain", "captain"), ("Set co-captain", "co"),
            ("Rename roster", "rename"), ("Delete roster", "delete"),
            ("Create roster", "create"), ("Add tryout", "tryout_add"),
            ("Remove tryout", "tryout_remove"), ("Rename tryouts heading", "rename_tryouts"),
            ("Remove captain", "remove_captain"), ("Remove co-captain", "remove_co")
        ]
        super().__init__(placeholder="Choose an action", min_values=1, max_values=1,
                         options=[discord.SelectOption(label=a, value=b) for a, b in actions],
                         row=1, custom_id="halo_dashboard_action")
        self.dashboard = dashboard

    async def callback(self, interaction):
        await self.dashboard.do_action(interaction, self.values[0])


class DashboardMemberSelect(UserSelect):
    def __init__(self, dashboard, action):
        placeholders = {"add": "Select player to add", "remove": "Select player to remove",
                        "captain": "Select captain", "co": "Select co-captain",
                        "tryout_add": "Select player for tryouts", "tryout_remove": "Select tryout to remove"}
        super().__init__(placeholder=placeholders[action], min_values=1, max_values=1, row=2,
                         custom_id="halo_dashboard_member_" + action)
        self.dashboard, self.action = dashboard, action

    async def callback(self, interaction):
        await interaction.response.defer()
        user = self.values[0]
        data = await get_roster()
        action, key = self.action, self.dashboard.roster_key
        if action in ("add", "remove", "captain", "co"):
            if key != "main":
                idx = int(key.split(":", 1)[1])
                rosters = data.setdefault("additional_rosters", [])
                if not 0 <= idx < len(rosters):
                    self.dashboard.notice = "That roster no longer exists. Select another roster."
                    await self.dashboard.refresh()
                    await interaction.response.edit_message(content=self.dashboard.status_text(), view=self.dashboard)
                    return
            players = get_players_for_key(data, key)
            if action == "add":
                if user.id in players:
                    self.dashboard.notice = f"{user.mention} is already on this roster."
                else:
                    players.append(user.id)
                    self.dashboard.notice = f"Added {user.mention}."
            elif action == "remove":
                if user.id in players:
                    players.remove(user.id)
                    self.dashboard.notice = f"Removed {user.mention} from this roster."
                else:
                    self.dashboard.notice = f"{user.mention} is not on this roster."
            else:
                field = "captain" if action == "captain" else "co_captain"
                if key == "main":
                    data[field] = user.id
                else:
                    data["additional_rosters"][int(key.split(":", 1)[1])][field] = user.id
                self.dashboard.notice = f"Set {field.replace('_', ' ')} to {user.mention}."
        else:
            people = data.setdefault("looking_at", [])
            if action == "tryout_add":
                if user.id not in people:
                    people.append(user.id)
                    self.dashboard.notice = f"Added {user.mention} to tryouts."
                else:
                    self.dashboard.notice = f"{user.mention} is already on tryouts."
            else:
                if user.id in people:
                    people.remove(user.id)
                    self.dashboard.notice = f"Removed {user.mention} from tryouts."
                else:
                    self.dashboard.notice = f"{user.mention} is not on tryouts."
        await save_roster(data, f"Roster editor: {action} {user.id}")
        await update_roster(interaction.client)
        self.dashboard.pending_action = None
        await self.dashboard.refresh()
        await interaction.response.edit_message(content=self.dashboard.status_text(), view=self.dashboard)


class DashboardNameModal(Modal):
    def __init__(self, dashboard, message, mode, current_name="", roster_key=None):
        titles = {"create": "Create Roster", "rename": "Rename Roster", "rename_tryouts": "Rename Tryouts Heading"}
        super().__init__(title=titles[mode])
        self.dashboard, self.message, self.mode, self.roster_key = dashboard, message, mode, roster_key
        self.name_input = TextInput(label="Name", default=current_name[:45] if current_name else None,
                                    placeholder="Enter a name", min_length=1, max_length=45)
        self.add_item(self.name_input)

    async def on_submit(self, interaction):
        name = str(self.name_input.value).strip()
        if not name:
            await interaction.response.send_message("Please enter a name.", ephemeral=True)
            return
        data = await get_roster()
        if self.mode == "create":
            rosters = data.setdefault("additional_rosters", [])
            rosters.append({"name": name, "players": [], "captain": None, "co_captain": None})
            self.dashboard.roster_key = f"extra:{len(rosters) - 1}"
            self.dashboard.notice = f"Created roster {name}. It is now selected."
            commit = f"Created roster: {name}"
        elif self.mode == "rename_tryouts":
            data["looking_at_name"] = name
            self.dashboard.notice = f"Renamed tryouts heading to {name}."
            commit = f"Renamed tryouts heading: {name}"
        else:
            if self.roster_key == "main":
                data["roster_name"] = name
            else:
                idx = int(self.roster_key.split(":", 1)[1])
                rosters = data.setdefault("additional_rosters", [])
                if not 0 <= idx < len(rosters):
                    await interaction.response.send_message("That roster no longer exists.", ephemeral=True)
                    return
                rosters[idx]["name"] = name
            self.dashboard.notice = f"Renamed roster to {name}."
            commit = f"Renamed roster: {name}"
        await save_roster(data, commit)
        await update_roster(interaction.client)
        await self.dashboard.refresh()
        await interaction.response.defer(ephemeral=True)
        try:
            await self.message.edit(content=self.dashboard.status_text(), view=self.dashboard)
        except discord.HTTPException as error:
            print(f"[Roster editor] Dashboard refresh after modal failed: {error}")


class DashboardDeleteConfirm(View):
    def __init__(self, dashboard, key, name):
        super().__init__(timeout=120)
        self.dashboard, self.key, self.name = dashboard, key, name

    @discord.ui.button(label="Confirm delete", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction, button):
        data = await get_roster()
        idx = int(self.key.split(":", 1)[1])
        rosters = data.setdefault("additional_rosters", [])
        if not 0 <= idx < len(rosters) or rosters[idx].get("name", "Additional Roster") != self.name:
            self.dashboard.notice = "Roster changed or no longer exists."
        else:
            del rosters[idx]
            self.dashboard.roster_key = "main"
            self.dashboard.notice = f"Deleted roster {self.name}."
            await save_roster(data, f"Deleted roster: {self.name}")
            await update_roster(interaction.client)
        await self.dashboard.refresh()
        await interaction.response.edit_message(content=self.dashboard.status_text(), view=self.dashboard)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction, button):
        await self.dashboard.refresh()
        await interaction.response.edit_message(content=self.dashboard.status_text(), view=self.dashboard)


class DashboardButton(discord.ui.Button):
    def __init__(self, dashboard, label, action):
        super().__init__(label=label, style=discord.ButtonStyle.secondary, row=3,
                         custom_id="halo_dashboard_" + action)
        self.dashboard, self.action = dashboard, action

    async def callback(self, interaction):
        if self.action == "refresh":
            await update_roster(interaction.client)
            self.dashboard.notice = "Dashboard refreshed."
        else:
            self.dashboard.roster_key = "main"
            self.dashboard.notice = "Selection reset to the main roster."
        await self.dashboard.refresh()
        await interaction.response.edit_message(content=self.dashboard.status_text(), view=self.dashboard)


class RosterDashboard(View):
    def __init__(self):
        super().__init__(timeout=1800)
        self.roster_key = "main"
        self.notice = None
        self.pending_action = None

    @classmethod
    async def create(cls):
        view = cls()
        await view.refresh()
        return view

    def status_text(self):
        notice = f"\n\n{self.notice}" if self.notice else ""
        return ("🟢 **HALO Roster Editor**\n"
                f"**Selected roster:** {getattr(self, 'selected_name', 'Main roster')}\n"
                "Choose a roster and an action below. This panel updates in place, so you can make multiple changes without running /rosterupdate again."
                + notice)

    async def refresh(self):
        self.clear_items()
        data = await get_roster()
        entries = roster_entries(data)
        valid = [key for key, _name, _players in entries]
        if self.roster_key not in valid:
            self.roster_key = "main"
        self.selected_name = next((name for key, name, _players in entries if key == self.roster_key), "Main roster")
        options = [discord.SelectOption(label=name[:100], value=key, default=key == self.roster_key)
                   for key, name, _players in entries]
        self.add_item(DashboardRosterSelect(self, options))
        self.add_item(DashboardActionSelect(self))
        if self.pending_action:
            self.add_item(DashboardMemberSelect(self, self.pending_action))
        self.add_item(DashboardButton(self, "🔄 Refresh", "refresh"))
        self.add_item(DashboardButton(self, "↩️ Main roster", "main"))
        return self

    async def do_action(self, interaction, action):
        self.notice = None
        self.pending_action = None
        if action in ("add", "remove", "captain", "co", "tryout_add", "tryout_remove"):
            self.pending_action = action
        elif action in ("create", "rename", "rename_tryouts"):
            data = await get_roster()
            current = ""
            key = self.roster_key
            if action == "rename":
                current = next((name for entry_key, name, _ in roster_entries(data) if entry_key == key), "")
            elif action == "rename_tryouts":
                current = data.get("looking_at_name", "Tryouts")
            await interaction.response.send_modal(DashboardNameModal(self, interaction.message, action, current, key))
            return
        elif action == "delete":
            if self.roster_key == "main":
                self.notice = "The main roster is protected and cannot be deleted."
            else:
                data = await get_roster()
                current = next((name for key, name, _ in roster_entries(data) if key == self.roster_key), None)
                if current is not None:
                    await interaction.response.edit_message(
                        content=f"⚠️ Delete **{current}** and its player list? This cannot be undone.",
                        view=DashboardDeleteConfirm(self, self.roster_key, current))
                    return
                self.notice = "That roster no longer exists. Refresh and select another."
        elif action in ("remove_captain", "remove_co"):
            data = await get_roster()
            field = "captain" if action == "remove_captain" else "co_captain"
            if self.roster_key == "main":
                data[field] = None
            else:
                idx = int(self.roster_key.split(":", 1)[1])
                rosters = data.setdefault("additional_rosters", [])
                if not 0 <= idx < len(rosters):
                    self.notice = "That roster no longer exists."
                else:
                    rosters[idx][field] = None
            await save_roster(data, f"Removed {field} for {self.roster_key}")
            await update_roster(interaction.client)
            self.notice = f"Removed {field.replace('_', ' ')}."
        await self.refresh()
        await interaction.response.edit_message(content=self.status_text(), view=self)
