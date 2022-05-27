import discord
import discord_components
from discord_components import DiscordComponents, Button, ButtonStyle
import database
import datetime

import main
import config
import asyncio
from discord.ext import commands
import validator as valid

# Primary    |  1  |  blurple
# Secondary  |  2  |  grey
# Success    |  3  |  green
# Danger     |  4  |  red
# Link       |  5  |  grey, navigates to a URL

mydb = database.DBlib(config.school_host, config.school_user, config.school_password, config.school_database)


def embeded(title, description, colour=discord.Colour.blue()):
	embed = discord.Embed(
		title=title,
		description=description,
		colour=colour
	)
	return embed


def get_dictionary_of_roles(roles):
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


def create_buttons(labels, btn_style: main.ButtonStyle = 1):
	btn_list = [[], [main.Button(style=4, label="Renunță")]]
	row = 0
	if type(labels) is not str:
		for label in labels:
			if len(btn_list[row]) >= 5:
				row += 1
				btn_list.insert(row, [])
			btn_list[row].append(main.Button(style=btn_style, label=label))
	else:
		btn_list[row].append(main.Button(style=btn_style, label=labels))
	return btn_list


async def do_required_roles_exist(member: discord.Member, asked_roles: [str]):
	roles = [role.name for role in member.guild.roles]
	counter = 0

	for asked_role in asked_roles:
		if asked_role not in roles:
			await member.guild.create_role(name=asked_role, colour=0x546E7A)
			if counter == 0:
				counter += 1
				embed = embeded('Notificare', 'Au fost adaugate roluri noi de elev.\nEste necesar de repoziționat rolurile', discord.Colour.green())
				await member.guild.get_channel(904096410532724756).send(embed=embed)


async def confirm_member(category: discord.CategoryChannel, member: discord.Member):
	role_names = []
	unconfirmed_member_role = None
	for role in member.roles:
		role_names.append(role.name)
		if role.name == config.unconfirmed_member_role_name:
			unconfirmed_member_role = role

	language_channel_names = [config.english_channel_name, config.francais_channel_name]
	for channel in category.channels:
		if channel.name in language_channel_names:
			if channel.name in role_names:
				await channel.set_permissions(member, view_channel=True)
		else:
			await channel.set_permissions(member, view_channel=True)

	await member.remove_roles(unconfirmed_member_role)


def add_member_to_wait_list(member: discord.Member):
	mydb.connect()
	mydb.insert('RegistrationInformation', ['UserID', 'Data', 'Status'], [member.id, datetime.date.today(), 'waiting'])		# 'blocked', 'waiting'


def remove_member_from_wait_list(this_member: discord.Member):
	table = 'RegistrationInformation'
	try:
		rows = mydb.read_rows(table, mydb.last_row_id(table))
	except IndexError:
		rows = None
	if rows:
		for member in this_member.guild.members:
			if member == this_member:
				for row in rows:
					if member.id == int(row[1]):
						mydb.delete(table, int(row[0]))


# Initierea clasului
class OnEventTrigger(commands.Cog):
	def __init__(self, client):
		self.client = client

	# When member joins the guild
	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		mydb.connect()
		# Definirea variabilelor esentiale
		registration_timeout = 180
		timeout = 30

		# verificare daca membrul este bot
		if member.bot:
			return
		else:
			table = 'RegistrationInformation'
			try:
				rows = mydb.read_rows(table, mydb.last_row_id(table))
			except IndexError:
				rows = None
			if rows:
				for member in member.guild.members:
					for row in rows:
						if member.id == int(row[1]):
							add_member_to_list = False
							if row[3] == 'blocked':
								await member.guild.kick(member)
								# Se trimite mesaj utilizatorului nou.
								message = 'Încercarea dumneavoastră de a vă conecta a eșuat.\nDumneavoastră vă aflați în lista persoanelor nedorite pe acest server.'
								embed = discord.Embed(title='Înregistrare în CEEE', description=message, colour=discord.Colour.dark_red())
								await member.send(embed=embed)
								# Se trimite mesaj de notificare in canalul de notificari al serverului.
								message = f'Membrul: {member}\nStatutul: {row[3]}\nA fost cu succes dat afară!'
								embed = discord.Embed(title='Membru nou', description=message, colour=discord.Colour.dark_red())
								await member.guild.get_channel(config.bot_notification_channel_id).send(embed=embed)
								return

		# Se trimite mesaj utilizatorului nou.
		embed = discord.Embed(title='Înregistrare în CEEE', description='Transmiteți botului mesaj ce conține **`Numele Prenumele`** dumneavoastră.', colour=discord.Colour.blue())
		msg_to_user: discord.Message = await member.send(embed=embed)

		# Se trimite mesaj de notificare in canalul de notificari al serverului.
		embed = discord.Embed(title='Membru nou', description=f'Se asteaptă raspuns de la {member}', colour=discord.Colour.gold())
		notification_msg = await member.guild.get_channel(config.bot_notification_channel_id).send(embed=embed)
		add_member_to_wait_list(member)

		def check(the_event_message):
			return the_event_message.author.id == member.id

		# Se asteapta numele utilizatorului in format de mesaj.
		try:
			event = await self.client.wait_for('message', timeout=registration_timeout, check=check)
		except asyncio.TimeoutError:
			message = f'Timpul acordat pentru înregistrare s-a scurs. Dumneavoastră puteți în decurs de 5 zile să vă înregistrați pe site {config.website_link}'
			embed = discord.Embed(title='Înregistrare amânată', description=message, colour=discord.Colour.gold())
			await msg_to_user.edit(embed=embed)
			embed = discord.Embed(title='Membru nou', description=f'{member} - a fost adăugat în lista de așteptare pentru înregistrare pe site\nMotivul: *inactivitate*', colour=discord.Colour.gold())
			await notification_msg.edit(embed=embed)
			return

		# Definirea variabilelor
		new_member_name = event.content
		statut = None
		roles = [x for x in member.guild.categories if valid.is_valid_group_name(x.name)]
		groups = get_dictionary_of_roles(roles)
		inactivity_message = 'Procesul a fost oprit din cauza inactivității utilizatorului'
		dismiss_message = 'Procesul a fost oprit de utilizator'
		rejoin_message = f'Pentru a va înregistra din nou, accesați link-ul următor: {config.server_join_link}'
		exit_message = ''
		language = ''
		year = ''
		group = ''

		# Se verifica daca noul utilizator a scris un nume valid
		if not valid.is_valid_member_name(new_member_name):
			message = 'Numele sau prenumlele introdus nu satisface cerintelor:'
			message += '\n```1. Numele trebuie sa conțină numai litere latine.'
			message += '\n2. Mesajul cu numele și prenumele trimis trebuie să fie format din 2 sau 3 cuvinte.'
			message += '\n3. Prima literă a fiecărui cuvânt trebuie să fie masjuscula.'
			message += '\n4. Numărul minim de litere în cuvânt trebuie să fie egal cu 3 sau mai mare.```'
			message += f'\n**Dumneavoastră puteți în decurs de 5 zile să vă înregistrați pe website** {config.website_link}'
			embed = discord.Embed(title='Înregistrare amânată', description=message, colour=discord.Colour.red())
			await member.send(embed=embed)

			embed = discord.Embed(title='Membru nou', description=f'{member} - a fost adăugat în lista de așteptare pentru înregistrare pe site\nMotivul: *nume incorect*\n|{new_member_name}|', colour=discord.Colour.red())
			await notification_msg.edit(embed=embed)
			# await member.guild.kick(member)
			return

		# Definirea statutului utilizatorului
		btns = [[
			main.Button(style=main.ButtonStyle.blue, label=config.student_role_name),
			main.Button(style=main.ButtonStyle.blue, label=config.teacher_role_name),
			],
			[
			main.Button(style=main.ButtonStyle.red, label="Renunță")]
			]

		message = f'**Numele:** `{new_member_name}`'
		embed = embeded('Statutul', message, discord.Colour.green())
		msg_to_user = await member.send(embed=embed, components=btns)

		# Verificarea butonului apasat
		def check(the_interacted_ctx):
			return the_interacted_ctx.author == member

		try:
			event = await self.client.wait_for('button_click', timeout=timeout, check=check)
		# Exceptie timpul de asteptare finisat
		except main.asyncio.TimeoutError:
			# Proces oprit din cauza inactivitatii
			exit_message = inactivity_message
			statut = 'exit'
		else:
			if event.component.label == config.student_role_name or event.component.label == config.teacher_role_name:
				statut = event.component.label
			elif event.component.label == 'Renunță':
				statut = 'exit'
				exit_message = dismiss_message
		await event.respond(type=6)

		phase = 0
		# Adaugarea rolurilor pentru Elevi
		if statut == config.student_role_name:
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
					await msg_to_user.edit(embed=embed, components=groupe)

					# Verificarea butonului apasat
					try:
						event = await self.client.wait_for('button_click', timeout=timeout, check=check)
					# Exceptie timpul de asteptare finisat
					except main.asyncio.TimeoutError:
						# Proces oprit din cauza inactivitatii
						exit_message = inactivity_message
						statut = 'exit'
						break
					else:
						if event.component.label == 'Renunță':
							exit_message = dismiss_message
							statut = 'exit'
							await event.respond(type=6)
							break
						else:
							group = event.component.label
					await event.respond(type=6)
					phase += 1

				# Phase 1 - Alegerea anului
				if phase == 1:
					labels = groups[group]
					years = create_buttons(labels)
					message += f'\n**Grupa:** `{group}`'
					embed = embeded('Anul de studii', message, discord.Colour.green())
					await msg_to_user.edit(embed=embed, components=years)

					# Verificarea butonului apasat
					try:
						event = await self.client.wait_for('button_click', timeout=timeout, check=check)
					# Exceptie timpul de asteptare finisat
					except main.asyncio.TimeoutError:
						# Proces oprit din cauza inactivitatii
						exit_message = inactivity_message
						statut = 'exit'
						break
					else:
						if event.component.label == 'Renunță':
							exit_message = dismiss_message
							statut = 'exit'
							await event.respond(type=6)
							break
						else:
							year = event.component.label
					await event.respond(type=6)
					phase += 1

				# Phase 2 - Alegerea limbii straine vorbite
				if phase == 2:
					languages = create_buttons([config.english_channel_name, config.francais_channel_name])
					message += f'\n**Anul:** `{year}`'
					embed = embeded('Limba străină', message, discord.Colour.green())
					await msg_to_user.edit(embed=embed, components=languages)

					# Verificarea butonului apasat
					try:
						event = await self.client.wait_for('button_click', timeout=timeout, check=check)
					# Exceptie timpul de asteptare finisat
					except main.asyncio.TimeoutError:
						# Proces oprit din cauza inactivitatii
						exit_message = inactivity_message
						statut = 'exit'
						break
					else:
						if event.component.label == 'Renunță':
							exit_message = dismiss_message
							statut = 'exit'
							await event.respond(type=6)
							break
						elif event.component.label == config.english_channel_name or event.component.label == config.francais_channel_name:
							language = event.component.label
							message += f'\n**Limba străină:** `{language}`'
							embed = embeded('Așteptare', message, discord.Colour.dark_green())
							await msg_to_user.edit(embed=embed, components=[])
					await event.respond(type=6)
					phase += 1
		# Adaugarea rolurilor pentru Profesori
		elif statut == config.teacher_role_name:
			# Returnarea mesajului finisat
			message += f'\n**Statutul:** `{statut}`'

		# Iesirea din commanda
		if statut == 'exit':
			if message == inactivity_message:
				message = rejoin_message
				embed = embeded('Înregistrare respinsă', f'{exit_message}\n{message}', discord.Colour.red())
				await msg_to_user.edit(embed=embed, components=[])
				notification_msg_embed = embeded('Membru nou', f'{member} - a fost adăugat în lista de așteptare pentru înregistrare pe site\nMotivul: *inactivitate*', discord.Colour.red())
				await notification_msg.edit(embed=notification_msg_embed)
				return
			else:
				message = rejoin_message
				embed = embeded('Înregistrare respinsă', f'{exit_message}\n{message}', discord.Colour.red())
				await msg_to_user.edit(embed=embed, components=[])
				await member.guild.kick(member)
				notification_msg_embed = embeded('Membru nou', f'{member} - a fost dat afară\nMotivul: *membrul a renunțat*', discord.Colour.red())
				await notification_msg.edit(embed=notification_msg_embed)
				return

		if statut == config.student_role_name:
			await do_required_roles_exist(member, [group, year])

		# Adaugarea rolurilor si a nickname-ului
		await member.edit(nick=new_member_name)
		# Adaugarea rolurilor
		for role in member.guild.roles:
			# Elev
			if statut == config.student_role_name:
				# Statutul
				if role.name == statut:
					await member.add_roles(role)
				# Grupa si anul
				elif role.name == group or role.name == year:
					await member.add_roles(role)
				# Limba straina
				elif role.name == language and role.colour.value == 6323595:
					await member.add_roles(role)
			# Profesor
			if statut == config.teacher_role_name:
				# Profesor?
				if role.name == config.teacher_role_name:
					await member.add_roles(role)
			if role.name == config.unconfirmed_member_role_name:
				await member.add_roles(role)
		# Mesaj ca totul sa executat cu success
		embed = embeded('Înregistrare finisată', message, discord.Colour.green())
		await msg_to_user.edit(embed=embed, components=[])
		notification_msg_embed = embeded('Membru nou', f'{member} - a finisat înregistrarea\nNumele: *{new_member_name}*\nStatutul: {statut}', discord.Colour.green())
		await notification_msg.edit(embed=notification_msg_embed)
		remove_member_from_wait_list(member)

	@commands.command(aliases=['addsub'])
	@commands.has_role('Admin')
	async def add_school_subjects_to_the_teacher(self, ctx: discord.ext.commands.Context, member: discord.Member, arguments):
		await ctx.channel.purge(limit=1)

		if type(member) is not discord.Member:
			embed = embeded('Adăugare profesor', f'Nu a fost introdus un membru.', discord.Colour.red())
			await ctx.channel.send(embed=embed)
			return

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
				elif guild_role.name == config.unconfirmed_member_role_name:
					await member.remove_roles(guild_role)

		embed = embeded('Profesor Adaugat', f'Membrul: {member}\nRoluri:\n{embed_message}', discord.Colour.green())
		await ctx.channel.send(embed=embed)

	# @commands.command(aliases=['newsub'])
	# @commands.has_role('Admin')
	# async def new_school_subjects_to_the_teacher(self, ctx: discord.ext.commands.Context, member: discord.Member):
	# 	await ctx.channel.purge(limit=1)
	#
	# 	if type(member) is not discord.Member:
	# 		embed = embeded('Adaugare profesor', f'Nu a fost introdus un membru.', discord.Colour.red())
	# 		await ctx.channel.send(embed=embed)
	# 		return
	#
	# 	embed_message = ''
	# 	subjects_and_classes = arguments.split(';')
	# 	roles_list = []
	# 	for element in subjects_and_classes:
	# 		subject, groups = element.split(':')
	# 		groups = groups.split(',')
	# 		embed_message += f'{subject} - {", ".join(groups)}; '
	# 		role_element = f'#{subject}'
	# 		for group in groups:
	# 			role_element += f'_{group}'
	# 		roles_list.append(role_element)
	#
	# 	guild_roles = [guild_role.name for guild_role in ctx.guild.roles]
	# 	for role in roles_list:
	# 		if role not in guild_roles:
	# 			await ctx.guild.create_role(name=role, colour=0x11806A)
	# 		for guild_role in ctx.guild.roles:
	# 			if guild_role.name == role:
	# 				await member.add_roles(guild_role)
	# 			elif guild_role.name == config.unconfirmed_member_role_name:
	# 				await member.remove_roles(guild_role)
	#
	# 	embed = embeded('Profesor Adaugat', f'Membrul: {member}\nRoluri:\n{embed_message}', discord.Colour.green())

	@commands.command(aliases=['vememb'])
	@commands.has_role('Admin')
	async def verify_members(self, ctx, readed_category=None):
		await ctx.channel.purge(limit=1)
		timeout = 30
		event = None
		process = None
		inactivity_message = 'Procesul a fost oprit din cauza inactivității utilizatorului'
		user_cancel_message = 'Procesul a fost oprit de utilizator'

		labels = ['Continuati', 'Statistica']
		components = create_buttons(labels)
		embed = embeded('Verificarea membrilor', 'Pentru a începe, apăsați *Continuați*', discord.Colour.blurple())
		msg: discord.Message = await ctx.channel.send(embed=embed, components=components)

		def check(the_event_message):
			return the_event_message.author.id == ctx.message.author.id
		# Alegerea procesului necesar
		try:
			event = await self.client.wait_for('button_click', timeout=timeout, check=check)
		except main.asyncio.TimeoutError:
			embed = embeded('Verificarea membrilor', inactivity_message, discord.Colour.red())
			await msg.edit(embed=embed, components=[])
			await event.respond(type=6)
			return
		else:
			if event.component.label == 'Renunță':
				embed = embeded('Verificarea membrilor', user_cancel_message, discord.Colour.light_gray())
				await msg.edit(embed=embed, components=[])
				await event.respond(type=6)
				return
			else:
				if event.component.label == labels[0]:
					if readed_category is not None:
						if valid.is_valid_group_name(readed_category):
							process = 'process_members'
						else:
							embed = embeded('Verificarea membrilor', 'Numele categoriei nu este valid', discord.Colour.red())
							await msg.edit(embed=embed, components=[])
							return
					else:
						process = 'get_group'
				elif event.component.label == labels[1]:
					process = 'stats'
			await event.respond(type=6)

		# Vizualizarea datelor statistice
		if process == 'stats':
			embed = embeded('Statistica membrilor', 'Prelucrarea datelor . . .', discord.Colour.gold())
			await msg.edit(embed=embed, components=[])
			confirmed_members = 0
			unconfirmed_members = 0
			for role in ctx.guild.roles:
				if role.name == config.unconfirmed_member_role_name:
					unconfirmed_members = len(role.members)
			labels = ['Continua']
			components = create_buttons(labels)
			message = f'Din {len(ctx.guild.members)} de membri - {unconfirmed_members} neconfirmați'
			embed = embeded('Statistica membrilor', message, discord.Colour.gold())
			await msg.edit(embed=embed, components=components)

			try:
				event = await self.client.wait_for('button_click', timeout=timeout, check=check)
			except main.asyncio.TimeoutError:
				embed = embeded('Statistica membrilor', inactivity_message, discord.Colour.red())
				await msg.edit(embed=embed, components=[])
				await event.respond(type=6)
				return
			else:
				if event.component.label == 'Renunță':
					embed = embeded('Statistica membrilor', user_cancel_message, discord.Colour.light_gray())
					await msg.edit(embed=embed, components=[])
					await event.respond(type=6)
					return
				else:
					if event.component.label == labels[0]:
						process = 'get_group'
			await event.respond(type=6)

		# Introducerea categoriei de la tastatura
		if process == 'get_group' and readed_category is None:
			embed = embeded('Alegerea categoriei', 'Introduceți denumirea categoriei de la tastatură . . .', discord.Colour.purple())
			await msg.edit(embed=embed, components=[])
			try:
				event = await self.client.wait_for('message', timeout=timeout, check=check)
			except asyncio.TimeoutError:
				embed = embeded('Alegerea categoriei', inactivity_message, discord.Colour.red())
				await msg.edit(embed=embed, components=[])
				return
			else:
				readed_category = event.content
				await ctx.channel.purge(limit=1)

				labels = ['Continua']
				components = create_buttons(labels)
				embed = embeded('Alegerea categoriei', f'Categoria aleasă: ***{readed_category}***', discord.Colour.gold())
				await msg.edit(embed=embed, components=components)

				try:
					event = await self.client.wait_for('button_click', timeout=timeout, check=check)
				except asyncio.TimeoutError:
					embed = embeded('Alegerea categoriei', inactivity_message, discord.Colour.red())
					await msg.edit(embed=embed, components=[])
					await event.respond(type=6)
					return
				else:
					if event.component.label == 'Renunță':
						embed = embeded('Alegerea categoriei', user_cancel_message, discord.Colour.light_gray())
						await msg.edit(embed=embed, components=[])
						await event.respond(type=6)
						return
					else:
						if event.component.label == labels[0]:
							if valid.is_valid_group_name(readed_category):
								process = 'process_members'
							else:
								embed = embeded('Alegerea categoriei', 'Numele categoriei nu este valid', discord.Colour.red())
								await msg.edit(embed=embed, components=[])
								return

				await event.respond(type=6)

		# Processul de confirmare
		if process == 'process_members' and readed_category is not None:
			members_list = []
			for member in ctx.guild.members:
				roles = [x.name for x in member.roles]
				if valid.is_valid_group_name(readed_category):
					if config.student_role_name in roles:
						if config.unconfirmed_member_role_name in roles:
							speciality, year = readed_category.split('-')

							if speciality in roles and year in roles:
								members_list.append(member)

			# Sortarea membrilor
			members_list.sort(key=lambda x: x.display_name)

			embed = embeded('Procesarea membrilor', f'Lista:\n' + '\n'.join([x.display_name for x in members_list]), discord.Colour.gold())
			await msg.edit(embed=embed, components=[])

			labels = ['Confirmă', 'Pas', 'Declină']
			components = create_buttons(labels)
			for member in members_list:
				embed = embeded('Confirmarea membrilor', f'Categoria aleasă: ***{member.display_name}***', discord.Colour.gold())
				await msg.edit(embed=embed, components=components)

				try:
					event = await self.client.wait_for('button_click', timeout=timeout, check=check)
				except asyncio.TimeoutError:
					embed = embeded('Confirmarea membrilor', inactivity_message, discord.Colour.red())
					await msg.edit(embed=embed, components=[])
					await event.respond(type=6)
					return
				else:
					if event.component.label == 'Renunță':
						embed = embeded('Confirmarea membrilor', user_cancel_message, discord.Colour.light_gray())
						await msg.edit(embed=embed, components=[])
						await event.respond(type=6)
						return
					else:
						if event.component.label == labels[0]:
							for role in ctx.guild.roles:
								if role.name == config.unconfirmed_member_role_name:
									await member.remove_roles(role)
						elif event.component.label == labels[2]:
							message = 'Înregistrarea dumneavoastră a fost respinsă de Admin'
							embed = embeded('Ați fost dat afară din server', message, discord.Colour.red())
							await member.send(embed=embed, components=[])
							await ctx.guild.kick(member)
				await event.respond(type=6)

			embed = embeded('Confirmarea membrilor', 'Finalizat', discord.Colour.green())
			await msg.edit(embed=embed, components=[])

	@commands.command(aliases=['accept'])
	@commands.has_role(config.class_master_role_name)
	async def accept_members(self, ctx: discord.Message):
		if ctx.channel.name != config.commands_channel_name:
			return

		timeout = 29
		embed_titles = 'Confirmarea elevilor'
		embed_description = f'Salut {ctx.author.mention}. Mesajul va fi sters peste **{timeout + 1}** secunde de inactivitate.'

		btn_ok = Button(style=ButtonStyle.green, label='Confirma', id='ok', emoji='\N{Squared OK}')
		btn_accept = Button(style=ButtonStyle.green, label='Accepta', id='`acceptat` :white_check_mark:', emoji='\N{Heavy Check Mark}')
		btn_dismiss = Button(style=ButtonStyle.red, label='Refuza', id='`refuzat` :x:', emoji='\N{Heavy Multiplication X}')
		btn_pass = Button(style=ButtonStyle.blue, label='Pass', id='`pass` :fast_forward:', emoji='\N{Black Right-Pointing Double Triangle}')
		btn_cancel = Button(style=ButtonStyle.grey, label='Anuleaza', id='cancel', emoji='\N{No Entry}')
		components = [[btn_accept, btn_dismiss, btn_pass, btn_cancel]]

		embed = discord.Embed(title=embed_titles, description=embed_description, colour=discord.Colour.orange())
		the_bot_msg: discord.Message = await ctx.channel.send(embed=embed)

		def check(the_event_message):
			return the_event_message.author.id == ctx.message.author.id

		new_description = ''
		catedra, year = ctx.channel.category.name.split('-')
		new_confirmed_users = []
		users_kicked = []
		member: discord.Member
		for member in ctx.guild.members:
			role_names = [x.name for x in member.roles]
			if catedra in role_names and year in role_names and config.unconfirmed_member_role_name in role_names and config.student_role_name in role_names:
				new_description += f'\n**Numele**: `{member.nick}`.'
				embed = discord.Embed(title=embed_titles, description=embed_description + '\n' + new_description + ' **Optiunea**: `-----` :arrow_left:', colour=discord.Colour.orange())
				embed.set_footer(text='Alege o optiune de mai jos.')
				await the_bot_msg.edit(embed=embed, components=components)

				try:
					event: discord_components.Interaction = await self.client.wait_for('button_click', timeout=timeout, check=check)
					await event.respond(type=6)
				except main.asyncio.TimeoutError:
					embed = discord.Embed(title=embed_titles, description=f'Timpul acordat de **{timeout + 1}** secunde s-a scurs.', colour=discord.Colour.red())
					await the_bot_msg.edit(embed=embed, components=[])
					return
				else:
					if event.custom_id == btn_cancel.id:
						embed = discord.Embed(title=embed_titles, description=f'Confirmarea elevilor a fost anulata de catre {event.author.mention}', colour=discord.Colour.red())
						await the_bot_msg.edit(embed=embed, components=[])
						return
					elif event.custom_id == btn_dismiss.id:
						users_kicked.append(member)
					elif event.custom_id == btn_accept.id:
						new_confirmed_users.append(member)

					new_description += f' **Optiunea**: {event.custom_id}'

		if len(new_description) == 0:
			new_description = f'Salut {ctx.author.mention}. Nu sunt persoane necornfirmate.'
			embed = discord.Embed(title=embed_titles, description=new_description, colour=discord.Colour.green())
			await the_bot_msg.edit(embed=embed, components=[])
			return

		components = [[btn_ok, btn_cancel]]
		embed = discord.Embed(title=embed_titles, description=f'{embed_description}\n{new_description}', colour=discord.Colour.gold())
		embed.set_footer(text='Alege o optiune de mai jos.')
		await the_bot_msg.edit(embed=embed, components=components)

		try:
			event: discord_components.Interaction = await self.client.wait_for('button_click', timeout=timeout, check=check)
			await event.respond(type=6)
		except main.asyncio.TimeoutError:
			embed = discord.Embed(title=embed_titles, description=f'Timpul acordat de **{timeout + 1}** secunde s-a scurs.', colour=discord.Colour.red())
			await the_bot_msg.edit(embed=embed, components=[])
			return
		else:
			if event.custom_id == btn_cancel.id:
				embed = discord.Embed(title=embed_titles, description=f'Confirmarea elevilor a fost anulata de catre {event.author.mention}', colour=discord.Colour.red())
				await the_bot_msg.edit(embed=embed, components=[])
				return
			else:
				embed = discord.Embed(title=embed_titles, description=f'Salut {event.author.mention}. `Comanda se executa` :arrows_counterclockwise:' + '\n' + new_description, colour=discord.Colour.gold())
				await the_bot_msg.edit(embed=embed, components=[])

				for member in users_kicked:
					await member.send(f'Salut {member.mention}. Cererea dumneavoastra de inregistrare a fost refuzata. :cry: Aveti dreptul iarasi sa va inregistrati.')
					await member.kick(reason=f'Integistrarea membrului {member.nick} a fost respinsa de catre {event.author.mention} ({config.class_master_role_name}).')

				for member in new_confirmed_users:
					await confirm_member(ctx.channel.category, member)

		embed = discord.Embed(title=embed_titles, description=f'Salut {event.author.mention}. `Comanda a fost executata cu succes` :ballot_box_with_check:\n{new_description}', colour=discord.Colour.green())
		await the_bot_msg.edit(embed=embed, components=[])


def setup(client):
	client.add_cog(OnEventTrigger(client))
