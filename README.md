# Repositorio_Papers_API_Concurrente


## Configuración del Entorno Local


### 1. Clonar el repositorio y navegar al proyecto
Si aún no lo has hecho, clona el repositorio y entra a la carpeta del proyecto:
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DE_LA_CARPETA>
```

### 2. Crear el entorno virtual
Ejecuta el siguiente comando para crear un entorno virtual llamado `venv`:
```bash
python -m venv venv
```

### 3. Activar el entorno virtual

* **Windows (CMD):**
  ```cmd
  .venv\Scripts\activate
  ```
* **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
* **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```

### 4. Instalar las dependencias
Una vez activado el entorno, instala todos los paquetes necesarios con el siguiente comando:
```bash
python -m pip install -r requirements.txt ó

python3 -m pip install -r requirements.txt
```
### 5. Levantar el api
Una vez instalado todo lo necesario, ejecutar:
```bash
python -m uvicorn main:app --reload
```
Copear la ruta de localhost y pegar en el navegador.

## Endpoints

* **GET /**: Muestra la interfaz principal del repositorio de papers.

* **GET /papers**: Obtiene y muestra la lista de todos los papers registrados en la base de datos.

* **GET /papers/{id}**: Busca un paper específico utilizando su ID.

* **POST /papers**: Registra un nuevo paper en la base de datos. El título no puede estar repetido.

* **PUT /papers/{id}**: Actualiza la información de un paper existente utilizando su ID.

* **DELETE /papers/{id}**: Elimina un paper de la base de datos utilizando su ID.

* **POST /papers/{id}/revision-validez**: Realiza una revisión de validez simulada del paper. Este endpoint utiliza `asyncio.to_thread()` para ejecutar la tarea bloqueante en un hilo secundario y evitar bloquear el event loop de FastAPI.
