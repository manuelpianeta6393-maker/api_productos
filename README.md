# API de Productos

API REST construida con FastAPI para administrar el catálogo de productos de una
distribuidora de bebidas y abarrotes. Implementa un CRUD completo sobre el recurso
**producto**, con arquitectura por capas, validaciones declaradas con Pydantic y reglas de
negocio aplicadas en la capa de servicios.

---

## 1. Nombre del proyecto

**API de Productos — Distribuidora de bebidas y abarrotes**

## 2. Descripción de la API

La API permite registrar, consultar, listar, actualizar y eliminar los productos que maneja
una distribuidora. Cada producto tiene un código interno único, un nombre comercial, una
categoría tomada de una lista cerrada, un precio de venta y una cantidad en bodega.

La API no se limita a guardar lo que le mandan: valida el formato de los datos antes de
procesarlos, impide registrar productos repetidos y calcula por su cuenta si un producto
está disponible para la venta. Cuando algo sale mal responde con un código HTTP adecuado y
un mensaje que explica qué ocurrió, en lugar de fallar sin explicación.

Los datos se almacenan **en memoria**, en una lista de diccionarios. No se utiliza base de
datos, por lo que la información se reinicia cada vez que se detiene el servidor.

## 3. Recurso seleccionado

El recurso principal es `producto`, expuesto en la ruta `/productos`.

## 4. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.10 o superior | Lenguaje base |
| FastAPI | Framework para construir la API REST |
| Pydantic v2 | Definición y validación de los modelos de datos |
| Uvicorn | Servidor ASGI que ejecuta la aplicación |
| Swagger UI | Documentación interactiva generada automáticamente |

## 5. Estructura de carpetas

```
api_productos/
├── app/
│   ├── __init__.py
│   ├── main.py                      Crea la aplicación y registra los routers
│   ├── routers/
│   │   ├── __init__.py
│   │   └── producto.py              Endpoints HTTP del recurso producto
│   ├── services/
│   │   ├── __init__.py
│   │   └── producto_service.py      Lógica del programa y reglas de negocio
│   └── schemas/
│       ├── __init__.py
│       └── producto.py              Modelos Pydantic de entrada y salida
├── requirements.txt
├── .gitignore
└── README.md
```

Cada capa tiene una responsabilidad distinta:

- **`main.py`** crea la instancia de FastAPI con su título y descripción, y registra el
  router de productos.
- **`routers/`** contiene únicamente las rutas. Cada función recibe la petición, llama al
  servicio correspondiente y devuelve el resultado. No contiene lógica de negocio.
- **`services/`** contiene la lógica del programa: buscar, crear, actualizar, eliminar,
  comprobar duplicados y aplicar las reglas de negocio. Es el único lugar donde se toca la
  lista de productos.
- **`schemas/`** contiene los modelos Pydantic que definen y validan lo que la API recibe y
  lo que devuelve.

## 6. Modelo del recurso

Un producto almacenado tiene la siguiente forma:

```json
{
  "id": 1,
  "codigo": "BEB-0001",
  "nombre": "Gaseosa Postobon 1.5 L",
  "categoria": "Bebidas",
  "precio": 4500.0,
  "stock": 120,
  "disponible": true
}
```

| Campo | Tipo | Origen | Validación |
|---|---|---|---|
| `id` | entero | Asignado por el servidor | No se envía en las peticiones |
| `codigo` | texto | Enviado por el cliente | Patrón `^[A-Za-z]{3}-\d{4}$`, se guarda en mayúsculas |
| `nombre` | texto | Enviado por el cliente | Entre 3 y 80 caracteres |
| `categoria` | texto | Enviado por el cliente | Solo uno de: `Bebidas`, `Abarrotes`, `Snacks`, `Lacteos`, `Aseo` |
| `precio` | decimal | Enviado por el cliente | Mayor que cero |
| `stock` | entero | Enviado por el cliente | Mayor o igual que cero |
| `disponible` | booleano | **Calculado por el servidor** | Es `true` únicamente cuando `stock > 0` |

### Modelos definidos en `schemas/producto.py`

- **`CategoriaProducto`**: enumeración con las cinco categorías válidas del catálogo.
- **`ProductoCreate`**: modelo de **entrada**. Contiene `codigo`, `nombre`, `categoria`,
  `precio` y `stock`. No incluye `id` ni `disponible`, porque esos dos campos no los decide
  el cliente. Se usa tanto en el `POST` como en el `PUT`.
- **`ProductoResponse`**: modelo de **salida**. Contiene los siete campos del producto. Al
  declararlo como `response_model`, FastAPI filtra la respuesta a exactamente esos campos.
- **`MensajeError`**: modelo del cuerpo de los errores (`{"detail": "..."}`). Se declara en
  el parámetro `responses` de cada endpoint para que Swagger documente los códigos 400 y 404
  en lugar de mostrarlos como respuestas no documentadas.

## 7. Endpoints disponibles

| Método | Endpoint | Recibe | Devuelve | Éxito | Posibles errores |
|---|---|---|---|---|---|
| GET | `/productos/` | Parámetro opcional `categoria` | Lista de productos | 200 | 422 |
| GET | `/productos/{producto_id}` | ID en la ruta | Objeto | 200 | 404, 422 |
| POST | `/productos/` | JSON | Objeto creado | 201 | 400, 422 |
| PUT | `/productos/{producto_id}` | ID + JSON | Objeto actualizado | 200 | 400, 404, 422 |
| DELETE | `/productos/{producto_id}` | ID en la ruta | Objeto eliminado | 200 | 404, 422 |

## 8. Contratos de los endpoints

### 8.1. GET `/productos/`

- **Método HTTP:** GET
- **Ruta:** `/productos/`
- **Propósito:** listar todos los productos del catálogo, con la opción de filtrarlos por
  categoría.
- **Datos de entrada:** ninguno en el cuerpo. Acepta el parámetro de consulta opcional
  `categoria`, que debe ser una de las cinco categorías válidas.

Ejemplo de llamada con filtro:

```
GET /productos/?categoria=Bebidas
```

- **Respuesta exitosa:**

```json
[
  {
    "id": 1,
    "codigo": "BEB-0001",
    "nombre": "Gaseosa Postobon 1.5 L",
    "categoria": "Bebidas",
    "precio": 4500.0,
    "stock": 120,
    "disponible": true
  }
]
```

- **Código HTTP exitoso:** `200 OK`
- **Posibles errores:** `422 Unprocessable Entity` si el valor de `categoria` no pertenece a
  la enumeración.
- **Nota:** si no hay productos registrados devuelve una lista vacía `[]` con código 200. Una
  lista vacía no es un error.

### 8.2. GET `/productos/{producto_id}`

- **Método HTTP:** GET
- **Ruta:** `/productos/{producto_id}`
- **Propósito:** consultar un único producto a partir de su identificador.
- **Datos de entrada:** `producto_id`, entero mayor o igual que 1, en la ruta.
- **Respuesta exitosa:**

```json
{
  "id": 1,
  "codigo": "BEB-0001",
  "nombre": "Gaseosa Postobon 1.5 L",
  "categoria": "Bebidas",
  "precio": 4500.0,
  "stock": 120,
  "disponible": true
}
```

- **Código HTTP exitoso:** `200 OK`
- **Posibles errores:**
  - `404 Not Found` — el id no corresponde a ningún producto:

    ```json
    { "detail": "No existe un producto con el id 99" }
    ```

  - `422 Unprocessable Entity` — el id no es un entero válido.

### 8.3. POST `/productos/`

- **Método HTTP:** POST
- **Ruta:** `/productos/`
- **Propósito:** registrar un producto nuevo en el catálogo.
- **Datos de entrada:**

```json
{
  "codigo": "BEB-0001",
  "nombre": "Gaseosa Postobon 1.5 L",
  "categoria": "Bebidas",
  "precio": 4500,
  "stock": 120
}
```

- **Respuesta exitosa:**

```json
{
  "id": 1,
  "codigo": "BEB-0001",
  "nombre": "Gaseosa Postobon 1.5 L",
  "categoria": "Bebidas",
  "precio": 4500.0,
  "stock": 120,
  "disponible": true
}
```

- **Código HTTP exitoso:** `201 Created`
- **Posibles errores:**
  - `400 Bad Request` — el código ya está asignado a otro producto:

    ```json
    { "detail": "El codigo BEB-0001 ya esta asignado al producto Gaseosa Postobon 1.5 L (id 1)" }
    ```

  - `400 Bad Request` — el nombre ya existe en el catálogo:

    ```json
    { "detail": "Ya existe un producto registrado con el nombre Gaseosa Postobon 1.5 L (id 1)" }
    ```

  - `422 Unprocessable Entity` — los datos no cumplen las validaciones (código con formato
    incorrecto, nombre de menos de 3 caracteres, precio menor o igual que cero, stock
    negativo, o categoría fuera de la lista).

### 8.4. PUT `/productos/{producto_id}`

- **Método HTTP:** PUT
- **Ruta:** `/productos/{producto_id}`
- **Propósito:** reemplazar los datos de un producto existente, conservando su id.
- **Datos de entrada:** `producto_id` en la ruta y, en el cuerpo, el mismo modelo del POST:

```json
{
  "codigo": "BEB-0001",
  "nombre": "Gaseosa Postobon 2.0 L",
  "categoria": "Bebidas",
  "precio": 5200,
  "stock": 95
}
```

- **Respuesta exitosa:**

```json
{
  "id": 1,
  "codigo": "BEB-0001",
  "nombre": "Gaseosa Postobon 2.0 L",
  "categoria": "Bebidas",
  "precio": 5200.0,
  "stock": 95,
  "disponible": true
}
```

- **Código HTTP exitoso:** `200 OK`
- **Posibles errores:**
  - `404 Not Found` — el id no existe.
  - `400 Bad Request` — el código o el nombre enviados pertenecen a **otro** producto. El
    producto que se está editando queda excluido de esa comprobación, de modo que sí puede
    conservar su propio código y su propio nombre mientras se le cambia el precio o el stock.
  - `422 Unprocessable Entity` — los datos no cumplen las validaciones.
- **Nota:** el campo `disponible` se recalcula en cada actualización. Si el stock pasa a
  cero, `disponible` queda en `false` automáticamente.

### 8.5. DELETE `/productos/{producto_id}`

- **Método HTTP:** DELETE
- **Ruta:** `/productos/{producto_id}`
- **Propósito:** eliminar un producto del catálogo.
- **Datos de entrada:** `producto_id` en la ruta. No lleva cuerpo.
- **Respuesta exitosa:** el producto eliminado, como confirmación de qué se borró.

```json
{
  "id": 3,
  "codigo": "LAC-0012",
  "nombre": "Leche Klarens 1 L",
  "categoria": "Lacteos",
  "precio": 3800.0,
  "stock": 0,
  "disponible": false
}
```

- **Código HTTP exitoso:** `200 OK`
- **Posibles errores:**
  - `404 Not Found` — el id no existe, o el producto ya fue eliminado antes.
  - `422 Unprocessable Entity` — el id no es un entero válido.

## 9. Reglas de negocio implementadas

Las cinco reglas viven en `services/producto_service.py`, nunca dentro de los endpoints.

1. **Código único.** No pueden existir dos productos con el mismo código. La comparación se
   hace sobre el código normalizado a mayúsculas, de modo que `beb-0001` y `BEB-0001` se
   consideran el mismo código. Violarla produce un `400`.

2. **Nombre único.** No pueden existir dos productos con el mismo nombre comercial. La
   comparación ignora mayúsculas y colapsa los espacios repetidos, así que
   `"Arroz  Diana 500 g"` y `"arroz diana 500 g"` se consideran el mismo nombre. Violarla
   produce un `400`.

3. **Exclusión del propio producto al actualizar.** Las dos reglas anteriores excluyen el
   producto que se está editando. Sin esa exclusión sería imposible modificar el precio de un
   producto sin cambiarle también el nombre, porque él mismo aparecería en la lista como un
   duplicado de sí mismo.

4. **Disponibilidad derivada del stock.** El campo `disponible` no lo envía el cliente: lo
   calcula el servidor con la expresión `stock > 0`, tanto al crear como al actualizar. Esto
   evita que el catálogo quede en un estado incoherente, como un producto marcado disponible
   con cero unidades en bodega.

5. **Normalización de los datos guardados.** El código se almacena siempre en mayúsculas y al
   nombre se le recortan los espacios sobrantes de los extremos, de manera que el catálogo
   quede uniforme sin importar cómo se haya escrito la petición.

Además, las validaciones de formato se aplican antes de que la petición llegue a la lógica,
porque están declaradas en el modelo `ProductoCreate`: patrón del código, longitud del
nombre, categoría dentro de la enumeración, precio mayor que cero y stock no negativo. Si
alguna falla, FastAPI responde `422` y la función del servicio no llega a ejecutarse.

## 10. Instrucciones para instalar las dependencias

Clonar el repositorio y situarse en la carpeta del proyecto:

```bash
git clone https://github.com/manuelpianeta6393-maker/api_productos.git
cd api_productos
```

Crear un entorno virtual e instalar las dependencias.

En Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 11. Instrucciones para ejecutar la API

Desde la carpeta raíz del proyecto, la que contiene `requirements.txt`:

```bash
uvicorn app.main:app --reload
```

La consola mostrará:

```
Uvicorn running on http://127.0.0.1:8000
```

Para detener el servidor se presiona `Ctrl + C`.

> Los datos se guardan en memoria. Cada vez que se reinicia el servidor el catálogo vuelve a
> quedar vacío y los identificadores arrancan de nuevo en 1.

## 12. Dirección de Swagger UI

Con el servidor en ejecución, la documentación interactiva está disponible en:

```
http://127.0.0.1:8000/docs
```

Desde allí se puede probar cada endpoint con el botón **Try it out**, sin necesidad de
herramientas externas. También está disponible la documentación alternativa en
`http://127.0.0.1:8000/redoc` y el esquema OpenAPI en `http://127.0.0.1:8000/openapi.json`.

---

## Pruebas realizadas

| Operación | Petición | Código | Resultado |
|---|---|---|---|
| Crear | `POST /productos/` | 201 | Producto creado con su id |
| Listar | `GET /productos/` | 200 | Catálogo completo |
| Filtrar | `GET /productos/?categoria=Bebidas` | 200 | Solo los productos de esa línea |
| Consultar | `GET /productos/2` | 200 | Producto solicitado |
| Consultar inexistente | `GET /productos/99` | 404 | `No existe un producto con el id 99` |
| Actualizar | `PUT /productos/1` | 200 | Producto actualizado |
| Actualizar con código ajeno | `PUT /productos/1` | 400 | Código ya asignado a otro producto |
| Actualizar inexistente | `PUT /productos/99` | 404 | `No existe un producto con el id 99` |
| Eliminar | `DELETE /productos/3` | 200 | Producto eliminado y devuelto |
| Eliminar repetido | `DELETE /productos/3` | 404 | `No existe un producto con el id 3` |
| Código duplicado | `POST /productos/` | 400 | Regla de negocio |
| Nombre duplicado | `POST /productos/` | 400 | Regla de negocio |
| Precio en cero | `POST /productos/` | 422 | Validación de Pydantic |
| Stock negativo | `POST /productos/` | 422 | Validación de Pydantic |
| Categoría inválida | `POST /productos/` | 422 | Validación de Pydantic |
