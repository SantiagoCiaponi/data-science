# Sistema Recomendador - Grupo 4 (Ciencia de Datos 2025)

Este proyecto constituye el Trabajo Integrador de la cátedra. Consiste en una API desarrollada en **FastAPI** que implementa un sistema de recomendaciones.

## Stack Tecnológico
* **Lenguaje:** Python 3.9+
* **Framework API:** FastAPI 
* **Procesamiento de Datos:** Pandas
* **Contrato de Interfaz:** OpenAPI 3.0.4 (`trabajoFinal.yaml`)

## Estructura del Proyecto
* `main.py`: Punto de entrada de la alpicación. Gestiona los endpoints y la persistencia local.
* `models.py`: definiciones de esquemas Pydantic (User, Item, Error) basados en el contrato oficial. Lo que hace cualquier model viste siempre se usan para esto...
* `recommendation.py`: motor de recomendaciones. Acá está tdoa la movida.
* `usuarios.csv`: archivo de almacenamiento persistente. Este va a tener la posta. Si cambiamos el csv se tiene que seguir comportando bien. 

## Instalación y Ejecución

1. **Clonar el repositorio** y asegurarse de tener los archivos del TPI disponibles para la carga del modelo.
2. **Instalar dependencias**:
    ```bash
    pip install fastapi uvicorn pandas
    ```
3. **Iniciar el servidor:**:
    ```bash
    uvicorn main:app --reload
    ```
3. **Usar la movida:**:
    toda la movida va a estar en:
    ```bash
    http://127.0.0.1:8000/docs
    ```