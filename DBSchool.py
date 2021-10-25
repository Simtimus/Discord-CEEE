import inspect
import mysql.connector
import datetime
import pytz
import time


def reconnect(func: classmethod):
	def new_func(self, *args, **kwargs):
		if time.time() - self.last_connection_time > self.minutes_passed_for_reconnection:
			self.mydb = mysql.connector.connect(host=self.host, user=self.user, password=self.db_password)
			self.last_connection_time = time.time()
			self.mycursor = self.mydb.cursor()
			self.mycursor.execute(f'USE {self.db_name}')

		return func(self, *args, **kwargs)  # Se executa functia originala.

	new_func.__name__ = func.__name__
	sig = inspect.signature(func)
	new_func.__signature__ = sig.replace(parameters=tuple(sig.parameters.values()))
	return new_func


class ConnectToDB:
	def __init__(self, host: str, user: str, password: str, db_name: str, minutes_for_reconnection: int = 5):
		"""
		Creaza o clasa pentru interactiunea cu baza de date.
		"""
		self.host = host
		self.user = user
		self.db_password = password
		self.db_name = db_name
		self.mydb = mysql.connector.connect(host=self.host, user=self.user, password=self.db_password)
		self.last_connection_time = time.time()
		self.mycursor = self.mydb.cursor()
		self.mycursor.execute(f'USE {self.db_name}')
		self.minutes_passed_for_reconnection = minutes_for_reconnection * 60

	@reconnect
	def add_startup_log(self):
		"""
		Adauga datata si ora rularii bot-ului.
		"""
		dt = datetime.datetime.now(pytz.timezone("Europe/Chisinau"))
		self.mycursor.execute(f'INSERT INTO `StartUpLogs` (`DataSiOra`) VALUES ("{dt.date()} {dt.time()}")')
		self.mydb.commit()

	@reconnect
	def save_new_state(self, activity_type: str, status_type: str, activity_name: str):
		"""
		Salveaza statutul impreuna cu datata si ora acestuia.
		"""
		dt = datetime.datetime.now(pytz.timezone("Europe/Chisinau"))
		self.mycursor.execute(f'INSERT INTO `BotStates` (`DataSiOra`, `TipulDeActivitate`, `StareaInRetea`, `Denumirea`) VALUES ("{dt.date()} {dt.time()}", "{activity_type}", "{status_type}", "{activity_name}")')
		self.mydb.commit()

	@reconnect
	def get_last_state(self) -> tuple:
		"""
		Returneaza ultima stare, in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute(f"SELECT * FROM `BotStates` ORDER BY `Id` DESC LIMIT 1;")
		result = self.mycursor.fetchall()
		if len(result) == 0:
			return ()
		return self.mycursor.fetchall()[0]