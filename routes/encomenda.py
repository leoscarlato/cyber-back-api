from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime
from uuid import uuid4
from db import DB  

router = APIRouter(
    prefix="/encomenda",
    tags=["encomenda"]
)

status_template = ["Em Preparação", "Em Trânsito", "Entregue"]

class Encomenda(BaseModel):
    id_encomenda: str = Field(default_factory=lambda: str(uuid4()))
    valor_total: float = 0.0
    data_postagem: datetime = Field(default_factory=datetime.now)
    endereco_origem: str
    endereco_destino: str
    peso_total: float = 0.0
    status: Dict[datetime, str] = {datetime.now(): status_template[0]}
    item_ids: List[str]
    id_usuario_comprador: str
    id_usuario_vendedor: str


def calcular_valor_total(ids_produtos: List[str]) -> float:
    total = 0.0
    for produto_id in ids_produtos:
        produto = next((p for p in DB.produtos if p.id_produto == produto_id), None)
        if produto is not None:
            total += produto.preco
        else:
            raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")
    return total


def calcular_peso_total(ids_produtos: List[str]) -> float:
    total = 0.0
    for produto_id in ids_produtos:
        produto = next((p for p in DB.produtos if p.id_produto == produto_id), None)
        if produto is not None:
            total += produto.peso
        else:
            raise HTTPException(status_code=404, detail=f"Produto com ID {produto_id} não encontrado")
    return total


def valida_user(id_usuario_comprador, id_usuario_vendedor):
    comprador = next((u for u in DB.usuarios if u.id_usuario == id_usuario_comprador), None)
    vendedor = next((u for u in DB.usuarios if u.id_usuario == id_usuario_vendedor), None)
    if not comprador and not vendedor:
        raise HTTPException(status_code=404, detail=f"Usuario Comprador com id {id_usuario_comprador} e Usuario Vendedor com id {id_usuario_vendedor} não encontrados")
    if not comprador:
        raise HTTPException(status_code=404, detail=f"Usuario Comprador com id {id_usuario_comprador} não encontrado")
    if not vendedor:
        raise HTTPException(status_code=404, detail=f"Usuario Vendedor com id {id_usuario_vendedor} não encontrado")


@router.post("/", response_model=Encomenda)    
def create_encomenda(encomenda: Encomenda):

    """ Rota para criar uma nova encomenda """

    valida_user(encomenda.id_usuario_comprador, encomenda.id_usuario_vendedor)
    encomenda.valor_total = calcular_valor_total(encomenda.item_ids)
    encomenda.peso_total = calcular_peso_total(encomenda.item_ids)

    DB.encomendas.append(encomenda)  
    return encomenda


@router.get("/")
def get_encomendas():

    """ Rota para listar todas as encomendas """

    return DB.encomendas


@router.get("/{id}")
def get_encomenda(id: str):

    """ Rota para listar uma encomenda específica através do id """

    for e in DB.encomendas:
        if e.id_encomenda == id:
            return e
    return {"message": f"Encomenda com id {id} não encontrada"}


@router.put("/{id}")
def update_encomenda(id: str, encomenda: Encomenda):

    """ Rota para atualizar uma encomenda específica através do id """

    for e in DB.encomendas:
        if e.id_encomenda == id:
            valida_user(encomenda.id_usuario_comprador, encomenda.id_usuario_vendedor)
            e.valor_total = calcular_valor_total(encomenda.item_ids)
            e.peso_total = calcular_peso_total(encomenda.item_ids)
            e.endereco_origem = encomenda.endereco_origem
            e.endereco_destino = encomenda.endereco_destino
            e.status = encomenda.status
            e.item_ids = encomenda.item_ids
            e.id_usuario_comprador = encomenda.id_usuario_comprador
            e.id_usuario_vendedor = encomenda.id_usuario_vendedor
            return e
    return {"message": f"Encomenda com id {id} não encontrada"}


@router.delete("/{id}")
def delete_encomenda(id: str):

    """ Rota para deletar uma encomenda específica através do id """

    for i, e in enumerate(DB.encomendas):
        if e.id_encomenda == id:
            DB.encomendas.pop(i)
            return {"message": "Encomenda removida"}
    return {"message": f"Encomenda com id {id} não encontrada"}


@router.put("/{id}/status")
def update_status_encomenda(id: str):

    """ Rota para atualizar o status de uma encomenda específica através do id """

    for e in DB.encomendas:
        if e.id_encomenda == id:
            values = e.status.values()
            if status_template[2] in values:
                return {"message": "Encomenda já foi entregue"}
            elif status_template[1] in values:
                e.status[datetime.now()] = status_template[2]
            else:
                e.status[datetime.now()] = status_template[1]
                return e
            return e
    return {"message": f"Encomenda com id {id} não encontrada"}


@router.get("/{id}/status")
def get_status_encomenda(id: str):

    """ Rota para listar o status de uma encomenda específica através do id """
    
    for e in DB.encomendas:
        if e.id_encomenda == id:
            return e.status
    return {"message": f"Encomenda com id {id} não encontrada"}