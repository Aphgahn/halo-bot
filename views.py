import discord


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
            "Captain selection menu coming in Part 4.",
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
            "Co-Captain selection menu coming in Part 4.",
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
            "Player slot menu coming in Part 4.",
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
            "Looking At menu coming in Part 4.",
            ephemeral=True
        )
