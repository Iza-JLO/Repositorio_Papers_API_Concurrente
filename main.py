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


"""
Me tardé como 2 horas persiguiendo un error de ip de MONGO :,cccc
"""


load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

if not MONGODB_URI:
    raise RuntimeError("La variable MONGODB_URI no está definida en el .env")

DB_NAME = os.getenv("MONGODB_DB", "Cluster0")
COLL_PAPERS = os.getenv("COLL_PAPERS", "papers")

client = None
db = None
papers = None


def get_mongo_client():
    return AsyncIOMotorClient(
        MONGODB_URI,
        connect=False,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=5000,
        retryWrites=True,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db, papers

    client = get_mongo_client()
    db = client[DB_NAME]
    papers = db[COLL_PAPERS]

    yield

    if client is not None:
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
async def listar_papers_legacy():
    return await listar_papers()


@app.get("/papers", response_model=list[PaperOut])
async def listar_papers():
    if papers is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="La base de datos no está disponible."
        )
    try:
        return await papers.find({}).to_list(length=50)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar a MongoDB Atlas. Verifica la URI, credenciales o acceso de red."
        ) from exc



#Método GET para obgener un paper con su id
@app.get("/estudiantes/{id}", response_model=PaperOut)
async def obtener_paper_legacy(id: str):
    return await obtener_paper(id)


@app.get("/papers/{id}", response_model=PaperOut)
async def obtener_paper(id: str):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    try:
        doc = await papers.find_one(
            {"_id": ObjectId(id)}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar a MongoDB Atlas. Verifica la URI, credenciales o acceso de red."
        ) from exc

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

    try:
        titulo_paper_existe = await papers.find_one(
            {"titulo": e.titulo}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar a MongoDB Atlas. Verifica la URI, credenciales o acceso de red."
        ) from exc

    if titulo_paper_existe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El título del Paper ya existe."
        )

    try:
        result = await papers.insert_one(
            e.model_dump()
        )

        nuevo = await papers.find_one(
            {"_id": result.inserted_id}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar a MongoDB Atlas. Verifica la URI, credenciales o acceso de red."
        ) from exc

    return nuevo


@app.put("/estudiantes/{id}", response_model=PaperOut)
async def actualizar_paper_legacy(
    id: str,
    e: PaperIn
):
    return await actualizar_paper(id, e)


@app.put("/papers/{id}", response_model=PaperOut)
async def actualizar_paper(
    id: str,
    e: PaperIn
):

    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=400,
            detail="ID inválido."
        )

    try:
        result = await papers.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": e.model_dump()},
            return_document=ReturnDocument.AFTER
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar a MongoDB Atlas. Verifica la URI, credenciales o acceso de red."
        ) from exc

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

    try:
        result = await papers.delete_one(
            {"_id": ObjectId(id)}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar a MongoDB Atlas. Verifica la URI, credenciales o acceso de red."
        ) from exc

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Paper no encontrado."
        )

    return None


def validar_revision_paper(nombre_paper: str):
    time.sleep(5)

    return {
        "paper": nombre_paper,
        "estado": "Revisión Finalizada",
        "páginas": random.randint(1, 20)
    }


@app.post("/papers/{id}/revision-validez")
async def revision_validez_paper_route(id: str):

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
        validar_revision_paper,
        paper["titulo"]
    )

    return revision