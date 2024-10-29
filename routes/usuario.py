from fastapi import Depends, APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlalchemy import create_engine, Column, String

from . import models
from . models import Usuario

from .database import SessionLocal, engine
from sqlalchemy.orm import Session as ORM_Session

models.Base.metadata.create_all(bind=engine)


router = APIRouter(
    prefix="/usuario",
    tags=["usuario"]
)

class UsuarioIn(BaseModel):
    nome: str = Field(..., description="Nome do usuário.")
    email: str = Field(..., description="E-mail do usuário.")
    senha: str = Field(..., description="Senha do usuário.")

class UsuarioOut(BaseModel):
    id_usuario: str = Field(description="ID único do usuário.")
    nome: str = Field(description="Nome do usuário.")
    email: str = Field(description="E-mail do usuário.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UsuarioOut, summary="Criar Usuário")
def create(usuarioIn: UsuarioIn = Body(
        ...,
        description="Dados do usuário a serem criados.",
        example={
            "nome": "Maciel Quental",
            "email": "enzoquental@btg.job.br",
            "senha": "teste"
        }
    ), db: ORM_Session = Depends(get_db)):
    """
    Cria um novo usuário com os dados fornecidos.

    Parâmetros:
    - `usuarioIn`: Dados do usuário a serem criados.
        Exemplo:
        ```
        {
            "nome": "Maciel Quental",
            "email": "enzoquental@btg.job.br",
            "senha": "teste"
        }
        ```
    """
    if db.query(Usuario).filter(Usuario.email == usuarioIn.email).first():
        raise HTTPException(400, detail=f"Usuário com email {usuarioIn.email} já cadastrado")

    usuario = Usuario(**usuarioIn.dict(), id_usuario=str(uuid4()))
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario
    
@router.get("/", summary="Listar Todos os Usuários")
def get_all(db: ORM_Session = Depends(get_db)):
    """
    Lista todos os usuários cadastrados.
    """
    return db.query(Usuario).all()
    
@router.get("/{id}", response_model=UsuarioOut, summary="Obter Usuário")
def get_unique(id: str = Path(..., description="ID do usuário que deseja obter."), db: ORM_Session = Depends(get_db)):
    """
    Obtém os detalhes de um usuário específico.

    Parâmetros:
    - `id`: ID do usuário que deseja obter.
        Exemplo:
        ```
        "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
    if usuario:
        return usuario
    raise HTTPException(404, detail=f"Usuário com id {id} não encontrado")
    
@router.put("/{id}", response_model=UsuarioOut, summary="Atualizar Usuário")
def update(id: str = Path(..., description="ID do usuário que deseja atualizar."),
           usuarioIn: UsuarioIn = Body(
               ...,
               description="Dados atualizados do usuário.",
               example={
                "nome": "Maciel Quental",
                "email": "enzoquental@btg.job.br",
                "senha": "teste"
                }
              ), db: ORM_Session = Depends(get_db)):
    """
    Atualiza os dados de um usuário específico.

    Parâmetros:
    - `id`: ID do usuário que deseja atualizar.
    - `usuarioIn`: Dados atualizados do usuário.
        Exemplo:
        ```
        ID: "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        Dados:
        {
            "nome": "Leo Barros",
            "email": "leobarros@btg.job.br",
            "senha": "teste"
        }
        """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
    if usuario:
        usuario.nome = usuarioIn.nome
        usuario.email = usuarioIn.email
        usuario.senha = usuarioIn.senha
        db.commit()
        db.refresh(usuario)
        return usuario
    raise HTTPException(404, detail=f"Usuário com id {id} não encontrado")
    
@router.delete("/{id}", summary="Deletar Usuário")
def delete(id: str = Path(..., description="ID do usuário que deseja deletar."), db: ORM_Session = Depends(get_db)):
    """
    Remove um usuário específico do sistema.

    Parâmetros:
    - `id`: ID do usuário que deseja deletar.
        Exemplo:
        ```
        "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        """
    usuario = db.query(Usuario).filter(Usuario.id_usuario == id).first()
    if usuario:
        db.delete(usuario)
        db.commit()
        return {"message": "Usuário removido"}
    raise HTTPException(404, detail=f"Usuário com id {id} não encontrado")
