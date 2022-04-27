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
mydb = database.DBlib(host=config.school_host, user=config.school_user, password=config.school_password, database=config.school_database)
cog_names = []


async def verify_members(guild: discord.Guild):
	table = 'RegistrationInformation'
	if guild:
		time = 0
		while True:
			if time != datetime.date.today():
				mydb.connect()
				try:
					rows = mydb.read_rows(table, mydb.last_row_id(table))
				except IndexError:
					rows = None
				if rows:
					for member in guild.members:
						for row in rows:
							if member.id == int(row[1]):
								if row[3] == 'waiting':
									if row[2] + datetime.timedelta(days=5) < datetime.date.today():
										await member.guild.kick(member)
										mydb.delete(table, int(row[0]))
				time = datetime.date.today()
				await asyncio.sleep(3600000)


@client.event
async def on_ready():
	DiscordComponents(client)
	print(f'Connected as {client.user.name} (ID:{client.user.id})')

	my_guild = None
	for guild in client.guilds:
		if guild.id == config.guild_id:
			my_guild = guild
			break

	await verify_members(my_guild)


for filename in os.listdir('cogs'):
	if filename.endswith('.py'):
		client.load_extension(f'cogs.{filename[:-3]}')
		cog_names.append(filename[:-3])

if not config.is_local_run:
	import keep_alive
	keep_alive.keep_alive()

client.run(config.TOKEN)
