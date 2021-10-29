import discord
import asyncio
from discord.ext import commands
import main


# E74C3C - grupa
# 11806A - obiectul predat
# 607D8B - limba straina
def create_embed(ctx: discord.Message, title: str, description: str, colour: hex=discord.Colour.blue()) -> discord.Embed:
	embed = discord.Embed(
		title=title,
		description=description,
		colour=colour
	)
	embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
	return embed


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


def create_buttons(labels):
	btn_list = [[], [main.Button(style=main.ButtonStyle.red, label="Renunta")]]
	row = 0
	for label in labels:
		if len(btn_list[row]) >= 5:
			row += 1
			btn_list.insert(row, [])
		btn_list[row].append(main.Button(style=main.ButtonStyle.blue, label=label))
	return btn_list


async def sync_channels(ctx: discord.Message, msg):
	unwanted_categories = ['Public', 'General', 'Developer']
	unwanted_channels = ['public', 'dezvoltarea-personala']
	sync_result = {}
	embed = create_embed(ctx, 'Sincronizarea canalelor', 'Initializarea sincronizarii', discord.Colour.orange())
	await msg.edit(embed=embed)
	count = 0
	for category in ctx.guild.categories:
		for channel in category.channels:
			await channel.edit(sync_permissions=True)
			# Daca canalul este pentru elevi si profesori
			if category.name not in unwanted_categories and channel.name not in unwanted_channels:
				if channel.name in sync_result.keys():
					sync_result[channel.name].append([category.name, channel.id])
				else:
					sync_result[channel.name] = [[category.name, channel.id]]

		count += 1
		embed = create_embed(ctx, 'Sincronizarea canalelor', f'Finailzat {count} din {len(ctx.guild.categories)} categorii', discord.Colour.orange())
		await msg.edit(embed=embed)
	# Finalizat
	embed = create_embed(ctx, 'Sincronizarea canalelor', f'Finailzat', discord.Colour.orange())
	await msg.edit(embed=embed)
	return sync_result


async def adaugarea_elevilor(ctx: discord.Message, msg):
	embed = create_embed(ctx, 'Adaugarea membrilor', 'Initializarea procesului', discord.Colour.gold())
	await msg.edit(embed=embed)
	count = 0
	for member in ctx.guild.members:
		count += 1
		roles = [role.name for role in member.roles]
		if ('Elev' or 'Admin' or 'Diriginte') in roles:
			for category in ctx.guild.categories:
				if is_valid_group_name(category.name):
					speciality, year = category.name.split('-')
					if (speciality in roles and year in roles) or 'Admin' in roles:
						await category.set_permissions(member, view_channel=True)

		embed = create_embed(ctx, 'Adaugarea membrilor', f'Finailzat {count} din {len(ctx.guild.members)} membri', discord.Colour.gold())
		await msg.edit(embed=embed)

	embed = create_embed(ctx, 'Adaugarea membrilor', f'Finailzat', discord.Colour.gold())
	await msg.edit(embed=embed)


async def set_language_groups_and_teachers(ctx: discord.Message, msg, sync_results) -> None:
	embed = create_embed(ctx, 'Actualizarea permisiunilor', 'Initializarea processync_resultsului', discord.Colour.dark_green())
	await msg.edit(embed=embed)
	count = 0
	for member in ctx.guild.members:
		count += 1
		roles = [role.name for role in member.roles]

		if 'Elev' in roles:
			for category in ctx.guild.categories:
				if is_valid_group_name(category.name):
					speciality, year = category.name.split('-')
					if speciality in roles and year in roles:
						for channel in category.channels:
							if channel.name == 'limba-engleza' and channel.name not in roles:
								await channel.set_permissions(member, view_channel=None)
							elif channel.name == 'limba-franceza' and channel.name not in roles:
								await channel.set_permissions(member, view_channel=None)
		elif 'Profesor' in roles:
			for role in member.roles:
				if role.name.startswith('#'):
					splited_discipline = role.name.split('_')
					group_name = splited_discipline[0][1:]
					# Daca numele primului element din lista coincide cu categoria
					for category in ctx.guild.categories:
						if category.name in splited_discipline:
							# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
							channels_id = sync_results[group_name[1:]]
							for element in channels_id:
								if element[0] == category.name:
									intercepted_channel = ctx.guild.get_channel(element[1])
									intercepted_channel.set_permissions(member, view_channel=True)

							voce_id = sync_results['voce']
							for element in voce_id:
								if element[0] == category.name:
									intercepted_channel = ctx.guild.get_channel(element[1])
									intercepted_channel.set_permissions(member, view_channel=True)

		# if ('Elev' or 'Profesor') in roles:
		# 	for category in ctx.guild.categories:
		# 		if is_valid_group_name(category.name):
		# 			if 'Elev' in roles:
		# 				speciality, year = category.name.split('-')
		# 				if speciality in roles and year in roles:
		# 					for channel in category.channels:
		# 						if channel.name == 'limba-engleza' and channel.name not in roles:
		# 							await channel.set_permissions(member, view_channel=None)
		# 						elif channel.name == 'limba-franceza' and channel.name not in roles:
		# 							await channel.set_permissions(member, view_channel=None)
		# 			elif 'Profesor' in roles:
		# 				for role in member.roles:
		# 					if role.name.startswith('#'):
		# 						splited_discipline = role.name.split('_')
		# 						group_name = splited_discipline[0]
		# 						# Daca numele primului element din lista coincide cu categoria
		# 						if category.name in splited_discipline:
		# 							# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
		# 							channels_id = sync_results[group_name[1:]]
		# 							for element in channels_id:
		# 								if element[0] == category.name:
		# 									intercepted_channel = ctx.guild.get_channel(element[1])
		# 									intercepted_channel.set_permissions(member, view_channel=True)
		#
		# 							voce_id = sync_results['voce']
		# 							for element in voce_id:
		# 								if element[0] == category.name:
		# 									intercepted_channel = ctx.guild.get_channel(element[1])
		# 									intercepted_channel.set_permissions(member, view_channel=True)

		embed = create_embed(ctx, 'Actualizarea permisiunilor', f'Finailzat {count} din {len(ctx.guild.members)} membri', discord.Colour.dark_green())
		await msg.edit(embed=embed)

	embed = create_embed(ctx, 'Actualizarea permisiunilor', f'Finailzat', discord.Colour.dark_green())
	await msg.edit(embed=embed)


# Initierea clasului
class ChannelRoles(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Asocierea rolurilor si canalelor
	@commands.command()
	@commands.has_role('Admin')
	async def update(self, ctx, only_member: discord.Member = None):
		await ctx.channel.purge(limit=1)

		# Daca sunt date de intrare
		if only_member is None:
			guild_members = ctx.guild.members
		else:
			guild_members = [only_member]

		# Pentru fiecare membru se verifica informatia
		count = 0
		scope = len(guild_members)
		embed = create_embed(ctx, 'Actualizarea membrilor', f'Finailzat {count} din {scope} membri')
		msg = await ctx.channel.send(embed=embed)

		# Pentru fiecare membru din server
		for member in guild_members:
			roles = [role.name for role in member.roles]

			# Daca membrul nu este bot sau Administrator Discord
			if 'Dev' not in roles and 'Bots' not in roles:
				# Daca membrul nu are inca roluri
				if 'Membru Nou' or 'Membru' in roles:
					# Daca membrul este membru nou
					if 'Membru Nou' in roles:
						for role in member.roles:
							# Rolul care declara ca membrul este membru nou este inlaturat
							if role.name == 'Membru Nou':
								await member.remove_roles(role)
							# Adauga rol cu permisiuni extinse
							if role.name == 'Membru':
								await member.add_roles(role)

					# Pentru fiecare categorie se verifica daca utilizatorul este admis
					for category in ctx.guild.categories:
						# Daca se gaseste denumirea categoriei in rolurile membrului
						if is_valid_group_name(category.name):
							# Daca membrul are rol de 'Elev'
							if 'Elev' in roles or ('Elev' in roles and category.name in roles):
								speciality, year = category.name.split('-')
								if (speciality in roles and year in roles) or category.name in roles:
									await category.set_permissions(member, view_channel=True)
									# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
									for channel in category.channels:
										# # Actiune default
										# if channel.name != 'limba-franceza' and channel.name != 'limba-engleza':
										# 	await channel.set_permissions(member, overwrite=overwrite)
										# Daca membrul are rolul 'limba-engleza'
										if channel.name == 'limba-engleza' and channel.name not in roles:
											await channel.set_permissions(member, view_channel=True)
										# Daca membrul are rolul 'limba-franceza'
										elif channel.name == 'limba-franceza' and channel.name not in roles:
											await channel.set_permissions(member, view_channel=True)

							# Daca membrul are rolul 'Profesor'
							elif 'Profesor' in roles:
								# Pentru fiecare rol din rolurile membrului
								for role in member.roles:
									# Daca rolul se incepe cu diez #
									if role.name.startswith('#'):
										splited_discipline = role.name.split('_')
										group_name = splited_discipline[0]
										# Daca numele primului element din lista coincide cu categoria
										if category.name in splited_discipline:
											# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
											for channel in category.channels:
												# Daca numele canalului este in lista
												if group_name[1:] == channel.name or channel.name == 'voce':
													await channel.set_permissions(member, view_channel=True)
							elif 'Profesor?' in roles:
								pass
							# Daca membrul are rol de diriginte
							elif f'Diriginte' in roles:
								speciality, year = category.name.split('-')
								if (speciality in roles and year in roles) or category.name in roles:
									await category.set_permissions(member, view_channel=True)
									# Pentru fiecare canal de categorie se permite accesul
									for channel in category.channels:
										# Dirigintele nu are permisiuni in canalul 'off-topic'
										if channel.name == 'off-topic':
											await channel.set_permissions(member, view_channel=None)
							# Daca membrul are rol de 'Admin'
							elif 'Admin' in roles:
								for channel in category.channels:
									await channel.set_permissions(member, view_channel=True)
			count += 1
			embed = create_embed(ctx, 'Actualizarea membrilor', f'Finailzat {count} din {scope} membri')
			await msg.edit(embed=embed)
		# Finalizat
		embed = create_embed(ctx, 'Actualizarea membrilor', f'Finailzat')
		await msg.edit(embed=embed)

	# Restaureaza permisiunile mebrilor la una sau mai multe categorii
	@commands.command(aliases=['uc'])
	@commands.has_role('Admin')
	async def unload_category(self, ctx, unload_category=None):
		await ctx.channel.purge(limit=1)

		# Daca a fost introdusa denumirea unei categorii de utilizator
		if unload_category is not None:
			message = f'Restaurare categoria {unload_category}'
			if is_valid_group_name(unload_category):
				for category in ctx.guild.categories:
					if category.name == unload_category:
						unload_category = [unload_category]
		else:
			message = f'Restaurarea categoriilor'
			unload_category = ctx.guild.categories
		# Pentru fiecare membru se verifica informatia
		count = 0
		scope = len(unload_category)
		embed = create_embed(ctx, message, f'Finailzat {count} din {scope} categorii')
		msg = await ctx.channel.send(embed=embed)
		for category in unload_category:
			if is_valid_group_name(category.name):
				for member in ctx.guild.members:
					roles = [role.name for role in member.roles]
					if 'Admin' in roles:
						pass
					else:
						await category.set_permissions(member, view_channel=None)
				for channel in category.channels:
					await channel.edit(sync_permissions=True)

			count += 1
			embed = create_embed(ctx, message, f'Finailzat {count} din {scope} membri')
			await msg.edit(embed=embed)
		# Finalizat
		embed = create_embed(ctx, message, f'Finailzat')
		await msg.edit(embed=embed)

	# Restaureaza permisiunile membrului la toate categoriile
	@commands.command(aliases=['um'])
	@commands.has_role('Admin')
	async def unload_member(self, ctx, unload_member: discord.Member = None):
		await ctx.channel.purge(limit=1)
		# Daca membrul are rol de 'Admin' permisiunile se pastreaza
		roles = [role.name for role in unload_member.roles]
		if 'Admin' in roles:
			embed = create_embed(ctx, ':x:Error', 'Membrii cu rol de @Admin nu pot fi lipsiti de permisiuni', discord.Colour.red())
			msg = await ctx.channel.send(embed=embed)
			return
		if unload_member is not None:
			message = f'Restaurare membrului {unload_member}'
			# Pentru fiecare membru se verifica ingroup_formatia
			count = 0
			scope = len(ctx.guild.categories)
			embed = create_embed(ctx, message, f'Finailzat {count} din {scope} membri')
			msg = await ctx.channel.send(embed=embed)
			# Pentru fiecare categorie din server
			for category in ctx.guild.categories:
				# Daca numele categoriei este nume de grup
				if is_valid_group_name(category.name):
					await category.set_permissions(unload_member, view_channel=None)
					# # Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
					# for channel in category.channels:
					# 	await channel.set_permissions(unload_member, overwrite=overwrite)
				count += 1
				embed = create_embed(ctx, message, f'Finailzat {count} din {scope} categorii')
				await msg.edit(embed=embed)
			# Finalizat
			embed = create_embed(ctx, message, f'Finailzat')
			await msg.edit(embed=embed)
		else:
			embed = create_embed(ctx, ':x:Error', 'Este necesara mentionarea membrului', discord.Colour.red())
			msg = await ctx.channel.send(embed=embed)

	# Asocierea rolurilor si canalelor
	@commands.command(aliases=['globup'])
	@commands.has_role('Admin')
	async def global_update(self, ctx):
		await ctx.channel.purge(limit=1)
		embed = create_embed(ctx, 'Procesul de actualizare', 'Initializare', discord.Colour.purple())
		msg = await ctx.channel.send(embed=embed)
		sync_result = await sync_channels(ctx, msg)
		await adaugarea_elevilor(ctx, msg)
		await set_language_groups_and_teachers(ctx, msg, sync_result)


def setup(client):
	client.add_cog(ChannelRoles(client))
