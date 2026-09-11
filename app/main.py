from fastapi import FastAPI

from app.routers.producto import router as productos_router

app = FastAPI(
    title="API de Productos",
    description=(
        "API REST para administrar el catalogo de productos de una distribuidora "
        "de bebidas y abarrotes. Implementa un CRUD completo sobre el recurso producto, "
        "con arquitectura por capas, validaciones con Pydantic y reglas de negocio "
        "aplicadas en la capa de servicios. Los datos se almacenan en memoria."
    ),
    version="1.0.0",
    contact={"name": "Manuel Julian Pianeta Calvo"},
)

app.include_router(productos_router)
