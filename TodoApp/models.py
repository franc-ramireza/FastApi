# Importamos la clase Base desde el archivo database.py
# Esta Base se usa para crear las tablas con SQLAlchemy
from database import Base

# Importamos los tipos de datos y la clase Column para definir las columnas de la tabla
from sqlalchemy import Column, Integer, String, Boolean

# Definimos el modelo Todos, que será una tabla en la base de datos

class Todos(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True , index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean , default=False)
