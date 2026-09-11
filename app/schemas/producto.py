from enum import Enum

from pydantic import BaseModel, Field


class CategoriaProducto(str, Enum):
    BEBIDAS = "Bebidas"
    ABARROTES = "Abarrotes"
    SNACKS = "Snacks"
    LACTEOS = "Lacteos"
    ASEO = "Aseo"


class ProductoCreate(BaseModel):
    codigo: str = Field(
        ...,
        pattern=r"^[A-Za-z]{3}-\d{4}$",
        description=(
            "Codigo interno del producto. Tres letras, un guion y cuatro digitos. "
            "El servidor lo almacena siempre en mayusculas."
        ),
        examples=["BEB-0001"],
    )
    nombre: str = Field(
        ...,
        min_length=3,
        max_length=80,
        description="Nombre comercial del producto.",
        examples=["Gaseosa Postobon 1.5 L"],
    )
    categoria: CategoriaProducto = Field(
        ...,
        description="Linea a la que pertenece el producto dentro del catalogo.",
        examples=["Bebidas"],
    )
    precio: float = Field(
        ...,
        gt=0,
        description="Precio de venta en pesos colombianos. Debe ser mayor que cero.",
        examples=[4500],
    )
    stock: int = Field(
        ...,
        ge=0,
        description="Unidades existentes en bodega. Puede ser cero pero nunca negativo.",
        examples=[120],
    )


class ProductoResponse(BaseModel):
    id: int = Field(..., description="Identificador asignado por el servidor.", examples=[1])
    codigo: str = Field(..., examples=["BEB-0001"])
    nombre: str = Field(..., examples=["Gaseosa Postobon 1.5 L"])
    categoria: CategoriaProducto = Field(..., examples=["Bebidas"])
    precio: float = Field(..., examples=[4500])
    stock: int = Field(..., examples=[120])
    disponible: bool = Field(
        ...,
        description="Calculado por el servidor: es verdadero unicamente cuando el stock es mayor que cero.",
        examples=[True],
    )


class MensajeError(BaseModel):
    detail: str = Field(..., examples=["No existe un producto con el id 99"])
