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
