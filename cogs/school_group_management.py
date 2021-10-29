import main
import config
import asyncio
import discord
import discord.ext
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle


# def arrange_the_buttons():
# 	Button = []
# 	components = []
# 	i = 0
# 	for lesson in config.default_school_lessons:
#


class SchoolGroupManagment(commands.Cog):
	def __init__(self, client):
		self.client = client

	@commands.has_role('Admin')
	@commands.command(pass_context=True, aliases=['newgroup'])
	async def new_group(self, ctx: discord.Message):
		group_name = '?'
		embed = discord.Embed(title=f'Creaza o grupa nou', description=f'Salut {ctx.author.mention}. Cu ajutprul acestei comenzi puteti seta usor categoria pentru o grupa noua.\n**Numele grupei:** `{group_name}`.', color=discord.Colour.gold())
		embed.add_field(name='Disciplinile grupei', value=f'', inline=True)

		components = [
			[
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
