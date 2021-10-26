import re  # RegEx
import discord
import asyncio
from discord.ext import commands
import main


# E74C3C - grupa
# 11806A - obiectul predat
# 607D8B - limba straina

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


def permission_overwrite(param):
	return discord.PermissionOverwrite(read_message_history=param, read_messages=param, send_messages=param, view_channel=param)


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
class ChannelRoles(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Asocierea rolurilor si canalelor
	@commands.command()
	@commands.has_role('Admin')
	async def update(self, ctx):
		await ctx.channel.purge(limit=1)
		# Pentru fiecare membru se verifica informatia
		count = 0
		scope = len(ctx.guild.members)
		embed = main.embeded(ctx, 'Actualizarea membrilor', f'Finailzat {count} din {scope} membri')
		msg = await ctx.channel.send(embed=embed)
		# Pentru fiecare membru din server
		for member in ctx.guild.members:
			roles = [role.name for role in member.roles]

			# Daca membrul nu are inca roluri
			if 'Membru Nou' or 'Membru' in roles:
				# Daca membrul este membru nou
				if 'Membru Nou' in roles:
					for role in member.roles:
						# Rolul care declara ca membrul este membru nou este inlaturat
						if role.name == 'Membru Nou':
							await member.remove_roles(role)
				# Daca membrul nu are rolul 'Membru'
				if 'Membru' not in roles:
					for role in ctx.guild.roles:
						# Adauga rol cu permisiuni extinse
						if role.name == 'Membru':
							await member.add_roles(role)

				# Pentru fiecare categorie se verifica daca utilizatorul este admis
				for category in ctx.message.guild.categories:
					# Daca categoria corespunde expresiei
					group_format = re.findall('^[A-Z][a-zA-Z]-[0-9]{4}[A-Z]?$', category.name)
					# Daca se gaseste denumirea categoriei in rolurile membrului
					if group_format != [] and category.name == group_format[0] and category.name in roles:
						# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
						for channel in category.channels:
							overwrite = permission_overwrite(True)
							# Daca membrul are rol de 'Elev'
							if 'Elev' in roles:
								# Actiune default
								if channel.name != 'limba-franceza' and channel.name != 'limba-engleza':
									await channel.set_permissions(member, overwrite=overwrite)
								# Daca membrul are rolul 'limba-engleza'
								elif channel.name == 'limba-engleza' and channel.name in roles:
									await channel.set_permissions(member, overwrite=overwrite)
								# Daca membrul are rolul 'limba-franceza'
								elif channel.name == 'limba-franceza' and channel.name in roles:
									await channel.set_permissions(member, overwrite=overwrite)
							# Daca membrul are rolul 'Profesor'
							elif 'Profesor' in roles:
								if channel.name in roles:
									await channel.set_permissions(member, overwrite=overwrite)
							elif 'Profesor?' in roles:
								pass
							else:
								await channel.set_permissions(member, overwrite=overwrite)
					# Daca categoria corespunde expresiei
					if group_format != [] and category.name == group_format[0]:
						# Daca membrul are rol de diriginte
						if f'Diriginte {group_format[0]}' in roles:
							# Pentru fiecare canal de categorie se permite accesul
							for channel in category.channels:
								# Dirigintele nu are permisiuni in canalul 'off-topic'
								if channel.name != 'off-topic':
									overwrite = permission_overwrite(True)
									await channel.set_permissions(member, overwrite=overwrite)
					# Daca membrul are rol de 'Admin'
					if group_format != [] and category.name == group_format[0] and 'Admin' in roles:
						for channel in category.channels:
							overwrite = permission_overwrite(True)
							await channel.set_permissions(member, overwrite=overwrite)
			count += 1
			embed = main.embeded(ctx, 'Actualizarea membrilor', f'Finailzat {count} din {scope} membri')
			await msg.edit(embed=embed)
		# Finalizat
		embed = main.embeded(ctx, 'Actualizarea membrilor', f'Finailzat')
		await msg.edit(embed=embed)

	# Restaureaza permisiunile mebrilor la una sau mai multe categorii
	@commands.command(aliases=['uc'])
	@commands.has_role('Admin')
	async def unload_category(self, ctx, unload_category=None):
		await ctx.channel.purge(limit=1)
		if unload_category is not None:
			message = f'Restaurare categoria {unload_category}'
		else:
			message = f'Restaurarea categoriilor'
		# Pentru fiecare membru se verifica informatia
		count = 0
		scope = len(ctx.guild.categories)
		embed = main.embeded(ctx, message, f'Finailzat {count} din {scope} categorii')
		msg = await ctx.channel.send(embed=embed)
		# Pentru fiecare membru din server
		for member in ctx.guild.members:
			roles = [role.name for role in member.roles]
			# Daca membrul are rol de 'Admin' permisiunile se pastreaza
			if 'Admin' in roles:
				count += 1
				continue
			# Pentru fiecare categorie se verifica daca utilizatorul este admis
			for category in ctx.guild.categories:
				# Daca se gaseste denumirea categoriei in rolurile membrului
				# Daca categoria corespunde expresiei
				group_format = re.findall('^[A-Z][a-zA-Z]-[0-9]{4}[A-Z]?$', category.name)
				if group_format != [] and category.name == group_format[0]:
					overwrite = permission_overwrite(None)
					# Daca utilizatorul a introdus denumirea categoriei
					if unload_category is not None and unload_category == category.name:
						# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
						for channel in category.channels:
							await channel.set_permissions(member, overwrite=overwrite)
						break
					# Daca utilizatorul nu a introdus nimic
					elif unload_category is None:
						for channel in category.channels:
							await channel.set_permissions(member, overwrite=overwrite)
			count += 1
			embed = main.embeded(ctx, message, f'Finailzat {count} din {scope} categorii')
			await msg.edit(embed=embed)
		# Finalizat
		embed = main.embeded(ctx, message, f'Finailzat')
		await msg.edit(embed=embed)

	# Restaureaza permisiunile membrului la toate categoriile
	@commands.command(aliases=['um'])
	@commands.has_role('Admin')
	async def unload_member(self, ctx, unload_member: discord.Member = None):
		await ctx.channel.purge(limit=1)
		# Daca membrul are rol de 'Admin' permisiunile se pastreaza
		roles = [role.name for role in unload_member.roles]
		if 'Admin' in roles:
			embed = main.embeded(ctx, ':x:Error', 'Membrii cu rol de @Admin nu pot fi lipsiti de permisiuni', discord.Colour.red())
			msg = await ctx.channel.send(embed=embed)
			return
		if unload_member is not None:
			message = f'Restaurare membrului {unload_member}'
			# Pentru fiecare membru se verifica ingroup_formatia
			count = 0
			scope = len(ctx.guild.categories)
			embed = main.embeded(ctx, message, f'Finailzat {count} din {scope} membri')
			msg = await ctx.channel.send(embed=embed)
			# Pentru fiecare categorie din server
			for category in ctx.guild.categories:
				# Daca se gaseste denumirea categoriei in rolurile membrului
				# Daca categoria corespunde expresiei
				group_format = re.findall('^[A-Z][a-zA-Z]-[0-9]{4}[A-Z]?$', category.name)
				if group_format != [] and category.name == group_format[0]:
					overwrite = permission_overwrite(None)
					# Daca utilizatorul a introdus membrul
					if unload_member is not None:
						# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
						for channel in category.channels:
							await channel.set_permissions(unload_member, overwrite=overwrite)
				count += 1
				embed = main.embeded(ctx, message, f'Finailzat {count} din {scope} categorii')
				await msg.edit(embed=embed)
			# Finalizat
			embed = main.embeded(ctx, message, f'Finailzat')
			await msg.edit(embed=embed)
		else:
			embed = main.embeded(ctx, ':x:Error', 'Este necesara mentionarea membrului', discord.Colour.red())
			msg = await ctx.channel.send(embed=embed)


def setup(client):
	client.add_cog(ChannelRoles(client))

# https://discordpy.readthedocs.io/en/stable/api.html#categorychannel
# https://discord.com/developers/docs/topics/permissions#permission-overwrites
