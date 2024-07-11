# Como iniciar

1. Clonar el repositorio
2. `cp .env.example .env` para copiar el archivo .env.example
3. Tienen que crear la BBDD()
   `CREATE DATABASE instagram`
4. Actualizar el valor de `DATABASE_URL` en el archivo `.env`
   `postgresql://user:password@localhost:5432/nombre_base_datos`

5.1 `pipenv shell`
5.2 `pipenv install`
5.3 `pipenv run init`: Crea el historial de migraciones(si no existe)

5.4 `pipenv run migrate`: Crea un nuevo archivo de migraciones

5.5 `pipenv run upgrade`: Aplica las migraciones a la BBDD

6 `pipenv run start`: Inicia el entorno de desarrollo

## A crear modelos

## A Crear Endpoints
