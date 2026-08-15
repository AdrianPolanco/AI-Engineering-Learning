
from abc import ABC, abstractmethod
from random import random


class Database(ABC):

# Creamos metodos abstractos utilizando el decorador @abstractmethod
    @abstractmethod
    def connect(self) -> None:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def execute_query(self, query: str) -> None:
        pass

    # Create common methods that can be used by all subclasses
    def log_query(self, query: str) -> None:
        print(f"Logging query: {query}")

# This will raise a TypeError because we cannot instantiate an abstract class
# database = Database()  

class PostgreSQLDatabase(Database):
    def connect(self) -> None:
        print("Connecting to PostgreSQL database...")
        raises_error = random() < 0.5  # Simulating a 50% chance of connection failure
        if raises_error:
            raise PostgreSQLConnectionError()

    def disconnect(self) -> None:
        print("Disconnecting from PostgreSQL database...")

    def execute_query(self, query: str) -> None:
        print(f"Executing query on PostgreSQL database: {query}")
        self.log_query(query)

class CassandraDatabase(Database):
    def connect(self) -> None:
        print("Connecting to Cassandra database...")
        raises_error = random() < 0.5  # Simulating a 50% chance of connection failure
        if raises_error:
            raise CassandraConnectionError()

    def disconnect(self) -> None:
        print("Disconnecting from Cassandra database...")

    def execute_query(self, query: str) -> None:
        print(f"Executing query on Cassandra database: {query}")
        self.log_query(query)

# Creando una excepcion personalizada para manejar errores de conexión a la base de datos PostgreSQL
class PostgreSQLConnectionError(Exception):
    def __init__(self, message: str = "Error connecting to PostgreSQL database"):
        self.message = message
        super().__init__(self.message)

class CassandraConnectionError(Exception):
    def __init__(self, message: str = "Error connecting to Cassandra database"):
        self.message = message
        super().__init__(self.message)


def execute_query_on_database(database: Database) -> None:
    try:
        database.connect()
    except (PostgreSQLConnectionError, CassandraConnectionError) as e:
        print(f"Error occurred: {e}")
    # else se ejecuta si no ocurren errores en el bloque try
    else:
        if isinstance(database, PostgreSQLDatabase) or isinstance(database, CassandraDatabase):
            database.execute_query("SELECT * FROM users;")
    # finally se ejecuta siempre, sin importar si ocurrio un error o no
    finally:
        database.disconnect()

postgres_db = PostgreSQLDatabase()
cassandra_db = CassandraDatabase()

execute_query_on_database(postgres_db)
execute_query_on_database(cassandra_db)
