from fastapi import APIRouter, Path, Query, status

from app.schemas.producto import (
    CategoriaProducto,
    MensajeError,
    ProductoCreate,
    ProductoResponse,
)
from app.services.producto_service import (
    actualizar_producto,
    crear_producto,
    eliminar_producto,
    listar_productos,
    obtener_producto,
)

router = APIRouter(prefix="/productos", tags=["Productos"])

ID_PRODUCTO = Path(..., ge=1, description="Identificador del producto.", examples=[1])


@router.get(
    "/",
    response_model=list[ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los productos",
    description=(
        "Devuelve el catalogo completo de productos registrados. "
        "Si se envia el parametro categoria, la lista se filtra por esa linea. "
        "Cuando no hay productos se devuelve una lista vacia, no un error."
    ),
)
def get_productos(
    categoria: CategoriaProducto | None = Query(
        default=None,
        description="Filtra el catalogo por linea de producto.",
    ),
):
    return listar_productos(categoria)


@router.get(
    "/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Consultar un producto por su id",
    description="Busca un unico producto a partir de su identificador.",
    responses={404: {"model": MensajeError, "description": "El producto no existe"}},
)
def get_producto(producto_id: int = ID_PRODUCTO):
    return obtener_producto(producto_id)


@router.post(
    "/",
    response_model=ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un producto nuevo",
    description=(
        "Crea un producto en el catalogo. El servidor asigna el id de forma automatica "
        "y calcula el campo disponible a partir del stock recibido. "
        "El codigo y el nombre no pueden repetirse."
    ),
    responses={400: {"model": MensajeError, "description": "Codigo o nombre ya registrado"}},
)
def post_producto(datos: ProductoCreate):
    return crear_producto(datos)


@router.put(
    "/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un producto existente",
    description=(
        "Reemplaza los datos de un producto conservando su id. "
        "El codigo y el nombre pueden mantenerse iguales, pero no pueden coincidir "
        "con los de otro producto del catalogo."
    ),
    responses={
        400: {"model": MensajeError, "description": "Codigo o nombre de otro producto"},
        404: {"model": MensajeError, "description": "El producto no existe"},
    },
)
def put_producto(datos: ProductoCreate, producto_id: int = ID_PRODUCTO):
    return actualizar_producto(producto_id, datos)


@router.delete(
    "/{producto_id}",
    response_model=ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar un producto",
    description=(
        "Retira un producto del catalogo y devuelve el registro eliminado "
        "como confirmacion de lo que se borro."
    ),
    responses={404: {"model": MensajeError, "description": "El producto no existe"}},
)
def delete_producto(producto_id: int = ID_PRODUCTO):
    return eliminar_producto(producto_id)
