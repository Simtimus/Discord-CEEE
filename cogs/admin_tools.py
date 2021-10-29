import discord
import os
import asyncio
import main
from discord.ext import commands
from discord_components import DiscordComponents, Button, ButtonStyle


# Initierea clasului
class Admin(commands.Cog):
	def __init__(self, client):
		self.client = client

	# Channel cleaning command
	@commands.command(aliases=['purge', 'clean', 'cls'])
	@commands.has_role('Admin')
	async def clear(self, ctx, amount=2):
		await ctx.channel.purge(limit=amount)

	@commands.command(pass_context=True, aliases=['cog'])
	@commands.has_role('Admin')
	async def cogs(self, ctx, *args):
		msg_text = f'Salut {ctx.author.mention}. Alegeti operatiunea dorita de dumneavoastra.'
		btn_reload = Button(style=ButtonStyle.green, label='Reincarca', id='reload')
		btn_load = Button(style=ButtonStyle.blue, label='Incarca', id='load')
		btn_unload = Button(style=ButtonStyle.red, label='Descarca', id='unload')
		msg = await ctx.channel.send(msg_text, components=[[btn_reload, btn_load, btn_unload]])

		def check(m):
			return m.channel == ctx.channel and (m.component.id == 'reload' or m.component.id == 'load' or m.component.id == 'unload')

		try:
			response = await self.client.wait_for('button_click', timeout=4, check=check)
		except asyncio.TimeoutError:
			await ctx.message.delete()
			await msg.delete()
		else:
			await msg.delete()
			args_without_error = []
			args = list(args)
			if len(args) == 0:
				args = main.cog_names.copy()

			for arg in args:
				if response.component.id == 'load':
					if f'{arg}.py' not in os.listdir('./cogs'):
						await ctx.channel.send(f'**[ERROR]** Salut {ctx.author.mention}. Cog-ul: "{arg}" nu exitsa.', components=[])
					elif arg in main.cog_names:
						await ctx.channel.send(f'**[ERROR]** Salut {ctx.author.mention}. Cog-ul: "{arg}" a fost deja incarcat.', components=[])
					else:
						self.client.load_extension(f'cogs.{arg}')
						main.cog_names.append(arg)
						args_without_error.append(arg)
				elif response.component.id == 'reload':
					if f'{arg}.py' not in os.listdir('./cogs'):
						await ctx.channel.send(f'**[ERROR]** Salut {ctx.author.mention}. Cog-ul: "{arg}" nu exitsa.', components=[])
					elif arg not in main.cog_names:
						await ctx.channel.send(f'**[ERROR]** Salut {ctx.author.mention}. Cog-ul: "{arg}" nu a fost incarcat.', components=[])
					else:
						self.client.reload_extension(f'cogs.{arg}')
						args_without_error.append(arg)
				elif response.component.id == 'unload':
					if arg in main.cog_names:
						self.client.unload_extension(f'cogs.{arg}')
						main.cog_names.remove(arg)
						args_without_error.append(arg)
					else:
						await ctx.channel.send(f'**[ERROR]** Salut {ctx.author.mention}. Cog-ul: "{arg}" nu a fost incarcat.', components=[])

			msg_text = f'Salut {ctx.author.mention}. Operatiunea "{response.component.label} : {str(args_without_error)}" a fost executata cu succes.'
			await ctx.channel.send(msg_text, components=[])


def setup(client):
	client.add_cog(Admin(client))
