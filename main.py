from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator, ConfigDict
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from bson import ObjectId
from dotenv import load_dotenv
import os
import time
import asyncio
from pymongo import ReturnDocument

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("La variable MONGODB_URI no está definida en el .env")

DB_NAME = os.getenv("MONGODB_DB", "Cluster0")
COLL_PAPERS = os.getenv("COLL_PAPERS", "papers")

client = None
db = None
papers = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, papers

    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    papers = db[COLL_PAPERS]

    yield

    client.close()


app = FastAPI(
    title="Repositorio Virtual Papers Científicos",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class paper(BaseModel):
    titulo: str
    autor: str
    area_estudio: str
    fecha: str
    numero_paginas: int


class PaperOut(PaperIn):
    id: str = Field(alias="_id")

    @field_validator("id", mode="before")
    @classmethod
    def object_to_str(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )


app.mount("/static", StaticFiles(directory="static"), name="static")


#Método GET para consultar los papers en la base
@app.get("/")
async def leer_index():
    return FileResponse("static/index.html")

@app.get("/estudiantes", response_model=list[PaperOut])
async def listar_papers():
    return await papers.find({}).to_list(length=50)



#Método GET para obgener un paper con su id
@app.get("/papers/{id}", response_model=PaperOut)
async def obtener_estudiante(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    doc = await papers.find_one(
        {"_id": ObjectId(id)}
    )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail="Paper no encontrado"
        )

    return doc


@app.post(
    "/estudiantes",
    response_model=EstudianteOut,
    status_code=status.HTTP_201_CREATED
)
async def crear_estudiante(e: EstudianteIn):

    correo_existe = await estudiantes.find_one(
        {"email": e.email}
    )

    if correo_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya se encuentra registrado."
        )

    result = await estudiantes.insert_one(
        e.model_dump()
    )

    nuevo = await estudiantes.find_one(
        {"_id": result.inserted_id}
    )

    return nuevo


@app.put("/estudiantes/{id}", response_model=EstudianteOut)
async def actualizar_estudiante(
    id: str,
    e: EstudianteIn
):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    result = await estudiantes.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": e.model_dump()},
        return_document=ReturnDocument.AFTER
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado."
        )

    return result


@app.delete(
    "/estudiantes/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def eliminar_estudiante(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    result = await estudiantes.delete_one(
        {"_id": ObjectId(id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado."
        )

    return None


def generar_reporte_pesado(nombre_estudiante: str):
    time.sleep(3)

    return {
        "estudiante": nombre_estudiante,
        "estado": "Reporte generado",
        "páginas": 10
    }


@app.post("/estudiantes/{id}/generar-reporte")
async def generar_reporte(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    estudiante = await estudiantes.find_one(
        {"_id": ObjectId(id)}
    )

    if not estudiante:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado."
        )

    reporte = await asyncio.to_thread(
        generar_reporte_pesado,
        estudiante["nombre"]
    )

    return reporte