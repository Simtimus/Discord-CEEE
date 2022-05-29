import os

# 546E7A - grupa
# 11806A - obiectul predat
# 607D8B - limba straina

cmd_prefix = '.'
TOKEN = ''
school_host = ''
school_user = ''
school_password = ''
school_database = ''

admin_role_name = 'Admin'
teacher_role_name = 'Profesor'
unconfirmed_teacher_role_name = 'Profesor?'
class_master_role_name = 'Diriginte'
student_role_name = 'Elev'
unconfirmed_member_role_name = 'Neconfirmat'
english_channel_name = 'limba-engleza'
francais_channel_name = 'limba-franceza'
commands_channel_name = 'comenzi'
voice_channel_name = 'voce'

important_roles_name = ['Dev', admin_role_name, 'Bots', 'Moderator', teacher_role_name, unconfirmed_teacher_role_name, class_master_role_name, student_role_name, unconfirmed_member_role_name, english_channel_name, francais_channel_name]

lowercase = ['a', 'ă', 'â',  'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'î', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 'ș', 't', 'ț', 'u', 'v', 'w', 'x', 'y', 'z']
uppercase = [a.upper() for a in lowercase]

server_join_link = 'https://discord.gg/7bPVtAWUxu'
website_link = 'https://discord-site-ceee.herokuapp.com/login'
guild_id = 875688932271087657
bot_notification_channel_id = 904096410532724756

is_local_run = None

if 'local_config.py' in os.listdir('.'):
	is_local_run = True
	import local_config
	cmd_prefix = local_config.cmd_prefix
	TOKEN = local_config.TOKEN
	school_host = local_config.db_host
	school_user = local_config.db_user
	school_password = local_config.db_password
	school_database = local_config.db_database
else:
	is_local_run = False
	TOKEN = os.getenv('TOKEN')
	school_host = os.getenv('db_host')
	school_user = os.getenv('db_user')
	school_password = os.getenv('db_password')
	school_database = os.getenv('db_database')
