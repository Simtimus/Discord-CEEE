import os

cmd_prefix = '.'
TOKEN = ''
school_host = ''
school_user = ''
school_password = ''
school_database = ''

student_role = 'Elev'
teacher_role = 'Profesor'
unconfirmed_teacher_role = 'Profesor?'
class_master_role = 'Diriginte'
admin_role = 'Admin'
english_channel = 'limba-engleza'
francais_channel = 'limba-franceza'
voice_channel = 'voce'
confirmed_member = 'Confirmat'
unconfirmed_member = 'Neconfirmat'


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
