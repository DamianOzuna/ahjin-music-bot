import discord
from discord.ext import commands
import yt_dlp as youtube_dl

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

audio_queues = {}

@bot.event
async def on_ready():
	print(f'Bot is online as {bot.user.name}')



@bot.command
async def skip(ctx):
	if not ctx.voice_client:
		return await ctx.send('Bot is currently not playing music')

	queue = audio_queues.get(ctx.guild.id)
	if not queue:
		return await ctx.send('There are no songs in queue')

	await ctx.voice_client.stop()
	await play_song(ctx, ctx.voice_client)


@bot.command()
async def stop(ctx):
	if not ctx.voice_client:
		return await ctx.send('The bot is not currently playing music')

	audio_queues[ctx.guild.id] = []
	await ctx.voice_client.stop()


@bot.command()
async def play(ctx, url):
	if not ctx.author.voice:
		return await ctx.send('You need to be in a voice channel to use this')

	voice_channel = ctx.author.voice.channel
	voice_client = ctx.voice_client

	if voice_client and voice_client.channel != channel:
		return await ctx.send('Bot is already playing music in a channel')

	if not url.startswith('https://www.youtube.com/watch?v='):
		return await ctx.send('Invalid URL')

	queue = audio_queues.get(ctx.guild.id)

	if not queue:
		queue = []
		audio_queues[ctx.guild.id] = queue

		queue.append(url)

	if not voice_client:
		voice_client = await voice_channel.connect()

	if len(queue) == 1:
		await play_song(ctx, voice_client)


async def play_song(ctx, voice_client):
	queue = audio_queues.get(ctx.guild.id)

	if not queue:
		return await voice_client.disconnect()

	url = queue[0]

	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192'
		}],
		'outtmpl': '%(id)s.mp3',
		'quiet': True
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		info = ydl.extract_info(url, download=False)
		audio_url = info['url']

	voice_client.play(discord.FFmpegPCMAudio(audio_url), after=lambda _: bot.loop.create_task(play_song(ctx, voice_client)))

	del queue[0]

bot.run('')