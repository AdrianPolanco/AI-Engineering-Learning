# Importando un modulo de un archivo (introduction) de un paquete Python (oop)
from error_handling.introduction import Database, PostgreSQLDatabase, CassandraDatabase

# Error por instanciacion de una clase abstracta (Database)
#database = Database()

postgres = PostgreSQLDatabase()
cassandra = CassandraDatabase()