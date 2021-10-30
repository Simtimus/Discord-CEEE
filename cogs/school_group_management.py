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


class SchoolGroupManagment(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.has_role('Admin')
	@commands.command(pass_context=True, aliases=['newgroup'])
	async def new_group(self, ctx: discord.Message, group_name: str):
		if group_name is None:
			await ctx.channel.send(f'**ERROR**. Trebuie sa introduceti numele grupei dupa comanda. Exemplu: `{config.cmd_prefix}newgroup AA-0119`.')
			return

		if not is_valid_group_name(group_name):
			await ctx.channel.send(f'**ERROR**. Numele grupei `{group_name}` nu corespunde formatului de denumire a grupelor.')
			return

		lessons = []
		# available_lessons = ['Matematica', 'L. Romana', 'Biologia', 'Chimia', 'Fizica', 'Ed. Fizica', 'Instoria', 'D. P.', 'Ed. P. societate', 'L. Straina', 'Geografia', 'Informatica']

		embed = discord.Embed(title=f'Creaza o grupa nou', description=f'Salut {ctx.author.mention}. Setati categoria, canalele si disciplinele pentru grupa **{group_name}**.\nMesajul va fi sters peste 40 secunde de inactivitate.', color=discord.Colour.gold())
		embed.add_field(name='Disciplinile grupei', value=f'`Nimic`', inline=True)

		components = [[
				Button(style=ButtonStyle.blue, label='Matematica', id='Matematica'),
				Button(style=ButtonStyle.blue, label='L. Romana', id='L. Romana'),
				Button(style=ButtonStyle.blue, label='Biologia', id='Biologia'),
				Button(style=ButtonStyle.blue, label='Chimia', id='Chimia'),
				Button(style=ButtonStyle.blue, label='Fizica', id='Fizica'),
			], [
				Button(style=ButtonStyle.blue, label='Ed. Fizica', id='Ed. Fizica'),
				Button(style=ButtonStyle.blue, label='Instoria', id='Instoria'),
				Button(style=ButtonStyle.blue, label='D. P.', id='D. P.'),
				Button(style=ButtonStyle.blue, label='Ed. P. societate', id='Ed. P. societate'),
				Button(style=ButtonStyle.blue, label='L. Straina', id='L. Straina')
			], [
				Button(style=ButtonStyle.blue, label='Geografia', id='Geografia'),
				Button(style=ButtonStyle.blue, label='Informatica', id='Informatica'),
				Button(style=ButtonStyle.green, label='Confirma', id='ok'),
				Button(style=ButtonStyle.red, label='Anuleaza', id='cancel')
			]]

		the_bot_msg = await ctx.channel.send(embed=embed, components=components)

		def check(the_event):
			return the_event.message.id == the_bot_msg.id

		while True:
			try:
				event = await self.client.wait_for('button_click', timeout=39, check=check)
				await event.respond(type=6)
			except asyncio.TimeoutError:
				await the_bot_msg.delete()
				await ctx.message.delete()
				return
			else:
				if event.component.id == 'cancel':
					await the_bot_msg.delete()
					await ctx.message.delete()
					await ctx.channel.send(content=f'Salut {event.author.mention}, ai anulat crearea unei grupe noi.')
					return
				elif event.component.id == 'ok':
					break
				elif event.component.id not in lessons:
					lessons.append(event.component.id)
					row_count = 0
					while row_count < len(components):
						btn_count = 0
						while btn_count < len(components[row_count]):
							if components[row_count][btn_count].id == event.component.id:
								components[row_count][btn_count].disabled = True
								lessons.append(components[row_count][btn_count].id)
							btn_count += 1
						row_count += 1

					await the_bot_msg.edit(embed=embed, components=components)


def setup(client):
	client.add_cog(SchoolGroupManagment(client))
