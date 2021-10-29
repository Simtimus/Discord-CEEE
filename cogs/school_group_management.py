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
	async def new_group(self, ctx: discord.Message, group_name: str=None):
		if group_name is None:
			await ctx.channel.send(f'**ERROR**. Trebuie sa introduceti numele grupei dupa comanda. Exemplu: `{config.cmd_prefix}newgroup AA-0119`.')
			return

		if not is_valid_group_name(group_name):
			await ctx.channel.send(f'**ERROR**. Numele grupei `{group_name}` nu corespunde formatului de denumire a grupelor.')
			return

		embed = discord.Embed(title=f'Creaza o grupa nou', description=f'Salut {ctx.author.mention}. Cu ajutprul acestei comenzi puteti seta usor categoria pentru o grupa **{group_name}**.', color=discord.Colour.gold())
		embed.add_field(name='Disciplinile grupei', value=f'?', inline=True)

		components = [[
				Button(style=ButtonStyle.grey, label='Matematica', id='matematica'),
				Button(style=ButtonStyle.grey, label='L. Romana', id='limba Romana'),
				Button(style=ButtonStyle.grey, label='Biologia', id='biologia'),
				Button(style=ButtonStyle.grey, label='Chimia', id='chimia'),
				Button(style=ButtonStyle.grey, label='Fizica', id='fizica')
			],
			[
				Button(style=ButtonStyle.blue, label='Ed. Fizica', id='ed. fizica'),
				Button(style=ButtonStyle.grey, label='Instoria', id='istoria'),
				Button(style=ButtonStyle.green, label='D. P.', id='d. p.')
			]]

		the_bot_msg = await ctx.channel.send(embed=embed)


def setup(client):
	client.add_cog(SchoolGroupManagment(client))
