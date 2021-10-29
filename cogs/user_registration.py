import discord
import os
import re
import main
import asyncio
from discord.ext import commands


def is_valid_name(name: str) -> bool:
	split_name = name.split(' ')
	if len(split_name) != 2 and len(split_name) != 3:
		return False

	for word in split_name:
		for char in word:
			if not 64 < ord(char) < 91 and not 94 < ord(char) < 123:
				return False

	return True


def group_role_name(name: str) -> str:
	split_name = name.split(' ')
	new_name = ''
	for word in split_name:
		new_name += word[0].upper() + word[1:len(word)] + ' '

	return new_name


def get_roles(member):
	roles = []
	for role in member.guild.roles:
		group_role = re.findall('^[A-Z][a-zA-Z]-[0-9]{4}[A-Z]?$', role.name)
		if group_role != [] and role.name == group_role[0]:
			roles.append(role)
	return roles


def embeded(title, description, colour=discord.Colour.blue()):
	embed = discord.Embed(
		title=title,
		description=description,
		colour=colour
	)
	return embed


def get_disctionary_of_roles(roles):
	groups = {}
	for role in roles:
		group, year = role.name.split('-')
		if group not in groups.keys():
			groups[group] = year
		elif group in groups.keys():
			if type(groups[group]) is str:
				lis = [groups[group], year]
				groups[group] = lis
			elif type(groups[group]) is list:
				lis = groups[group]
				lis.append(year)
				groups[group] = lis
	return groups


def create_buttons(labels):
	btn_list = [[], [main.Button(style=main.ButtonStyle.red, label="Renunta")]]
	row = 0
	for label in labels:
		if len(btn_list[row]) >= 5 and row == 0:
			row += 1
			btn_list.insert(row, [])
		btn_list[row].append(main.Button(style=main.ButtonStyle.blue, label=label))
	return btn_list


# Initierea clasului
class OnEventTrigger(commands.Cog):
	def __init__(self, client):
		self.client = client

	# When member joins the guild
	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		timeout = 60
		event = None

		message = f'Introduceti **`Numele Prenumele`** dumneavoastra'
		embed = embeded('Inregistrare in CEEE', message, discord.Colour.green())
		msg = await member.send(embed=embed)

		def check(the_event_message):
			return the_event_message.author.id == member.id

		try:
			event = await self.client.wait_for('message', timeout=timeout, check=check)
		except asyncio.TimeoutError:
			message = 'Timpul acordat pentru inregistrare s-a scurs. Pentru a va putea inregistra, accesati linkul de mai jos.\nhttps://discord.gg/SQnZ3scFmb'
			embed = embeded('Inregistrare respinsa', message, discord.Colour.red())
			await msg.edit(embed=embed, components=[])
			await member.guild.kick(member)
		else:
			# Definirea variabilelor
			name = event.content
			statut = None
			roles = get_roles(member)
			groups = get_disctionary_of_roles(roles)
			timeout = 30
			exit_message = ''
			language = ''
			year = ''
			group = ''

			# Verificarea parametrului name la simboluri
			if not is_valid_name(name):
				message = 'Numele introdus contine simboluri. Pentru a va putea inregistra, accesati linkul de mai jos.\nhttps://discord.gg/SQnZ3scFmb'
				embed = embeded('Inregistrare respinsa', message, discord.Colour.red())
				await member.send(embed=embed, components=[])
				await member.guild.kick(member)
				return

			# Definirea statutului utilizatorului
			statuses = [[
				main.Button(style=main.ButtonStyle.blue, label="Elev"),
				main.Button(style=main.ButtonStyle.blue, label="Profesor"),
			], [
				main.Button(style=main.ButtonStyle.red, label="Renunta")
			]]

			message = f'**Numele:** `{name}`'
			embed = embeded('Statutul', message, discord.Colour.green())
			msg = await member.send(embed=embed, components=statuses)

			# Verificarea butonului apasat
			def check(the_interacted_ctx):
				return the_interacted_ctx.author == member

			try:
				event = await self.client.wait_for('button_click', timeout=timeout, check=check)
			# Exceptie timpul de asteptare finisat
			except main.asyncio.TimeoutError:
				# Proces oprit din cauza inactivitatii
				exit_message = 'Procesul a fost oprit din cauza inactivitatii utilizatorului'
				statut = 'exit'
			else:
				if event.component.label == 'Elev' or event.component.label == 'Profesor':
					statut = event.component.label
				elif event.component.label == 'Renunta':
					statut = 'exit'
					exit_message = 'Procesul a fost oprit de utilizator'
			await event.respond(type=6)

			phase = 0
			# Adaugarea rolurilor pentru Elevi
			if statut == 'Elev':
				year = None
				group = None
				language = None
				while phase < 3:
					# Phase 0 -  Alegerea grupei / specialitatii
					if phase == 0:
						labels = list(groups.keys())
						groupe = create_buttons(labels)
						message += f'\n**Statutul:** `{statut}`'
						embed = embeded('Grupa/Specialitatea', message, discord.Colour.green())
						await msg.edit(embed=embed, components=groupe)

						# Verificarea butonului apasat
						try:
							event = await self.client.wait_for('button_click', timeout=timeout, check=check)
						# Exceptie timpul de asteptare finisat
						except main.asyncio.TimeoutError:
							# Proces oprit din cauza inactivitatii
							exit_message = 'Procesul a fost oprit din cauza inactivitatii utilizatorului'
							statut = 'exit'
							break
						else:
							if event.component.label == 'Renunta':
								exit_message = 'Procesul a fost oprit de utilizator'
								statut = 'exit'
								await event.respond(type=6)
								break
							else:
								group = event.component.label
						await event.respond(type=6)
						phase += 1

					# Phase 1 - Alegerea grupului/specialitatii
					if phase == 1:
						labels = groups[group]
						years = create_buttons(labels)
						message += f'\n**Grupa:** `{group}`'
						embed = embeded('Anul de studii', message, discord.Colour.green())
						await msg.edit(embed=embed, components=years)

						# Verificarea butonului apasat
						try:
							event = await self.client.wait_for('button_click', timeout=timeout, check=check)
						# Exceptie timpul de asteptare finisat
						except main.asyncio.TimeoutError:
							# Proces oprit din cauza inactivitatii
							exit_message = 'Procesul a fost oprit din cauza inactivitatii utilizatorului'
							statut = 'exit'
							break
						else:
							if event.component.label == 'Renunta':
								exit_message = 'Procesul a fost oprit de utilizator'
								statut = 'exit'
								await event.respond(type=6)
								break
							else:
								year = event.component.label
						await event.respond(type=6)
						phase += 1

					# Phase 2 - Alegerea limbii straine vorbite
					if phase == 2:
						languages = create_buttons(['limba-engleza', 'limba-franceza'])
						message += f'\n**Anul:** `{year}`'
						embed = embeded('Limba straina', message, discord.Colour.green())
						await msg.edit(embed=embed, components=languages)

						# Verificarea butonului apasat
						try:
							event = await self.client.wait_for('button_click', timeout=timeout, check=check)
						# Exceptie timpul de asteptare finisat
						except main.asyncio.TimeoutError:
							# Proces oprit din cauza inactivitatii
							exit_message = 'Procesul a fost oprit din cauza inactivitatii utilizatorului'
							statut = 'exit'
							break
						else:
							if event.component.label == 'Renunta':
								exit_message = 'Procesul a fost oprit de utilizator'
								statut = 'exit'
								await event.respond(type=6)
								break
							elif event.component.label == 'limba-engleza' or event.component.label == 'limba-franceza':
								language = event.component.label
								message += f'\n**Limba straina:** `{language}`'
								embed = embeded('Asteptare', message, discord.Colour.green())
								await msg.edit(embed=embed, components=[])
						await event.respond(type=6)
						phase += 1
			# Adaugarea rolurilor pentru Profesori
			elif statut == 'Profesor':
				# Returnarea mesajului finisat
				message += f'\n**Statutul:** `{statut}`'

			# Iesirea din commanda
			if statut == 'exit':
				message = 'Pentru a va putea inregistra, accesati linkul de mai jos.\nhttps://discord.gg/SQnZ3scFmb'
				embed = embeded('Inregistrare respinsa', f'{exit_message}\n{message}', discord.Colour.red())
				await msg.edit(embed=embed, components=[])
				await member.guild.kick(member)
				return

			# Adaugarea rolurilor si a nickname-ului
			await member.edit(nick=name)
			# Adaugarea rolurilor
			for role in member.guild.roles:
				# Elev
				if statut == 'Elev':
					# Statutul
					if role.name == statut:
						await member.add_roles(role)
					# Grupa
					elif role.name == f'{group}-{year}':
						await member.add_roles(role)
					# Limba straina
					elif role.name == language and role.colour.value == 6323595:
						await member.add_roles(role)
				# Profesor
				if statut == 'Profesor':
					# Profesor?
					if role.name == 'Profesor?':
						await member.add_roles(role)
				# Membru nou
				if role.name == 'Membru':
					await member.remove_roles(role)
				elif role.name == 'Membru Nou':
					await member.add_roles(role)
			# Mesaj ca totul sa executat cu success
			embed = embeded('Inregistrare finisata', message, discord.Colour.green())
			await msg.edit(embed=embed, components=[])

	@commands.command(aliases=['addsubj'])
	async def add_school_subjects_to_the_teacher(self, ctx, member: discord.Member, arguments):
		await ctx.channel.purge(limit=1)

		embed_message = ''
		subjects_and_classes = arguments.split(';')
		roles_list = []
		for element in subjects_and_classes:
			subject, groups = element.split(':')
			groups = groups.split(',')
			embed_message += f'{subject} - {", ".join(groups)}; '
			role_element = f'#{subject}'
			for group in groups:
				role_element += f'_{group}'
			roles_list.append(role_element)

		guild_roles = [guild_role.name for guild_role in ctx.guild.roles]
		for role in roles_list:
			if role not in guild_roles:
				await ctx.guild.create_role(name=role, colour=0x11806A)
			for guild_role in ctx.guild.roles:
				if guild_role.name == role:
					await member.add_roles(guild_role)

		embed = embeded('Profesor Adaugat', f'Membrul: {member}\nRoluri:\n{embed_message}', discord.Colour.green())
		await ctx.channel.send(embed=embed)


def setup(client):
	client.add_cog(OnEventTrigger(client))
