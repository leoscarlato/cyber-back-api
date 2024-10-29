from fastapi import Depends, APIRouter, HTTPException, Path, Body
from pydantic import Field
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from .models import Localizacao


router = APIRouter(
    prefix="/localizacao",
    tags=["localizacao"]
)

class LocalizacaoIn(BaseModel):
    endereco: str = Field(..., description="Endereço da localização.")
    id_encomenda: str = Field(..., description="ID da encomenda associada à localização.")


class LocalizacaoOut(BaseModel):
    id_localizacao: str = Field(default_factory=lambda: str(uuid4()), description="ID único da localização.")
    data: datetime = Field(default_factory=datetime.now, description="Data da localização.")
    endereco: str = Field(..., description="Endereço da localização.")
    id_encomenda: str = Field(..., description="ID da encomenda associada à localização.")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=LocalizacaoOut, summary="Criar Localização")
def create(localizacaoIn: LocalizacaoIn = Body(
        ...,
        description="Dados da localização a serem criados.",
        example={
            "endereco": "Rua Casa do Ator, 123",
            "id_encomenda": "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        }
    ), db: Session = Depends(get_db)):
    """
    Cria uma nova localização com os dados fornecidos.

    Parâmetros:
    - `localizacaoIn`: Dados da localização a serem criados.
        Exemplo:
        ```
        {
            "endereco": "Rua Casa do Ator, 123",
            "id_encomenda": "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        }
        ```
    """
    # encomenda = db.query(models.Encomenda).filter(models.Encomenda.id_encomenda == localizacaoIn.id_encomenda).first()
    # if not encomenda:
    #     raise HTTPException(status_code=404, detail=f"Encomenda com id {localizacaoIn.id_encomenda} não encontrada")

    localizacao = models.Localizacao(**localizacaoIn.dict())
    db.add(localizacao)
    db.commit()
    db.refresh(localizacao)
    return localizacao

@router.get("/", summary="Listar Todas as Localizações")
def get_all(db: Session = Depends(get_db)):
    """
    Lista todas as localizações cadastradas.
    """
    return db.query(models.Localizacao).all()

@router.get("/{id}", response_model=LocalizacaoOut, summary="Obter Localização")
def get_unique(id: str = Path(..., description="ID da localização que deseja obter."), db: Session = Depends(get_db)):
    """
    Obtém os detalhes de uma localização específica.

    Parâmetros:
    - `id`: ID da localização que deseja obter.
        Exemplo:
        ```
        "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        ```
    """
    localizacao = db.query(Localizacao).filter(Localizacao.id_localizacao == id).first()
    if localizacao:
        return localizacao
    raise HTTPException(404, detail=f"Localização com id {id} não encontrada")

@router.put("/{id}", response_model=LocalizacaoOut, summary="Atualizar Localização")
def update(id: str = Path(..., description="ID da localização que deseja atualizar."),
           localizacaoIn: LocalizacaoIn = Body(
               ...,
               description="Dados atualizados da localização.",
               example={
                   "endereco": "Rua Casa do Ator, 123",
                   "id_encomenda": "7ee85363-1c9d-4bf8-afd6-645aad61539f"
               }
           ), db: Session = Depends(get_db)):
    """
    Atualiza os dados de uma localização específica.

    Parâmetros:
    - `id`: ID da localização que deseja atualizar.
    - `localizacaoIn`: Dados atualizados da localização.
        Exemplo:
        ```
        ID: "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        Dados:
        {
            "endereco": "Rua Casa do Ator, 123",
            "id_encomenda": "7ee85363-1c9d-4bf8-afd6-645aad61539f"
        }
        """
    localizacao = db.query(models.Localizacao).filter(models.Localizacao.id_localizacao == id).first()
    if not localizacao:
        raise HTTPException(404, detail=f"Localização com id {id} não encontrada")

    localizacao.endereco = localizacaoIn.endereco
    localizacao.id_encomenda = localizacaoIn.id_encomenda
    db.commit()
    db.refresh(localizacao)
    return localizacao

@router.delete("/{id}", summary="Deletar Localização")
def delete(id: str = Path(..., description="ID da localização que deseja deletar."), db: Session = Depends(get_db)):
    """
    Remove uma localização específica do sistema.

    Parâmetros:
    - `id`: ID da localização que deseja deletar.
        Exemplo:
        ```
        "b2a53b2a-5151-4ef7-ae94-c4992dd119ef"
        """
    localizacao = db.query(Localizacao).filter(Localizacao.id_localizacao == id).first()
    if not localizacao:
        raise HTTPException(404, detail=f"Localização com id {id} não encontrada")

    db.delete(localizacao)
    db.commit()
    return {"message": "Localização removida"}
