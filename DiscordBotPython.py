import discord
from discord.ext import commands
import asyncio

# 1. Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 2. View for the main ticket creation panel
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Persistent view

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket_btn")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # FIX: Defer the response immediately to prevent the 3-second timeout error
        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild

        # Check if the user already has an open ticket channel
        existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{interaction.user.name.lower()}")
        if existing_channel:
            await interaction.followup.send(f"You already have an open ticket: {existing_channel.mention}", ephemeral=True)
            return

        # Set up channel permissions (Only user, bot, and admins can view)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)
        }

        # Create a private text channel
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            overwrites=overwrites,
            topic=f"Support ticket for {interaction.user.name} (ID: {interaction.user.id})"
        )

        # Send welcome message inside the new ticket with a close button
        embed = discord.Embed(
            title="Support Ticket",
            description=f"Hello {interaction.user.mention}! Support staff will be with you shortly.\nClick the button below when you are ready to close this ticket.",
            color=discord.Color.blue()
        )
        await ticket_channel.send(embed=embed, view=CloseTicketView())

        # Notify the user privately using followup instead of response
        await interaction.followup.send(f"Your ticket has been created: {ticket_channel.mention}", ephemeral=True)

# 3. View for closing an active ticket channel
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Closing this ticket channel in 5 seconds...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Ticket system is online and ready!")

# 4. Command to deploy the ticket panel message
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Sends the panel with the button to create a ticket."""
    embed = discord.Embed(
        title="Support Center",
        description="Need assistance? Click the button below to open a private support ticket with our staff.",
        color=discord.Color.blurple()
    )
    await ctx.send(embed=embed, view=TicketView())
    await ctx.message.delete() # Clean up the setup command message

# 5. Run the bot using your token directly
TOKEN = "Put your discord bot token here."

bot.run(TOKEN)
