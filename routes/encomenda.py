from fastapi import Depends, APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlalchemy import create_engine, Column, String
from datetime import datetime
from . import models
from .database import SessionLocal, engine
from sqlalchemy.orm import Session as ORM_Session
from typing import List
from . models import Produto, Encomenda, LocalizacaoOut, Localizacao
import requests
router = APIRouter(
    prefix="/encomenda",
    tags=["encomenda"]
)

class EncomendaOut(BaseModel):
    id_encomenda: str
    valor_total: float
    data_postagem: datetime
    endereco_origem: str
    endereco_destino: str
    peso_total: float
    id_usuario_comprador: str
    id_usuario_vendedor: str



class EncomendaIn(BaseModel):
    endereco_origem: str = Field(..., description="Endereço de origem da encomenda.")
    endereco_destino: str = Field(..., description="Endereço de destino da encomenda.")
    produto_ids: List[str] = Field(..., description="IDs dos produtos na encomenda.")
    id_usuario_comprador: str = Field(..., description="ID do usuário comprador.")
    id_usuario_vendedor: str = Field(..., description="ID do usuário vendedor.")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends, APIRouter, HTTPException, Path, Body
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlalchemy.orm import Session as ORM_Session
from sqlalchemy.exc import IntegrityError

from . import models
from .database import SessionLocal
from .models import Encomenda

router = APIRouter(
    prefix="/encomenda",
    tags=["encomenda"]
)



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EncomendaOut, summary="Criar Encomenda")    
def create_encomenda(encomendaIn: EncomendaIn = Body(
        ...,
        description="Dados da encomenda a serem criados.",
        example={
            "endereco_origem": "Rua casa do ator 99",
            "endereco_destino": "Rua casa do ator 100",
            "produto_ids": ["4956c5f1-31ec-4eb4-b417-90753e7bb6fd"],
            "id_usuario_comprador": "b2a53b2a-5151-4ef7-ae94-c4992dd119ef",
            "id_usuario_vendedor": "13cc3687-050a-4e0f-8f46-3fe63aa6e5db"
        }
    ), db: ORM_Session = Depends(get_db)):
    try:

        encomenda = Encomenda(
            endereco_origem=encomendaIn.endereco_origem,
            endereco_destino=encomendaIn.endereco_destino,
            id_usuario_comprador=encomendaIn.id_usuario_comprador,
            id_usuario_vendedor=encomendaIn.id_usuario_vendedor
        )
        
        valor_total = 0
        peso_total = 0
        for produto_id in encomendaIn.produto_ids:
            produto = db.query(Produto).filter(Produto.id_produto == produto_id).first()
            if produto:
                valor_total += produto.preco
                peso_total += produto.peso
                encomenda.produtos.append(produto)
            else:
                raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")
        
        encomenda.valor_total = valor_total
        encomenda.peso_total = peso_total
        db.add(encomenda)
        db.commit()
        db.refresh(encomenda)
        
        requests.post("http://localhost:8000/localizacao", json={"endereco": encomenda.endereco_origem, "id_encomenda": encomenda.id_encomenda})

        return EncomendaOut(
            id_encomenda=encomenda.id_encomenda,
            valor_total=encomenda.valor_total,
            data_postagem=encomenda.data_postagem,
            endereco_origem=encomenda.endereco_origem,
            endereco_destino=encomenda.endereco_destino,
            peso_total=encomenda.peso_total,
            id_usuario_comprador=encomenda.id_usuario_comprador,
            id_usuario_vendedor=encomenda.id_usuario_vendedor,
            produto_ids=[produto.id_produto for produto in encomenda.produtos]
        )
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao criar encomenda: {}".format(e))

@router.get("/", summary="Listar Todas as Encomendas")
def get_encomendas(db: ORM_Session = Depends(get_db)):
    return db.query(Encomenda).all()

@router.get("/{id}", summary="Obter Encomenda")
def get_encomenda(id: str = Path(..., description="ID da encomenda que deseja obter."), db: ORM_Session = Depends(get_db)):
    encomenda = db.query(Encomenda).filter(Encomenda.id_encomenda == id).first()
    if encomenda:
        return encomenda
    raise HTTPException(status_code=404, detail=f"Encomenda com id {id} não encontrada")

@router.put("/{id}", response_model=EncomendaOut, summary="Atualizar Encomenda")
def update_encomenda(id: str = Path(..., description="ID da encomenda que deseja atualizar."),
                     encomendaIn: EncomendaIn = Body(
                         ...,
                         description="Dados atualizados da encomenda.",
                         example={
                             "endereco_origem": "Rua casa do ator 99",
                             "endereco_destino": "Rua casa do ator 100",
                             "produto_ids": ["4956c5f1-31ec-4eb4-b417-90753e7bb6fd"],
                             "id_usuario_comprador": "b2a53b2a-5151-4ef7-ae94-c4992dd119ef",
                             "id_usuario_vendedor": "13cc3687-050a-4e0f-8f46-3fe63aa6e5db"
                         }
                     ), db: ORM_Session = Depends(get_db)):
    encomenda = db.query(Encomenda).filter(Encomenda.id_encomenda == id).first()
    if encomenda:
        try:
            # Update basic attributes
            encomenda.endereco_origem = encomendaIn.endereco_origem
            encomenda.endereco_destino = encomendaIn.endereco_destino
            encomenda.id_usuario_comprador = encomendaIn.id_usuario_comprador
            encomenda.id_usuario_vendedor = encomendaIn.id_usuario_vendedor

            # Update associated products
            encomenda.produtos.clear()  # Clear existing products
            valor_total = 0
            peso_total = 0
            for produto_id in encomendaIn.produto_ids:
                produto = db.query(Produto).filter(Produto.id_produto == produto_id).first()
                if produto:
                    valor_total += produto.preco
                    peso_total += produto.peso
                    encomenda.produtos.append(produto)
                else:
                    raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")
            
            encomenda.valor_total = valor_total
            encomenda.peso_total = peso_total
            
            db.commit()
            db.refresh(encomenda)
            
            return EncomendaOut(
                id_encomenda=encomenda.id_encomenda,
                valor_total=encomenda.valor_total,
                data_postagem=encomenda.data_postagem,
                endereco_origem=encomenda.endereco_origem,
                endereco_destino=encomenda.endereco_destino,
                peso_total=encomenda.peso_total,
                id_usuario_comprador=encomenda.id_usuario_comprador,
                id_usuario_vendedor=encomenda.id_usuario_vendedor,
                produto_ids=[produto.id_produto for produto in encomenda.produtos]
            )
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=400, detail="Erro ao atualizar encomenda: {}".format(e))
    raise HTTPException(status_code=404, detail=f"Encomenda com id {id} não encontrada")


@router.delete("/{id}", summary="Deletar Encomenda")
def delete_encomenda(id: str = Path(..., description="ID da encomenda que deseja deletar."), db: ORM_Session = Depends(get_db)):
    encomenda = db.query(Encomenda).filter(Encomenda.id_encomenda == id).first()
    if encomenda:
        db.delete(encomenda)
        db.commit()
        return {"message": "Encomenda removida"}
    raise HTTPException(status_code=404, detail=f"Encomenda com id {id} não encontrada")

@router.get("/{id}/localizacao", response_model=List[LocalizacaoOut], summary="Obter histórico de Localização da Encomenda")
def get_status_encomenda(id: str = Path(..., description="ID da encomenda que deseja obter o histórico de localização."), db: ORM_Session = Depends(get_db)):
    """"
    Obtém o histórico de localização de uma encomenda específica.
    
    Parâmetros:
    - `id`: ID da encomenda que deseja obter o histórico de localização.
        Exemplo:
        ```
        "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        ```

    """
    localizacoes = db.query(Localizacao).filter(Localizacao.id_encomenda == id).all()
    return localizacoes

