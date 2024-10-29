from sqlalchemy import Table, Column, String, Float, DateTime, ForeignKey
from pydantic import BaseModel, Field
from sqlalchemy.orm import relationship
from uuid import uuid4
from pydantic import BaseModel
from datetime import datetime

import datetime
import uuid
from .database import Base

encomenda_produto_association = Table('encomenda_produto', Base.metadata,
    Column('encomenda_id', String(36), ForeignKey('encomendas.id_encomenda', ondelete="CASCADE")),
    Column('produto_id', String(36), ForeignKey('produtos.id_produto', ondelete="CASCADE"))
)
class Encomenda(Base):
    __tablename__ = 'encomendas'

    id_encomenda = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    valor_total = Column(Float, default=0.0)
    data_postagem = Column(DateTime, default=datetime.datetime.now)
    endereco_origem = Column(String(36))
    endereco_destino = Column(String(36))
    peso_total = Column(Float, default=0.0)
    
    id_usuario_comprador = Column(String(36), ForeignKey('usuarios.id_usuario'))
    id_usuario_vendedor = Column(String(36), ForeignKey('usuarios.id_usuario'))

    comprador = relationship("Usuario", foreign_keys=[id_usuario_comprador])
    vendedor = relationship("Usuario", foreign_keys=[id_usuario_vendedor])

    produtos = relationship("Produto", secondary=encomenda_produto_association, backref="encomendas")



class Produto(Base):
    __tablename__ = 'produtos'

    id_produto = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String(36))
    peso = Column(Float)
    preco = Column(Float)

class Localizacao(Base):
    __tablename__ = 'localizacoes'
    id_localizacao = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    data = Column(DateTime, default=datetime.datetime.now)
    endereco = Column(String(36))
    
    id_encomenda = Column(String(36), ForeignKey('encomendas.id_encomenda'))

class ProdutoOut(BaseModel):
    id_produto: str
    nome: str
    peso: float
    preco: float

    class Config:
        from_attributes = True


class LocalizacaoOut(BaseModel):
    id_localizacao: str = Field(default_factory=lambda: str(uuid4()), description="ID único da localização.")
    data: datetime = Field(default_factory=datetime.datetime.now, description="Data da localização.")
    endereco: str = Field(..., description="Endereço da localização.")
    id_encomenda: str = Field(..., description="ID da encomenda associada à localização.")

    class Config:
        arbitrary_types_allowed = True


class Usuario(Base):
    __tablename__ = 'usuarios'

    id_usuario = Column(String(36), primary_key=True)
    nome = Column(String(36))
    email = Column(String(36))
    senha = Column(String(36))

