import urllib
import os

import sqlalchemy
from pydantic import BaseModel
import databases
from databases import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List

#DATABASE_URL = "postgres://yumwiiyonbrhtq:335a7abfe2c16429ae3fac7b2e68b553da9f4fd2c8c4bdc592c368fe807ae692@ec2-52-86-2-228.compute-1.amazonawscom:5432/d7djdi44gfhefq"

host_server = os.environ.get('host_server', 'localhost')
db_server_port = urllib.parse.quote_plus(
    str(os.environ.get('db_server_port', '5432')))
database_name = os.environ.get('database_name', 'fastapi')
db_username = urllib.parse.quote_plus(
    str(os.environ.get('db_username', 'postgres')))
db_password = urllib.parse.quote_plus(
    str(os.environ.get('db_password', '1234')))
ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode', 'prefer')))

DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}?sslmode={}'.format(
    db_username, db_password, host_server, db_server_port, database_name, ssl_mode)

metadata = sqlalchemy.MetaData()


empleado = sqlalchemy.Table(
    'empleado',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nombre", sqlalchemy.String),
    sqlalchemy.Column("apellido", sqlalchemy.String),
    sqlalchemy.Column("direccion", sqlalchemy.String),
    sqlalchemy.Column("telefono", sqlalchemy.String),
    sqlalchemy.Column("salario", sqlalchemy.Integer),
    sqlalchemy.Column("comDepV", sqlalchemy.Integer),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, pool_size=10, max_overflow=0
)
metadata.create_all(engine)


class ClienteIn(BaseModel):
    rut: int
    nombre: str
    direccion: str
    telefono: str
    contacto: str


class ProveedorIn(BaseModel):
    rut: int
    nombre: str
    direccion: str
    telefono1: str
    telefono2: str
    calle: str
    numero: str
    comuna: str
    ciudad: str


class ProductoIn(BaseModel):
    id: int
    nombre: str
    precioActual: float
    stock: int
    proveedor: str


class EmpleadoIn(BaseModel):
    id: int
    nombre: str
    apellido: str
    direccion: str
    telefono: str
    salario: int
    comDepV: int


class Empleado(BaseModel):
    nombre: str
    apellido: str
    direccion: str
    telefono: str
    salario: int
    comDepV: int


"""class EmpleadoIn(BaseModel):
    nombre: str
    apellido: str
    status: bool

class Empleado(BaseModel):
    id: int
    nombre: str
    apellido: str
    status: bool
"""

app = FastAPI(title="FAST API UMG ")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


database = databases.Database(DATABASE_URL)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnet()


@app.post("/empleados/", response_model=Empleado)
async def create_empleado(emp: EmpleadoIn):
    query = empleado.insert().values(
        id=emp.id, nombre=emp.nombre, apellido=emp.apellido, direccion=emp.direccion, telefono=emp.telefono, salario=emp.salario, comDepV=emp.comDepV)

    last_record_id = await database.execute(query)
    return {**emp.dict(), "id": last_record_id}


@app.get("/getEmpleado/", response_model=List[Empleado])
async def getEmpleado(skip: int = 0, take: int = 20):
    query = empleado.select().offset(skip).limit(take)
    return await database.fetch_all(query)


@app.delete("/empleadoDelete/{empleado_id}/")
async def del_empleado(emp_id: int):
    query = empleado.delete().where(empleado.c.id == emp_id)
    await database.execute(query)
    return {"message": " Empleado with id:{} deleted succesfully!".format(emp_id)}


@app.put("/empleadoUpdate/{emp_id}", response_model=Empleado)
async def setEmpleadoId(emp_id: int, emp: EmpleadoIn):
    query = empleado.update().where(empleado.c.id == emp_id).values(
        id=emp.id, nombre=emp.nombre, apellido=emp.apellido, direccion=emp.direccion, telefono=emp.telefono, salario=emp.salario, comDepV=emp.comDepV)
    await database.execute(query)
    return {**emp.dict(), "id": emp_id}
