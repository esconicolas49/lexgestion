# LexGestión — prototipo de gestión jurídica

Aplicación inicial desarrollada con Python y Streamlit. Incluye módulos demostrativos para clientes, casos, tareas, documentos y solicitudes de asesoría.

## Requisitos
- Python 3.10 o superior (recomendado: Python 3.12)
- Git
- Visual Studio Code

## Instalación local (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Abre la dirección local que aparece en la terminal (normalmente http://localhost:8501).

## Estructura
- `app.py`: interfaz Streamlit y navegación.
- `database.py`: operaciones SQLite.
- `styles.css`: estilos visuales.
- `data/`: base de datos local generada al ejecutar.
- `uploads/`: archivos cargados localmente.

## GitHub

```bash
git init
git add .
git commit -m "Initial legal management prototype"
git branch -M main
git remote add origin https://github.com/USUARIO/REPOSITORIO.git
git push -u origin main
```

Cambia la URL por la de tu repositorio.

## Despliegue
En Streamlit Community Cloud crea una app, selecciona el repositorio, rama `main` y archivo `app.py`.

## ADVERTENCIA DE SEGURIDAD
Este proyecto es un prototipo educativo. NO usar con datos personales reales, expedientes, documentos confidenciales ni información protegida por secreto profesional. No incluye autenticación ni autorización real, cifrado de archivos, auditoría, copias de seguridad, controles de retención ni endurecimiento de seguridad.

Antes de producción se requiere:
1. Autenticación robusta y MFA.
2. Roles y permisos verificados en el servidor para cada operación.
3. PostgreSQL gestionado y almacenamiento privado de archivos.
4. Cifrado en tránsito y en reposo, gestión de claves y backups probados.
5. Registro de auditoría y políticas de retención/eliminación.
6. Revisión de seguridad, privacidad y cumplimiento legal aplicable en Colombia.
7. Contratos y acuerdos con proveedores cloud y evaluación de transferencias/encargados de datos.

No subas `.streamlit/secrets.toml`, contraseñas, llaves, bases de datos ni documentos al repositorio.
