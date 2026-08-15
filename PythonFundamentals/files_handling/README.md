
`poetry new proyecto` | Crea un nuevo proyecto con la estructura recomendada.
`poetry init`         | Inicializa Poetry en un proyecto existente.  
`poetry install`      | Instala todas las dependencias del proyecto. También crea el entorno virtual si no existe.
`poetry add paquete`| Agrega una dependencia. Ej: `poetry add requests`.
`poetry add --group dev pytest` | Agrega una dependencia de desarrollo. 
`poetry remove paquete`         | Elimina una dependencia.
`poetry update`| Actualiza todas las dependencias según las restricciones del `pyproject.toml`.
`poetry update paquete`  | Actualiza solo un paquete específico. 
`poetry lock` | Regenera el archivo `poetry.lock`.
`poetry show` | Lista las dependencias instaladas.
`poetry show --tree` | Muestra el árbol de dependencias.
`poetry check` | Verifica que `pyproject.toml` sea válido.
