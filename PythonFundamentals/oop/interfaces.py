
from abc import ABC, abstractmethod

# Creamos una clase abstracta utilizando el modulo abc (Abstract Base Classes)
# Haciendo heredar a la clase ABC en la definicion de la clase
# El principal caso de uso de las clases abstractas es para definir interfaces
#  es decir, un contrato con conjunto de metodos que deben ser implementados por las subclases
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

    def disconnect(self) -> None:
        print("Disconnecting from PostgreSQL database...")

    def execute_query(self, query: str) -> None:
        print(f"Executing query on PostgreSQL database: {query}")
        self.log_query(query)

class CassandraDatabase(Database):
    def connect(self) -> None:
        print("Connecting to Cassandra database...")

    def disconnect(self) -> None:
        print("Disconnecting from Cassandra database...")

    def execute_query(self, query: str) -> None:
        print(f"Executing query on Cassandra database: {query}")
        self.log_query(query)

postgres_db = PostgreSQLDatabase()
cassandra_db = CassandraDatabase()

