import mysql.connector
import datetime
import pytz
import time
import inspect


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


class ConnectTo_db:
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

	# def Reconnect(self) -> None:
	# 	if time.time() - self.last_connection_time > self.minutes_passed_for_reconnection:
	# 		self.mydb = mysql.connector.connect(host=self.host, user=self.user, password=self.db_password)
	# 		self.last_connection_time = time.time()
	# 		print('Reconnect')
	# 		self.mycursor = self.mydb.cursor()
	# 		self.mycursor.execute(f'USE {self.db_name}')

	@reconnect
	def AddNewRow(self, table: str, columns: list, values: list, use_system_time: bool = False) -> None:
		"""
		Adauga o noua linie in tabel. "use_system_time" - asigura utilizarea timpului standart al sistemei. In caz contrar timpul se stabileste automat in regiunea "Europe/Chisinau"
		"""
		columns_lower = []
		for column in columns:
			columns_lower.append(column.lower())

		if len(columns) != len(values):
			raise Exception('Nu coincide nr. de elemente in "columns" cu nr. de elemente in "values"')
		elif 'datasiora' in columns_lower or 'id' in columns_lower:
			raise Exception('Nu puteti seta manual parametrii "DataSiOra" sau "Id" in "columns"')

		if use_system_time:
			dt_now = datetime.datetime.now()
		else:
			dt_now = datetime.datetime.now(pytz.timezone("Europe/Chisinau"))
			dt_now = f"{dt_now.date()} {dt_now.time()}"

		request = f'INSERT INTO `{table}` (`DataSiOra`, '
		for column in columns:
			request += f'`{column}`'
			if columns[-1] != column:
				request += ', '
			else:
				request += ') '

		request += f'VALUES ("{dt_now}", '
		for value in values:
			request += f'"{value}"'
			if values[-1] != value:
				request += ', '
			else:
				request += ')'

		self.mycursor.execute(request)
		self.mydb.commit()

	@reconnect
	def GetTableNames(self) -> tuple:
		"""
		Returneaza o lista cu numele tuturor tabelelelor existente in baza de date, in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute("SHOW tables")
		table_names = ()

		for table in self.mycursor.fetchall():
			table_names += (table[0],)

		return table_names

	@reconnect
	def GetColumnNames(self, table: str) -> tuple:
		"""
		Returneaza un tuple cu numele tuturor coloanelor existente in tabel, in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute(f"SHOW COLUMNS FROM {table}")
		columns = self.mycursor.fetchall()
		column_names = ()
		for column in columns:
			column_names += (column[0],)
		return column_names

	@reconnect
	def GetAllRowsFromTable(self, table: str) -> tuple:
		"""
		Returneaza un tuple cu toate randurile existente in tabel, in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute(f"SELECT * FROM {table}")
		return self.mycursor.fetchall()

	@reconnect
	def GetFirstRow(self, table: str) -> tuple:
		"""
		Returneaza primul rand din tabel, in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute(f"SELECT * FROM `{table}` LIMIT 1;")
		return self.mycursor.fetchall()[0]

	@reconnect
	def GetLastRow(self, table: str) -> tuple:
		"""
		Returneaza ultimul rand din table, in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute(f"SELECT * FROM `{table}` ORDER BY `Id` DESC LIMIT 1;")
		return self.mycursor.fetchall()[0]

	@reconnect
	def SelectAllRowsFromTable(self, table: str, condition: str) -> tuple:
		"""
		Returneaza toate randurile din tabel in baza conditiei, in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute(f"SELECT * FROM `{table}` WHERE {condition};")
		return self.mycursor.fetchall()

	@reconnect
	def UpdateRowUsingId(self, table: str, id: int, columns: list, values: list) -> None:
		"""
		Actualiza un rand bazanduse pe "Id", in urma unei noi cereri adresate bazei de date.
		"""
		columns_lower = []
		for column in columns:
			columns_lower.append(column.lower())

		if len(columns) != len(values):
			raise Exception('Nu coincide nr. de elemente in "columns" cu nr. de elemente in "values"')
		elif 'datasiora' in columns_lower or 'id' in columns_lower:
			raise Exception('Nu puteti actualiza manual parametrii "DataSiOra" sau "Id" in "columns"')

		i = 0
		request = f'UPDATE `{table}` SET '
		while i < len(columns):
			request += f"{columns[i]} = '{values[i]}'"
			if i != len(columns) - 1:
				request += ', '
			i += 1

		request += f' WHERE `Id` = {id}'
		self.mycursor.execute(request)
		self.mydb.commit()

	@reconnect
	def DeleteRowUsingID(self, table: str, id: int) -> None:
		"""
		Sterge un rand bazanduse pe "Id", in urma unei noi cereri adresate bazei de date.
		"""
		self.mycursor.execute(f'DELETE FROM {table} WHERE `Id`={id}')
		self.mydb.commit()
