import os

cmd_prefix = '.'
TOKEN = ''
school_host = ''
school_user = ''
school_password = ''
school_database = ''

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
