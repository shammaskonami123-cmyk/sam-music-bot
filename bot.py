import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

queues = {}

async def search_youtube(query):
    ydl_opts = {'format': 'bestaudio', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        return info['url'], info['title']

async def play_next(vc, interaction):
    if queues.get(interaction.guild.id):
        url = queues[interaction.guild.id].pop(0)
        source = await discord.FFmpegOpusAudio.from_probe(url)
        vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(vc, interaction), bot.loop))

class PlayerControls(discord.ui.View):
    def __init__(self, vc):
        super().__init__(timeout=None)
        self.vc = vc

    @discord.ui.button(label="⏸ Pause", style=discord.ButtonStyle.primary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc.is_playing():
            self.vc.pause()
            await interaction.response.send_message("Paused", ephemeral=True)

    @discord.ui.button(label="▶ Resume", style=discord.ButtonStyle.success)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.vc.is_paused():
            self.vc.resume()
            await interaction.response.send_message("Resumed", ephemeral=True)

    @discord.ui.button(label="⏹ Stop", style=discord.ButtonStyle.danger)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.vc.stop()
        await interaction.response.send_message("Stopped", ephemeral=True)

@tree.command(name="play", description="Play song")
async def play(interaction: discord.Interaction, query: str):

    if not interaction.user.voice:
        await interaction.response.send_message("Voice il kayar bro 😅")
        return

    await interaction.response.defer()

    vc = interaction.guild.voice_client
    if not vc:
        vc = await interaction.user.voice.channel.connect()

    url, title = await search_youtube(query)

    if interaction.guild.id not in queues:
        queues[interaction.guild.id] = []

    if vc.is_playing():
        queues[interaction.guild.id].append(url)
        await interaction.followup.send(f"Added: {title}")
    else:
        source = await discord.FFmpegOpusAudio.from_probe(url)
        vc.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(play_next(vc, interaction), bot.loop))
        
        view = PlayerControls(vc)
        await interaction.followup.send(f"Playing: {title}", view=view)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")

bot.run("MTQ4NzA0OTM5NzM5MTg1NTY0Nw.GT3nbr.9CvXlP8bxPwLk8Gg6KEbbO8y-V0fa8UH6_9hiY")
import os
bot.run(os.getenv("MTQ4NzA0OTM5NzM5MTg1NTY0Nw.GT3nbr.9CvXlP8bxPwLk8Gg6KEbbO8y-V0fa8UH6_9hiY"))