# Importarea librariilor
import os
import pytz
import discord
import asyncio
import datetime
from datetime import date
import database
import config
from discord.ext import commands
from discord_components import *
# from discord_slash import SlashCommand

# Initializarea discord
intents = discord.Intents.all()
client = commands.Bot(command_prefix=config.cmd_prefix, case_insensitive=True, intents=intents)
# slash = SlashCommand(client, sync_commands=True)

SchoolDB = database.DBlib(host=config.school_host, user=config.school_user, password=config.school_password, database=config.school_database)
cog_names = []


@client.event
async def on_ready():
	DiscordComponents(client)
	print(f'Connected as {client.user.name} (ID:{client.user.id})')


for filename in os.listdir('cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')
		cog_names.append(filename[:-3])

if not config.is_local_run:
	import keep_alive
	keep_alive.keep_alive()

client.run(config.TOKEN)
