from fastapi import FastAPI
from routes import encomenda ,produto, usuario, localizacao



app = FastAPI()


app.include_router(encomenda.router)
app.include_router(localizacao.router)
app.include_router(produto.router)
app.include_router(usuario.router)

