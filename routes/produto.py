from fastapi import Depends, APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlalchemy import create_engine, Column, String

from . import models
from . models import Produto, ProdutoOut
from .database import SessionLocal, engine
from sqlalchemy.orm import Session as ORM_Session

models.Base.metadata.create_all(bind=engine)

router = APIRouter(
    prefix="/produto",
    tags=["produto"]
)

class ProdutoIn(BaseModel):
    nome: str = Field(..., description="Nome do produto.")
    peso: float = Field(..., description="Peso do produto.")
    preco: float = Field(..., description="Preço do produto.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ProdutoOut, summary="Criar Produto")
def create(produto_in: ProdutoIn = Body(
        ...,
        description="Dados do produto a serem criados.",
        example={
            "nome": "Camisa Coxa",
            "peso": 100,
            "preco": 199.99
        }
    ), db: ORM_Session = Depends(get_db)):
    """
    Cria um novo produto com os dados fornecidos.

    Parâmetros:
    - `produtoIn`: Dados do produto a serem criados.
        Exemplo:
        ```
        {
            "nome": "Camisa Coxa",
            "peso": 100,
            "preco": 199.99
        }
        ```
    """
    produto = Produto(
        nome=produto_in.nome,
        peso=produto_in.peso,
        preco=produto_in.preco,
        id_produto=str(uuid4())
    )
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return ProdutoOut.from_orm(produto) 

@router.get("/", summary="Listar Produtos")
def get_all(db: ORM_Session = Depends(get_db)):
    """
    Lista todos os produtos cadastrados no sistema.
    """
    return db.query(Produto).all()
    

@router.get("/{id}", response_model=ProdutoOut, summary="Obter Produto")
def get_produto(id_produto: str, db: ORM_Session = Depends(get_db)):
    """
    Obtém os detalhes de um produto específico.

    Parâmetros:
    - `id`: ID do produto que deseja obter.
        Exemplo:
        ```
        "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        ```
    """
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if produto:
        return ProdutoOut.from_orm(produto)  # Conversão para Pydantic.
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@router.put("/{id}", response_model=ProdutoOut, summary="Atualizar Produto")
def update(id: str = Path(..., description="ID do produto que deseja atualizar."),
           produtoIn: ProdutoIn = Body(
               ...,
               description="Dados atualizados do produto.",
               example={
                   "nome": "Novo Nome",
                   "peso": 2.0,
                   "preco": 150.0
               }
           ), db: ORM_Session = Depends(get_db)):
    """
    Atualiza os dados de um produto específico.

    Parâmetros:
    - `id`: ID do produto que deseja atualizar.
    - `produtoIn`: Dados atualizados do produto.
        Exemplo:
        ```
        ID: "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        Dados:
        {
            "nome": "Camisa Coxa Doido",
            "peso": 200,
            "preco": 399.99
        }
        ```
    """
    produto = db.query(Produto).filter(Produto.id_produto == id).first()
    if not produto:
        raise HTTPException(404, detail=f"Produto com id {id} não encontrado")
    produto.nome = produtoIn.nome
    produto.peso = produtoIn.peso
    produto.preco = produtoIn.preco
    db.commit()
    db.refresh(produto)
    return ProdutoOut.from_orm(produto)

@router.delete("/{id}", summary="Deletar Produto")
def delete(id: str = Path(..., description="ID do produto que deseja deletar."), db: ORM_Session = Depends(get_db)):
    """
    Remove um produto específico do sistema.

    Parâmetros:
    - `id`: ID do produto que deseja deletar.
        Exemplo:
        ```
        "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        """
    produto = db.query(Produto).filter(Produto.id_produto == id).first()
    if not produto:
        raise HTTPException(404, detail=f"Produto com id {id} não encontrado")
    db.delete(produto)
    db.commit()
    return {"message": "Produto deletado com sucesso"}
