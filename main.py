from fastapi import FastAPI
from routes import encomenda, produto, usuario

app = FastAPI()
app.include_router(encomenda.router)
app.include_router(produto.router)
app.include_router(usuario.router)

@app.get("/")
def home():
    return {"message": "Bem vindo a API de encomendas"}