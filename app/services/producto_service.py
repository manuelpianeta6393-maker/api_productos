from fastapi import HTTPException

from app.schemas.producto import CategoriaProducto, ProductoCreate

_productos: list[dict] = []
_siguiente_id = 1


def _normalizar(texto: str) -> str:
    return " ".join(texto.split()).lower()


def _buscar_por_codigo(codigo: str, excluir_id: int | None = None) -> dict | None:
    objetivo = codigo.strip().upper()
    for producto in _productos:
        if producto["id"] != excluir_id and producto["codigo"] == objetivo:
            return producto
    return None


def _buscar_por_nombre(nombre: str, excluir_id: int | None = None) -> dict | None:
    objetivo = _normalizar(nombre)
    for producto in _productos:
        if producto["id"] != excluir_id and _normalizar(producto["nombre"]) == objetivo:
            return producto
    return None


def _validar_reglas_de_negocio(datos: ProductoCreate, excluir_id: int | None = None) -> None:
    repetido = _buscar_por_codigo(datos.codigo, excluir_id)
    if repetido is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"El codigo {repetido['codigo']} ya esta asignado al producto "
                f"{repetido['nombre']} (id {repetido['id']})"
            ),
        )

    repetido = _buscar_por_nombre(datos.nombre, excluir_id)
    if repetido is not None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Ya existe un producto registrado con el nombre {repetido['nombre']} "
                f"(id {repetido['id']})"
            ),
        )


def _armar_producto(producto_id: int, datos: ProductoCreate) -> dict:
    return {
        "id": producto_id,
        "codigo": datos.codigo.strip().upper(),
        "nombre": datos.nombre.strip(),
        "categoria": datos.categoria,
        "precio": datos.precio,
        "stock": datos.stock,
        "disponible": datos.stock > 0,
    }


def listar_productos(categoria: CategoriaProducto | None = None) -> list[dict]:
    if categoria is None:
        return _productos

    return [producto for producto in _productos if producto["categoria"] == categoria]


def obtener_producto(producto_id: int) -> dict:
    for producto in _productos:
        if producto["id"] == producto_id:
            return producto

    raise HTTPException(
        status_code=404,
        detail=f"No existe un producto con el id {producto_id}",
    )


def crear_producto(datos: ProductoCreate) -> dict:
    global _siguiente_id

    _validar_reglas_de_negocio(datos)

    nuevo = _armar_producto(_siguiente_id, datos)
    _productos.append(nuevo)
    _siguiente_id += 1

    return nuevo


def actualizar_producto(producto_id: int, datos: ProductoCreate) -> dict:
    actual = obtener_producto(producto_id)

    _validar_reglas_de_negocio(datos, excluir_id=producto_id)

    actual.update(_armar_producto(producto_id, datos))

    return actual


def eliminar_producto(producto_id: int) -> dict:
    producto = obtener_producto(producto_id)
    _productos.remove(producto)

    return producto
