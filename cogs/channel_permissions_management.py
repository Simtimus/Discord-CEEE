import discord
import asyncio
from discord.ext import commands
import main
import config
import validator as valid


def create_embed(ctx: discord.Message, title: str, description: str, colour: hex = discord.Colour.blue()) -> discord.Embed:
	embed = discord.Embed(
		title=title,
		description=description,
		colour=colour
	)
	embed.set_footer(text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}")
	return embed


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
	sync_result = {}
	embed = create_embed(ctx, 'Sincronizarea canalelor', 'In desfasurare...', discord.Colour.orange())
	await msg.edit(embed=embed)
	for category in ctx.guild.categories:
		if valid.is_valid_group_name(category.name):
			for channel in category.channels:
				await channel.edit(sync_permissions=True)
				if channel.name in sync_result.keys():
					sync_result[channel.name].append([category.name, channel])
				else:
					sync_result[channel.name] = [[category.name, channel]]
	embed = create_embed(ctx, 'Sincronizarea canalelor', f'Finailzat', discord.Colour.orange())
	await msg.edit(embed=embed)
	return sync_result


async def adaugarea_elevilor(ctx: discord.Message, msg):
	embed = create_embed(ctx, 'Adaugarea membrilor', 'In desfasurare...', discord.Colour.gold())
	await msg.edit(embed=embed)
	for member in ctx.guild.members:
		roles = [role.name for role in member.roles]
		if config.unconfirmed_member_role_name not in roles:
			if config.student_role_name in roles or config.class_master_role_name in roles:
				for category in ctx.guild.categories:
					if valid.is_valid_group_name(category.name):
						speciality, year = category.name.split('-')
						if (speciality in roles and year in roles) or config.admin_role_name in roles:
							await category.set_permissions(member, view_channel=True)
	embed = create_embed(ctx, 'Adaugarea membrilor', f'Finailzat', discord.Colour.gold())
	await msg.edit(embed=embed)


async def set_language_groups_and_teachers(ctx: discord.Message, msg, sync_result) -> None:
	embed = create_embed(ctx, 'Actualizarea permisiunilor', 'In desfasurare...', discord.Colour.dark_green())
	await msg.edit(embed=embed)
	for member in ctx.guild.members:
		roles = [role.name for role in member.roles]

		if config.unconfirmed_member_role_name not in roles:
			if config.student_role_name in roles:
				for category in ctx.guild.categories:
					if valid.is_valid_group_name(category.name):
						speciality, year = category.name.split('-')
						if speciality in roles and year in roles:
							for channel in category.channels:
								if channel.name == config.english_channel_name and channel.name not in roles:
									await channel.set_permissions(member, view_channel=None)
								elif channel.name == config.francais_channel_name and channel.name not in roles:
									await channel.set_permissions(member, view_channel=None)
			elif config.teacher_role_name in roles:
				for role in member.roles:
					if role.name.startswith('#'):
						splited_discipline = role.name.split('_')
						group_name = splited_discipline[0][1:]
						# Daca numele primului element din lista coincide cu categoria
						for category in ctx.guild.categories:
							if category.name in splited_discipline:
								# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
								channels = sync_result[group_name]
								for element in channels:
									if element[0] == category.name:
										await element[1].set_permissions(member, view_channel=True)

								voice_channel = sync_result[config.voice_channel_name]
								for element in voice_channel:
									if element[0] == category.name:
										await element[1].set_permissions(member, view_channel=True)
	embed = create_embed(ctx, 'Actualizarea permisiunilor', f'Finailzat', discord.Colour.green())
	await msg.edit(embed=embed)


# Initierea clasului
class ChannelRoles(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Restaureaza permisiunile mebrilor la una sau mai multe categorii
	@commands.command(aliases=['uc'])
	@commands.has_role('Admin')
	async def unload_category(self, ctx, unload_category=None):
		await ctx.channel.purge(limit=1)

		# Daca a fost introdusa denumirea unei categorii de utilizator
		if unload_category is not None:
			message = f'Restaurare categoriei {unload_category}'
			if valid.is_valid_group_name(unload_category):
				for category in ctx.guild.categories:
					if category.name == unload_category:
						unload_category = [category]
		else:
			message = f'Restaurarea categoriilor'
			unload_category = ctx.guild.categories

		embed = create_embed(ctx, message, 'In desfasurare...')
		msg = await ctx.channel.send(embed=embed)
		# Pentru fiecare membru se verifica informatia
		for category in unload_category:
			if valid.is_valid_group_name(category.name):
				for member in ctx.guild.members:
					roles = [role.name for role in member.roles]
					if config.admin_role_name in roles:
						pass
					else:
						await category.set_permissions(member, view_channel=None)
				for channel in category.channels:
					await channel.edit(sync_permissions=True)
		# Finalizat
		embed = create_embed(ctx, message, f'Finailzat', discord.Colour.green())
		await msg.edit(embed=embed)

	# Asocierea rolurilor si canalelor
	@commands.command(aliases=['smartup'])
	@commands.has_role('Admin')
	async def smart_update(self, ctx, category_name):
		await ctx.channel.purge(limit=1)
		embed = create_embed(ctx, 'Procesul de actualizare', 'Initializare', discord.Colour.purple())
		msg = await ctx.channel.send(embed=embed)

		# Sincronizarea categoriei
		sync_result = {}
		embed = create_embed(ctx, 'Sincronizarea canalelor', 'In desfasurare...', discord.Colour.orange())
		await msg.edit(embed=embed)
		for category in ctx.guild.categories:
			if category_name == category.name:
				if valid.is_valid_group_name(category.name):
					for channel in category.channels:
						await channel.edit(sync_permissions=True)
						if channel.name in sync_result.keys():
							sync_result[channel.name].append([category.name, channel])
						else:
							sync_result[channel.name] = [[category.name, channel]]
		embed = create_embed(ctx, 'Sincronizarea canalelor', f'Finailzat', discord.Colour.orange())
		await msg.edit(embed=embed)

		# Adaugarea elevilor
		embed = create_embed(ctx, 'Adaugarea membrilor', 'In desfasurare...', discord.Colour.gold())
		await msg.edit(embed=embed)
		for member in ctx.guild.members:
			roles = [role.name for role in member.roles]
			if config.unconfirmed_member_role_name not in roles:
				if config.student_role_name in roles or config.class_master_role_name in roles:
					for category in ctx.guild.categories:
						if category_name == category.name:
							if valid.is_valid_group_name(category.name):
								speciality, year = category.name.split('-')
								if (speciality in roles and year in roles) or config.admin_role_name in roles:
									await category.set_permissions(member, view_channel=True)
		embed = create_embed(ctx, 'Adaugarea membrilor', f'Finailzat', discord.Colour.gold())
		await msg.edit(embed=embed)

		# Adaugarea profesorilor si elevilor in canalele cu limba straina
		embed = create_embed(ctx, 'Actualizarea permisiunilor', 'In desfasurare...', discord.Colour.dark_green())
		await msg.edit(embed=embed)
		for member in ctx.guild.members:
			roles = [role.name for role in member.roles]

			if config.unconfirmed_member_role_name not in roles:
				if config.student_role_name in roles:
					for category in ctx.guild.categories:
						if category_name == category.name:
							if valid.is_valid_group_name(category.name):
								speciality, year = category.name.split('-')
								if speciality in roles and year in roles:
									for channel in category.channels:
										if channel.name == config.english_channel_name and channel.name not in roles:
											await channel.set_permissions(member, view_channel=None)
										elif channel.name == config.francais_channel_name and channel.name not in roles:
											await channel.set_permissions(member, view_channel=None)
				elif config.teacher_role_name in roles:
					for role in member.roles:
						if role.name.startswith('#'):
							splited_discipline = role.name.split('_')
							group_name = splited_discipline[0][1:]
							# Daca numele primului element din lista coincide cu categoria
							for category in ctx.guild.categories:
								if category_name == category.name:
									if category.name in splited_discipline:
										# Pentru fiecare denumire de canal se verifica coincidenta cu denumirea rolurilor
										channels = sync_result[group_name]
										for element in channels:
											if element[0] == category.name:
												await element[1].set_permissions(member, view_channel=True)

										voice_channel = sync_result[config.voice_channel_name]
										for element in voice_channel:
											if element[0] == category.name:
												await element[1].set_permissions(member, view_channel=True)
		embed = create_embed(ctx, 'Actualizarea permisiunilor', f'Finailzat', discord.Colour.green())
		await msg.edit(embed=embed)

	# Asocierea rolurilor si canalelor
	@commands.command()
	@commands.has_role('Admin')
	async def update(self, ctx):
		await ctx.channel.purge(limit=1)
		embed = create_embed(ctx, 'Procesul de actualizare', 'Initializare', discord.Colour.purple())
		msg = await ctx.channel.send(embed=embed)
		sync_result = await sync_channels(ctx, msg)
		await adaugarea_elevilor(ctx, msg)
		await set_language_groups_and_teachers(ctx, msg, sync_result)


def setup(client):
	client.add_cog(ChannelRoles(client))
