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
import random

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

class PaperIn(BaseModel):
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

#Crear un nuevo paper jeje
@app.post(
    "/papers",
    response_model=PaperOut,
    status_code=status.HTTP_201_CREATED
)
async def crear_paper(e: PaperIn):

    titulo_paper_existe = await papers.find_one(
        {"titulo": e.titulo}
    )

    if titulo_paper_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El título del Paper ya existe."
        )

    result = await papers.insert_one(
        e.model_dump()
    )

    nuevo = await papers.find_one(
        {"_id": result.inserted_id}
    )

    return nuevo


@app.put("/estudiantes/{id}", response_model=PaperOut)
async def actualizar_estudiante(
    id: str,
    e: PaperIn
):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    result = await papers.find_one_and_update(
        {"_id": ObjectId(id)},
        {"$set": e.model_dump()},
        return_document=ReturnDocument.AFTER
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Paper no encontrado."
        )

    return result


@app.delete(
    "/papers/{id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def eliminar_paper(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    result = await papers.delete_one(
        {"_id": ObjectId(id)}
    )

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Paper no encontrado."
        )

    return None


def revision_validez_paper(nombre_paper: str):
    time.sleep(5)

    return {
        "estudiante": nombre_paper,
        "estado": "Revisión Finalizada",
        "páginas": random.random.randint(1,20)
    }


@app.post("/papers{id}/revision-validez")
async def revision_validez_paper(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    paper = await papers.find_one(
        {"_id": ObjectId(id)}
    )

    if not paper:
        raise HTTPException(
            status_code=404,
            detail="Paper no encontrado."
        )

    revision = await asyncio.to_thread(
        revision_validez_paper,
        paper["nombre"]
    )

    return revision