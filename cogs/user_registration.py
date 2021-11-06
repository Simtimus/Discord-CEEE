import discord
import main
import config
import asyncio
from discord.ext import commands

# Primary    |  1  |  blurple
# Secondary  |  2  |  grey
# Success    |  3  |  green
# Danger     |  4  |  red
# Link       |  5  |  grey, navigates to a URL


def is_valid_name(name: str) -> bool:
	split_name = name.split(' ')
	if len(split_name) != 2 and len(split_name) != 3:
		return False

	for word in split_name:
		for char in word:
			if not 64 < ord(char) < 91 and not 94 < ord(char) < 123:
				return False

	return True


def is_valid_group_name(name: str) -> bool:
	split_group_name = name.split('-')
	if len(split_group_name) != 2:
		return False

	if not 64 < ord(split_group_name[0][0]) < 91:  # Daca primul simbol nu este litera mare.
		return False

	if not 64 < ord(split_group_name[0][1]) < 91 and not 94 < ord(split_group_name[0][1]) < 123:  # Daca al doilea simbol nu este litara.
		return False

	if len(split_group_name[1]) != 4 and len(split_group_name[1]) != 5:
		return False

	if not str(split_group_name[1][0:3]).isdigit():  # Daca primele 4 numere nu este o cifra.
		return False

	if len(split_group_name[1]) == 5 and not 64 < ord(split_group_name[1][-1]) < 91:  # Daca litera de la urma este mare (daca exista)
		return False

	return True


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


def create_buttons(labels, btn_style: main.ButtonStyle = 1):
	btn_list = [[], [main.Button(style=4, label="Renunta")]]
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
				embed = embeded('Notificare', 'Au fost adaugate roluri noi de elev.\nEste necesar de repozitionat rolurile', discord.Colour.green())
				await member.guild.get_channel(904096410532724756).send(embed=embed)


# Initierea clasului
class OnEventTrigger(commands.Cog):
	def __init__(self, client):
		self.client = client

	# When member joins the guild
	@commands.Cog.listener()
	async def on_member_join(self, member: discord.Member):
		timeout = 120
		join_link = 'https://discord.gg/7bPVtAWUxu'

		message = f'Introduceti **`Numele Prenumele`** dumneavoastra'
		embed = embeded('Inregistrare in CEEE', message, discord.Colour.green())
		msg: discord.Message = await member.send(embed=embed)

		new_member_embed = embeded('Membru nou', f'Se asteapta raspuns de la *{member}*', discord.Colour.gold())
		new_member = await member.guild.get_channel(904096410532724756).send(embed=new_member_embed)

		def check(the_event_message):
			return the_event_message.author.id == member.id

		try:
			event = await self.client.wait_for('message', timeout=timeout, check=check)
		except asyncio.TimeoutError:
			message = f'Timpul acordat pentru inregistrare s-a scurs. Pentru a va putea inregistra, accesati linkul de mai jos.\n{join_link}'
			embed = embeded('Inregistrare respinsa', message, discord.Colour.red())
			await msg.edit(embed=embed, components=[])
			await member.guild.kick(member)
			new_member_embed = embeded('Membru nou', f'*{member}* - a fost dat afara\nMotivul: *inactivitate*', discord.Colour.red())
			await new_member.edit(embed=new_member_embed)
		else:
			# Definirea variabilelor
			name = event.content
			statut = None
			roles = [x for x in member.guild.categories if is_valid_group_name(x.name)]
			groups = get_disctionary_of_roles(roles)
			timeout = 30
			exit_message = ''
			language = ''
			year = ''
			group = ''

			# Verificarea parametrului name la simboluri
			if not is_valid_name(name):
				message = f'Numele introdus nu contine doar simboluri din alfabetul latin sau nu este compus din cel putin Nume Prenume.'
				message += f'\nPentru a va putea inregistra, accesati linkul de mai jos.\n{join_link}'
				embed = embeded('Inregistrare respinsa', message, discord.Colour.red())
				await member.send(embed=embed, components=[])
				await member.guild.kick(member)
				new_member_embed = embeded('Membru nou', f'*{member}* - a fost dat afara\nMotivul: *nume incorect*', discord.Colour.red())
				await new_member.edit(embed=new_member_embed)
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
				if event.component.label == config.student_role_name or event.component.label == config.teacher_role_name:
					statut = event.component.label
				elif event.component.label == 'Renunta':
					statut = 'exit'
					exit_message = 'Procesul a fost oprit de utilizator'
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

					# Phase 1 - Alegerea anului
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
						languages = create_buttons([config.english_channel_name, config.francais_channel_name])
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
							elif event.component.label == config.english_channel_name or event.component.label == config.francais_channel_name:
								language = event.component.label
								message += f'\n**Limba straina:** `{language}`'
								embed = embeded('Asteptare', message, discord.Colour.green())
								await msg.edit(embed=embed, components=[])
						await event.respond(type=6)
						phase += 1
			# Adaugarea rolurilor pentru Profesori
			elif statut == config.teacher_role_name:
				# Returnarea mesajului finisat
				message += f'\n**Statutul:** `{statut}`'

			# Iesirea din commanda
			if statut == 'exit':
				message = f'Pentru a va putea inregistra, accesati linkul de mai jos.\n{join_link}'
				embed = embeded('Inregistrare respinsa', f'{exit_message}\n{message}', discord.Colour.red())
				await msg.edit(embed=embed, components=[])
				await member.guild.kick(member)
				new_member_embed = embeded('Membru nou', f'*{member}* - a fost dat afara\nMotivul: *membrul a renuntat*', discord.Colour.red())
				await new_member.edit(embed=new_member_embed)
				return

			await do_required_roles_exist(member, [group, year])

			# Adaugarea rolurilor si a nickname-ului
			await member.edit(nick=name)
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
					if role.name == config.unconfirmed_teacher_role_name:
						await member.add_roles(role)
				# Membru nou
				if role.name == config.confirmed_member_name:
					await member.remove_roles(role)
				elif role.name == config.unconfirmed_member_name:
					await member.add_roles(role)
			# Mesaj ca totul sa executat cu success
			embed = embeded('Inregistrare finisata', message, discord.Colour.green())
			await msg.edit(embed=embed, components=[])
			new_member_embed = embeded('Membru nou', f'*{member}* - a finisat inregistrarea\nDisplayName: *{name}*', discord.Colour.red())
			await new_member.edit(embed=new_member_embed)

	@commands.command(aliases=['addsub'])
	async def add_school_subjects_to_the_teacher(self, ctx: discord.ext.commands.Context, member: discord.Member, arguments):
		await ctx.channel.purge(limit=1)

		if type(member) is not discord.Member:
			embed = embeded('Adaugare profesor', f'Nu a fost introdus un membru.', discord.Colour.red())
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

		embed = embeded('Profesor Adaugat', f'Membrul: {member}\nRoluri:\n{embed_message}', discord.Colour.green())
		await ctx.channel.send(embed=embed)

	@commands.command(aliases=['vememb'])
	async def verify_members(self, ctx, readed_category=None):
		await ctx.channel.purge(limit=1)
		timeout = 30
		event = None
		process = None
		inactivity_message = 'Procesul a fost oprit din cauza inactivitatii utilizatorului'
		user_cancel_message = 'Procesul a fost oprit de utilizator'

		labels = ['Continuati', 'Statistica']
		components = create_buttons(labels)
		embed = embeded('Verificarea membrilor', 'Pentru a incepe, apasati *Continuati*', discord.Colour.blurple())
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
			if event.component.label == 'Renunta':
				embed = embeded('Verificarea membrilor', user_cancel_message, discord.Colour.light_gray())
				await msg.edit(embed=embed, components=[])
				await event.respond(type=6)
				return
			else:
				if event.component.label == labels[0]:
					if readed_category is not None:
						if is_valid_group_name(readed_category):
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
				if role.name == config.confirmed_member_name:
					confirmed_members = len(role.members)
				elif role.name == config.unconfirmed_member_name:
					unconfirmed_members = len(role.members)
			labels = ['Continua']
			components = create_buttons(labels)
			message = f'Din {len(ctx.guild.members)}:\n{confirmed_members} - confirmati\n{unconfirmed_members} - neconfirmati'
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
				if event.component.label == 'Renunta':
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
			embed = embeded('Alegerea categorieie', 'Introduceti denumirea categoriei de la tastatura . . .', discord.Colour.purple())
			await msg.edit(embed=embed, components=[])
			try:
				event = await self.client.wait_for('message', timeout=timeout, check=check)
			except asyncio.TimeoutError:
				embed = embeded('Alegerea categorieie', inactivity_message, discord.Colour.red())
				await msg.edit(embed=embed, components=[])
				return
			else:
				readed_category = event.content
				await ctx.channel.purge(limit=1)

				labels = ['Continua']
				components = create_buttons(labels)
				embed = embeded('Alegerea categorieie', f'Categoria aleasa: ***{readed_category}***', discord.Colour.gold())
				await msg.edit(embed=embed, components=components)

				try:
					event = await self.client.wait_for('button_click', timeout=timeout, check=check)
				except asyncio.TimeoutError:
					embed = embeded('Alegerea categorieie', inactivity_message, discord.Colour.red())
					await msg.edit(embed=embed, components=[])
					await event.respond(type=6)
					return
				else:
					if event.component.label == 'Renunta':
						embed = embeded('Alegerea categorieie', user_cancel_message, discord.Colour.light_gray())
						await msg.edit(embed=embed, components=[])
						await event.respond(type=6)
						return
					else:
						if event.component.label == labels[0]:
							if is_valid_group_name(readed_category):
								process = 'process_members'
							else:
								embed = embeded('Alegerea categorieie', 'Numele categoriei nu este valid', discord.Colour.red())
								await msg.edit(embed=embed, components=[])
								return

				await event.respond(type=6)

		# Processul de confirmare
		if process == 'process_members' and readed_category is not None:
			members_list = []
			for member in ctx.guild.members:
				roles = [x.name for x in member.roles]
				if is_valid_group_name(readed_category):
					if config.student_role_name in roles:
						if config.confirmed_member_name not in roles:
							speciality, year = readed_category.split('-')

							if speciality in roles and year in roles:
								members_list.append(member)

			# Sortarea membrilor
			members_list.sort(key=lambda x: x.display_name)

			embed = embeded('Procesarea membrilor', f'Lista:\n' + '\n'.join([x.display_name for x in members_list]), discord.Colour.gold())
			await msg.edit(embed=embed, components=[])

			labels = ['Confirma', 'Pas', 'Declina']
			components = create_buttons(labels)
			for member in members_list:
				embed = embeded('Confirmarea membrilor', f'Categoria aleasa: ***{member.display_name}***', discord.Colour.gold())
				await msg.edit(embed=embed, components=components)

				try:
					event = await self.client.wait_for('button_click', timeout=timeout, check=check)
				except asyncio.TimeoutError:
					embed = embeded('Confirmarea membrilor', inactivity_message, discord.Colour.red())
					await msg.edit(embed=embed, components=[])
					await event.respond(type=6)
					return
				else:
					if event.component.label == 'Renunta':
						embed = embeded('Confirmarea membrilor', user_cancel_message, discord.Colour.light_gray())
						await msg.edit(embed=embed, components=[])
						await event.respond(type=6)
						return
					else:
						if event.component.label == labels[0]:
							for role in ctx.guild.roles:
								if role.name == config.confirmed_member_name:
									await member.add_roles(role)
								elif role.name == config.unconfirmed_member_name:
									await member.remove_roles(role)
						elif event.component.label == labels[2]:
							embed = embeded('Ati fost dat afara din server', 'Pentru a va inregistra, accesati linkul care a fost trimis anterior', discord.Colour.red())
							await member.send(embed=embed, components=[])
							await ctx.guild.kick(member)
				await event.respond(type=6)

			embed = embeded('Confirmarea membrilor', 'Finalizat', discord.Colour.green())
			await msg.edit(embed=embed, components=[])


def setup(client):
	client.add_cog(OnEventTrigger(client))
