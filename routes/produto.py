from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from pydantic import Field
from fastapi import APIRouter
from passlib.context import CryptContext
from db import DB

router = APIRouter(
    prefix="/produto",
    tags=["produto"]
)

class Produto(BaseModel):
    id_produto: str = None
    nome: str
    preco: float
    peso: float

@router.post("/", response_model=Produto)
def create_produto(produto: Produto):

    """Rota para criar um novo produto"""

    if produto.id_produto is None:
        produto.id_produto = str(uuid4())
    DB.produtos.append(produto)
    return produto

@router.get("/")
def get_produtos():

    """Rota para listar todos os produtos"""

    return DB.produtos

@router.get("/{id}")
def get_produto(id: str):

    """Rota para listar um produto específico"""

    for p in DB.produtos:
        if p.id_produto == id:
            return p
    return {"message": "Produto não encontrado"}


@router.put("/{id}")
def update_produto(id: str, produto: Produto):

    """Rota para atualizar um produto"""

    for p in DB.produtos:
        if p.id_produto == id:
            p.nome = produto.nome
            p.preco = produto.preco
            p.peso = produto.peso
            return p    
    return {"message": "Produto não encontrado"}

@router.delete("/{id}")
def delete_produto(id: str):

    """Rota para deletar um produto"""
    
    for i, p in enumerate(DB.produtos):
        if p.id_produto == id:
            DB.produtos.pop(i)
            return {"message": "Produto removido"}
    return {"message": "Produto não encontrado"}
