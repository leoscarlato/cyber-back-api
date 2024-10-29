from fastapi import FastAPI
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from pydantic import Field
from fastapi import APIRouter
from passlib.context import CryptContext
from db import DB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
    prefix="/usuario",
    tags=["usuario"]
)

usuarios = DB.usuarios

class Usuario(BaseModel):
    id_usuario: str = None
    nome: str
    email: str
    senha: str

    def hash_password(self):
        self.senha = pwd_context.hash(self.senha)


@router.post("/", response_model=Usuario)
def create_usuario(usuario: Usuario):

    """Rota para criar um novo usuario"""

    if usuario.id_usuario is None:
        usuario.id_usuario = str(uuid4())
    usuario.hash_password()
    usuarios.append(usuario)
    return usuario

@router.get("/")
def get_usuarios():
    
    """Rota para listar todos os usuarios"""
    
    return usuarios 

@router.get("/{id_usuario}")
def get_usuario(id_usuario: str):

    """Rota para listar um usuario específico"""

    for usuario in usuarios:
        if usuario.id_usuario == id_usuario:
            return usuario
    return {"message": "Usuario não encontrado"}

@router.put("/{id_usuario}")
def update_usuario(id_usuario: str, usuario: Usuario):

    """Rota para atualizar um usuario"""

    for u in usuarios:
        if u.id_usuario == id_usuario:
            u.nome = usuario.nome
            u.email = usuario.email
            u.senha = usuario.senha
            u.hash_password()
            return u
    return {"message": "Usuario não encontrado"}

@router.delete("/{id_usuario}")
def delete_usuario(id_usuario: str):

    """Rota para deletar um usuario"""
    
    for i, u in enumerate(usuarios):
        if u.id_usuario == id_usuario:
            usuarios.pop(i)
            return {"message": "Usuario removido"}
    return {"message": "Usuario não encontrado"}