import discord_components

import main
import config
import asyncio
import discord
import discord.ext
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle


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


def is_group_name_exist(group_name: str, ctx: discord.Message) -> bool:
	for category in ctx.guild.categories:
		if category.name == group_name:
			return True

	return False


def crete_embed_for_default_lessons(group_name: str, mention: str, lessons: [str]) -> discord.Embed:
	embed = discord.Embed(title=f'Creaza o grupa nou', description=f'Salut {mention}. Setati categoria, canalele si disciplinele pentru grupa **{group_name}**.\nMesajul va fi sters peste **40 secunde** de inactivitate.', color=discord.Colour.orange())
	value_lessons = '`Nimic`'
	if len(lessons) != 0:
		value_lessons = ''
		for lesson in lessons:
			value_lessons += f'`{lesson}`; '

	embed.add_field(name='Disciplinile generale', value=value_lessons, inline=False)
	return embed


def crete_embed_additional_lessons(group_name: str, mention: str, default_lessons: [str]) -> discord.Embed:
	embed = discord.Embed(title=f'Creaza o grupa nou', description=f'Salut {mention}. Setati categoria, canalele si disciplinele pentru grupa **{group_name}**.\nComanda va expira in **2 minute** de inactivitate.', color=discord.Colour.gold())
	default_value_lessons = '`Nimic`'
	if len(default_lessons) != 0:
		default_value_lessons = ''
		for default_lesson in default_lessons:
			default_value_lessons += f'`{default_lesson}`; '

	embed.add_field(name='Disciplinile generale', value=default_value_lessons, inline=False)
	return embed


async def add_default_lessons(ctx: discord.Message, the_bot_msg: discord.Message, client: discord.Client, group_name: str, lessons: [str], components: [[discord_components.Button]]) -> bool:
	def check(the_event):
		return the_event.message.id == the_bot_msg.id

	while True:
		try:
			event = await client.wait_for('button_click', timeout=39, check=check)
			await event.respond(type=6)
		except asyncio.TimeoutError:
			await the_bot_msg.delete()
			return True
		else:
			if event.component.id == 'cancel':
				await the_bot_msg.delete()
				await ctx.channel.send(content=f'Salut {event.author.mention}, ai anulat crearea unei grupe noi.')
				return True
			elif event.component.id == 'ok':
				return False
			elif event.component.id not in lessons:
				lessons.append(event.component.id)
				row_count = 0
				while row_count < len(components):
					btn_count = 0
					while btn_count < len(components[row_count]):
						if components[row_count][btn_count].id == event.component.id:
							components[row_count][btn_count].disabled = True
						btn_count += 1
					row_count += 1
				await the_bot_msg.edit(embed=crete_embed_for_default_lessons(group_name, ctx.author.mention, lessons), components=components)


async def add_additional_lessons(ctx: discord.Message, the_bot_msg: discord.Message, client: discord.Client) -> ([str], str):
	def check(the_event_message: discord.Message):
		return the_event_message.channel.id == ctx.channel.id

	try:
		event: discord.Message = await client.wait_for('message', timeout=119, check=check)
	except asyncio.TimeoutError:
		await the_bot_msg.delete()
		await ctx.channel.send('S-a scur timpul de **2 minute** acordat pentru raspuns.')
		return
	else:
		additional_lessons: list[str] = event.content.split(' ')
		additional_lessons_value = ''
		await event.delete()
		for additional_lesson in additional_lessons:
			if len(additional_lesson) < 3:
				await the_bot_msg.delete()
				await ctx.channel.send('**ERROR**. Mesajul nu corespunde formatului necesar.')
				return
			additional_lessons_value += f'`{additional_lesson}`; '

		return additional_lessons, additional_lessons_value


async def get_confirmation(ctx: discord.Message, client: discord.Client, the_bot_msg: discord.Message) -> bool:
	def check(the_event_message: discord.Message):
		return the_event_message.channel.id == ctx.channel.id

	try:
		event: discord_components.Interaction = await client.wait_for('button_click', timeout=119, check=check)
		await event.respond(type=6)
	except asyncio.TimeoutError:
		return False
	else:
		if event.component.id == 'ok':
			return True
		else:
			await the_bot_msg.delete()
			await ctx.channel.send(f'Salut {event.author.mention}, ai anulat crearea unei grupe noi.')
			return False


async def create_new_group(guild: discord.Guild, group_name: str, default_lessons: [str], additional_lessons: [str]):
	category = await guild.create_category(group_name)
	await category.create_text_channel('public')
	for default_lesson in default_lessons:
		await category.create_text_channel(default_lesson)

	for additional_lesson in additional_lessons:
		await category.create_text_channel(additional_lesson)

	await category.create_text_channel(config.commands_channel_name)
	await category.create_voice_channel('voce')


class SchoolGroupManagement(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.has_role('Admin')
	@commands.command(pass_context=True, aliases=['newgroup'])
	async def new_group(self, ctx: discord.Message, group_name: str=None):
		if group_name is None:
			await ctx.channel.send(f'**ERROR**. Trebuie sa introduceti numele grupei dupa comanda. Exemplu: `{config.cmd_prefix}newgroup AA-0119`.')
			return

		if not is_valid_group_name(group_name):
			await ctx.channel.send(f'**ERROR**. Numele grupei `{group_name}` nu corespunde formatului de denumire a grupelor.')
			return

		if is_group_name_exist(group_name, ctx):
			await ctx.channel.send(f'**ERROR**. Grupa `{group_name}` deja exista in server.')
			return

		await ctx.message.delete()

		default_lessons = []
		components = [[
				Button(style=ButtonStyle.blue, label='Matematica', id='matematica'),
				Button(style=ButtonStyle.blue, label='Informatica', id='informatica'),
				Button(style=ButtonStyle.blue, label='Biologia', id='biologia'),
				Button(style=ButtonStyle.blue, label='Chimia', id='chimia'),
				Button(style=ButtonStyle.blue, label='Fizica', id='fizica'),
			], [
				Button(style=ButtonStyle.blue, label='Ed. Fizica', id='educatia-fizica'),
				Button(style=ButtonStyle.blue, label='Instoria', id='istoria'),
				Button(style=ButtonStyle.blue, label='D. P.', id='dezvoltarea-personala'),
				Button(style=ButtonStyle.blue, label='Ed. P. Societate', id='educatia-pentru-societate'),
				Button(style=ButtonStyle.blue, label='Geografia', id='geografia'),
			], [
				Button(style=ButtonStyle.blue, label='L. Engleza', id='limba-engleza'),
				Button(style=ButtonStyle.blue, label='L. Franceza', id='limba-franceza'),
				Button(style=ButtonStyle.blue, label='L. Romana', id='limba-romana'),
			], [
				Button(style=ButtonStyle.green, label='Confirma', id='ok'),
				Button(style=ButtonStyle.red, label='Anuleaza', id='cancel')
			]]

		the_bot_msg: discord.Message = await ctx.channel.send(embed=crete_embed_for_default_lessons(group_name, ctx.author.mention, default_lessons), components=components)
		is_error = await add_default_lessons(ctx, the_bot_msg, self.client, group_name, default_lessons, components)
		if is_error:
			return

		embed = crete_embed_additional_lessons(group_name, ctx.author.mention, default_lessons)
		embed.add_field(name='Disciplinile de profil sau adaugatoare', value='Trimiteti-mi un mesaj in decurs de **2 minute**, in care aceste disciplini vor fi scrise dupa formatul din exemplul urmator: `c-a-d` `electronica-industriala` `masini-e-a`.\nCursurile sunt delimitate de spatii libere, iar spatiile din denumirile cursurilor sunt inlocuite cu "-".', inline=False)
		await the_bot_msg.edit(embed=embed, components=[])

		result = await add_additional_lessons(ctx, the_bot_msg, self.client)
		if result is None:
			return

		additional_lessons: list[str] = result[0]
		additional_lessons_value: str = result[1]
		components = [[Button(style=ButtonStyle.green, label='Confirma', id='ok'), Button(style=ButtonStyle.red, label='Anuleaza', id='cancel')]]

		embed = crete_embed_additional_lessons(group_name, ctx.author.mention, default_lessons)
		embed.add_field(name='Disciplinile de profil sau adaugatoare', value=additional_lessons_value, inline=False)
		await the_bot_msg.edit(embed=embed, components=components)

		if not await get_confirmation(ctx, self.client, the_bot_msg):
			return

		await the_bot_msg.edit(embed=embed, components=[])
		await create_new_group(ctx.guild, group_name, default_lessons, additional_lessons)

		embed = embed = discord.Embed(title=f'Creaza o grupa nou', description=f'Grupa **{group_name}** a fost creata cu succes.', color=discord.Colour.green())
		await the_bot_msg.edit(embed=embed, components=[])


def setup(client):
	client.add_cog(SchoolGroupManagement(client))
