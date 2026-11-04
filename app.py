import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date, datetime

# ---------------- CONFIGURACIÓN ----------------

st.set_page_config(
    page_title="LexGestión",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB = "lexgestion.db"
CARPETA_DOCUMENTOS = "documentos"

os.makedirs(CARPETA_DOCUMENTOS, exist_ok=True)

# ---------------- DISEÑO ----------------

st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fb;
    }

    section[data-testid="stSidebar"] {
        background-color: #101d35;
    }

    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    h1, h2, h3 {
        color: #14294b;
    }

    div[data-testid="stMetric"] {
        background: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e9f0;
    }

    div.stButton > button {
        background-color: #17345e;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 18px;
    }

    div.stButton > button:hover {
        background-color: #c49b45;
        color: white;
    }

    .encabezado {
        background: #14294b;
        padding: 22px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }

    .encabezado h1 {
        color: white;
        margin: 0;
    }

    .encabezado p {
        color: #dce4f1;
        margin-bottom: 0;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- BASE DE DATOS ----------------

def conectar():
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_db():
    with conectar() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            documento TEXT,
            correo TEXT,
            telefono TEXT,
            fecha TEXT
        );

        CREATE TABLE IF NOT EXISTS casos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            cliente TEXT,
            area TEXT,
            estado TEXT,
            responsable TEXT,
            fecha TEXT,
            descripcion TEXT
        );

        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            responsable TEXT,
            fecha TEXT,
            prioridad TEXT,
            estado TEXT
        );

        CREATE TABLE IF NOT EXISTS solicitudes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            correo TEXT,
            servicio TEXT,
            descripcion TEXT,
            fecha TEXT,
            estado TEXT
        );

        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            categoria TEXT,
            caso TEXT,
            ruta TEXT,
            fecha TEXT
        );
        """)


inicializar_db()


def consultar(sql, parametros=()):
    with conectar() as conn:
        return pd.read_sql_query(sql, conn, params=parametros)


def ejecutar(sql, parametros=()):
    with conectar() as conn:
        conn.execute(sql, parametros)


# ---------------- ENCABEZADO ----------------

st.markdown("""
<div class="encabezado">
    <h1>⚖️ LexGestión</h1>
    <p>Plataforma de gestión jurídica</p>
</div>
""", unsafe_allow_html=True)


# ---------------- MENÚ ----------------

with st.sidebar:
    st.title("LEXGESTIÓN")
    st.caption("Panel de administración")
    st.divider()

    pagina = st.radio(
        "MENÚ PRINCIPAL",
        [
            "Inicio",
            "Clientes",
            "Expedientes",
            "Tareas",
            "Documentos",
            "Solicitudes",
            "Reportes"
        ]
    )

    st.divider()
    st.caption("LexGestión · Gestión jurídica")


# ==================================================
# INICIO
# ==================================================

if pagina == "Inicio":

    st.title("Panel general")
    st.caption("Resumen de actividad")

    clientes = consultar("SELECT * FROM clientes")
    casos = consultar("SELECT * FROM casos")
    tareas = consultar("SELECT * FROM tareas")
    solicitudes = consultar("SELECT * FROM solicitudes")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Clientes", len(clientes))
    c2.metric("Expedientes", len(casos))
    c3.metric("Tareas", len(tareas))
    c4.metric("Solicitudes", len(solicitudes))

    st.divider()

    izquierda, derecha = st.columns(2)

    with izquierda:
        st.subheader("Últimos expedientes")
        if not casos.empty:
            st.dataframe(
                casos[["titulo", "cliente", "estado"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay expedientes registrados.")

    with derecha:
        st.subheader("Tareas pendientes")
        pendientes = tareas[tareas["estado"] != "Completada"]

        if not pendientes.empty:
            st.dataframe(
                pendientes[["titulo", "responsable", "fecha"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay tareas pendientes.")


# ==================================================
# CLIENTES
# ==================================================

elif pagina == "Clientes":

    st.title("Clientes")

    with st.expander("＋ Registrar cliente", expanded=False):

        with st.form("form_cliente"):

            nombre = st.text_input("Nombre completo")
            documento = st.text_input("Documento")
            correo = st.text_input("Correo electrónico")
            telefono = st.text_input("Teléfono")

            guardar = st.form_submit_button("Guardar cliente")

            if guardar:
                if not nombre.strip():
                    st.warning("Ingresa el nombre del cliente.")
                else:
                    ejecutar("""
                        INSERT INTO clientes
                        (nombre, documento, correo, telefono, fecha)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        nombre.strip(),
                        documento.strip(),
                        correo.strip(),
                        telefono.strip(),
                        date.today().isoformat()
                    ))

                    st.success("Cliente guardado.")
                    st.rerun()

    datos = consultar("SELECT * FROM clientes ORDER BY id DESC")

    st.subheader("Directorio de clientes")

    if not datos.empty:
        busqueda = st.text_input("Buscar cliente")

        if busqueda:
            datos = datos[
                datos.astype(str).apply(
                    lambda fila: fila.str.contains(
                        busqueda, case=False
                    ).any(),
                    axis=1
                )
            ]

        st.dataframe(
            datos.drop(columns=["id"]),
            use_container_width=True,
            hide_index=True
        )

        with st.expander("Eliminar cliente"):
            id_cliente = st.number_input(
                "ID del cliente",
                min_value=1,
                step=1
            )

            if st.button("Eliminar cliente"):
                ejecutar(
                    "DELETE FROM clientes WHERE id = ?",
                    (id_cliente,)
                )
                st.success("Registro eliminado.")
                st.rerun()

    else:
        st.info("Todavía no hay clientes registrados.")


# ==================================================
# EXPEDIENTES
# ==================================================

elif pagina == "Expedientes":

    st.title("Expedientes")

    clientes = consultar("SELECT nombre FROM clientes")
    lista_clientes = (
        clientes["nombre"].tolist()
        if not clientes.empty else []
    )

    with st.expander("＋ Crear expediente"):

        with st.form("form_caso"):

            titulo = st.text_input("Nombre del expediente")

            cliente = st.selectbox(
                "Cliente",
                ["Sin asignar"] + lista_clientes
            )

            area = st.selectbox(
                "Área jurídica",
                [
                    "Civil",
                    "Comercial",
                    "Laboral",
                    "Penal",
                    "Familia",
                    "Administrativo",
                    "Tributario",
                    "Otra"
                ]
            )

            responsable = st.text_input("Abogado responsable")

            estado = st.selectbox(
                "Estado",
                [
                    "Abierto",
                    "En proceso",
                    "En revisión",
                    "Cerrado"
                ]
            )

            descripcion = st.text_area("Descripción breve")

            guardar = st.form_submit_button("Guardar expediente")

            if guardar:
                if not titulo.strip():
                    st.warning("El nombre del expediente es obligatorio.")
                else:
                    ejecutar("""
                        INSERT INTO casos
                        (titulo, cliente, area, estado, responsable,
                         fecha, descripcion)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        titulo.strip(),
                        cliente,
                        area,
                        estado,
                        responsable.strip(),
                        date.today().isoformat(),
                        descripcion.strip()
                    ))

                    st.success("Expediente creado.")
                    st.rerun()

    datos = consultar("SELECT * FROM casos ORDER BY id DESC")

    st.subheader("Expedientes registrados")

    if not datos.empty:

        filtro = st.selectbox(
            "Filtrar por estado",
            ["Todos", "Abierto", "En proceso", "En revisión", "Cerrado"]
        )

        if filtro != "Todos":
            datos = datos[datos["estado"] == filtro]

        st.dataframe(
            datos.drop(columns=["id", "descripcion"]),
            use_container_width=True,
            hide_index=True
        )

        with st.expander("Eliminar expediente"):
            id_caso = st.number_input(
                "ID del expediente",
                min_value=1,
                step=1
            )

            if st.button("Eliminar expediente"):
                ejecutar(
                    "DELETE FROM casos WHERE id = ?",
                    (id_caso,)
                )
                st.success("Expediente eliminado.")
                st.rerun()

    else:
        st.info("No hay expedientes registrados.")


# ==================================================
# TAREAS
# ==================================================

elif pagina == "Tareas":

    st.title("Tareas y seguimiento")

    with st.expander("＋ Crear tarea"):

        with st.form("form_tarea"):

            titulo = st.text_input("Nombre de la tarea")
            responsable = st.text_input("Responsable")
            fecha = st.date_input("Fecha límite")

            prioridad = st.selectbox(
                "Prioridad",
                ["Baja", "Media", "Alta", "Urgente"]
            )

            estado = st.selectbox(
                "Estado",
                ["Pendiente", "En proceso", "Completada"]
            )

            guardar = st.form_submit_button("Guardar tarea")

            if guardar:
                if not titulo.strip():
                    st.warning("Escribe el nombre de la tarea.")
                else:
                    ejecutar("""
                        INSERT INTO tareas
                        (titulo, responsable, fecha, prioridad, estado)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        titulo.strip(),
                        responsable.strip(),
                        fecha.isoformat(),
                        prioridad,
                        estado
                    ))

                    st.success("Tarea creada.")
                    st.rerun()

    datos = consultar("SELECT * FROM tareas ORDER BY fecha ASC")

    st.subheader("Listado de tareas")

    if not datos.empty:

        st.dataframe(
            datos.drop(columns=["id"]),
            use_container_width=True,
            hide_index=True
        )

        with st.expander("Actualizar estado de tarea"):

            id_tarea = st.number_input(
                "ID de tarea",
                min_value=1,
                step=1
            )

            nuevo_estado = st.selectbox(
                "Nuevo estado",
                ["Pendiente", "En proceso", "Completada"]
            )

            if st.button("Actualizar tarea"):
                ejecutar(
                    "UPDATE tareas SET estado = ? WHERE id = ?",
                    (nuevo_estado, id_tarea)
                )
                st.success("Tarea actualizada.")
                st.rerun()

        with st.expander("Eliminar tarea"):

            id_eliminar = st.number_input(
                "ID para eliminar",
                min_value=1,
                step=1,
                key="eliminar_tarea"
            )

            if st.button("Eliminar tarea"):
                ejecutar(
                    "DELETE FROM tareas WHERE id = ?",
                    (id_eliminar,)
                )
                st.success("Tarea eliminada.")
                st.rerun()

    else:
        st.info("No hay tareas registradas.")


# ==================================================
# DOCUMENTOS
# ==================================================

elif pagina == "Documentos":

    st.title("Gestión documental")

    st.caption("Carga y consulta de archivos.")

    with st.expander("＋ Subir documento"):

        with st.form("form_documento"):

            archivo = st.file_uploader(
                "Seleccionar archivo",
                type=[
                    "pdf", "docx", "doc",
                    "xlsx", "xls", "jpg",
                    "jpeg", "png", "txt"
                ]
            )

            categoria = st.selectbox(
                "Categoría",
                [
                    "Contrato",
                    "Poder",
                    "Demanda",
                    "Prueba",
                    "Identificación",
                    "Sentencia",
                    "Otro"
                ]
            )

            caso = st.text_input("Expediente relacionado")

            guardar = st.form_submit_button("Guardar documento")

            if guardar:
                if archivo is None:
                    st.warning("Selecciona un archivo.")
                else:
                    nombre_seguro = os.path.basename(archivo.name)
                    nombre_final = (
                        datetime.now().strftime("%Y%m%d%H%M%S%f")
                        + "_"
                        + nombre_seguro
                    )

                    ruta = os.path.join(
                        CARPETA_DOCUMENTOS,
                        nombre_final
                    )

                    with open(ruta, "wb") as f:
                        f.write(archivo.getbuffer())

                    ejecutar("""
                        INSERT INTO documentos
                        (nombre, categoria, caso, ruta, fecha)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        nombre_seguro,
                        categoria,
                        caso.strip(),
                        ruta,
                        date.today().isoformat()
                    ))

                    st.success("Documento guardado.")
                    st.rerun()

    datos = consultar(
        "SELECT * FROM documentos ORDER BY id DESC"
    )

    st.subheader("Documentos registrados")

    if not datos.empty:

        st.dataframe(
            datos[["nombre", "categoria", "caso", "fecha"]],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Descargar documento")

        opciones = {
            f"{fila.id} - {fila.nombre}": fila.ruta
            for fila in datos.itertuples()
            if os.path.isfile(fila.ruta)
        }

        if opciones:
            seleccionado = st.selectbox(
                "Seleccionar documento",
                list(opciones.keys())
            )

            ruta = opciones[seleccionado]

            with open(ruta, "rb") as archivo:
                st.download_button(
                    "Descargar archivo",
                    data=archivo.read(),
                    file_name=os.path.basename(ruta)
                )

    else:
        st.info("No hay documentos cargados.")


# ==================================================
# SOLICITUDES
# ==================================================

elif pagina == "Solicitudes":

    st.title("Solicitudes de asesoría")

    with st.expander("＋ Nueva solicitud"):

        with st.form("form_solicitud"):

            nombre = st.text_input("Nombre del solicitante")
            correo = st.text_input("Correo electrónico")

            servicio = st.selectbox(
                "Servicio solicitado",
                [
                    "Asesoría jurídica",
                    "Consulta legal",
                    "Representación judicial",
                    "Elaboración de contrato",
                    "Revisión documental",
                    "Otro"
                ]
            )

            descripcion = st.text_area(
                "Describe brevemente tu solicitud"
            )

            guardar = st.form_submit_button("Registrar solicitud")

            if guardar:
                if not nombre.strip() or not correo.strip():
                    st.warning("Completa nombre y correo.")
                else:
                    ejecutar("""
                        INSERT INTO solicitudes
                        (nombre, correo, servicio, descripcion, fecha, estado)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        nombre.strip(),
                        correo.strip(),
                        servicio,
                        descripcion.strip(),
                        date.today().isoformat(),
                        "Nueva"
                    ))

                    st.success("Solicitud registrada.")
                    st.rerun()

    datos = consultar(
        "SELECT * FROM solicitudes ORDER BY id DESC"
    )

    st.subheader("Solicitudes recibidas")

    if not datos.empty:

        st.dataframe(
            datos.drop(columns=["id"]),
            use_container_width=True,
            hide_index=True
        )

        with st.expander("Actualizar solicitud"):

            id_solicitud = st.number_input(
                "ID de solicitud",
                min_value=1,
                step=1
            )

            estado = st.selectbox(
                "Estado",
                ["Nueva", "En revisión", "Atendida", "Cerrada"]
            )

            if st.button("Actualizar solicitud"):
                ejecutar(
                    "UPDATE solicitudes SET estado = ? WHERE id = ?",
                    (estado, id_solicitud)
                )
                st.success("Solicitud actualizada.")
                st.rerun()

    else:
        st.info("No hay solicitudes registradas.")


# ==================================================
# REPORTES
# ==================================================

elif pagina == "Reportes":

    st.title("Reportes")

    clientes = consultar("SELECT * FROM clientes")
    casos = consultar("SELECT * FROM casos")
    tareas = consultar("SELECT * FROM tareas")
    documentos = consultar("SELECT * FROM documentos")
    solicitudes = consultar("SELECT * FROM solicitudes")

    st.subheader("Resumen de gestión")

    a, b, c = st.columns(3)
    a.metric("Clientes", len(clientes))
    b.metric("Expedientes", len(casos))
    c.metric("Documentos", len(documentos))

    d, e = st.columns(2)
    d.metric("Tareas", len(tareas))
    e.metric("Solicitudes", len(solicitudes))

    st.divider()

    st.subheader("Exportar información")

    tablas = {
        "Clientes": clientes,
        "Expedientes": casos,
        "Tareas": tareas,
        "Documentos": documentos.drop(columns=["ruta"], errors="ignore"),
        "Solicitudes": solicitudes
    }

    seleccion = st.selectbox(
        "Seleccionar reporte",
        list(tablas.keys())
    )

    csv = tablas[seleccion].to_csv(
        index=False
    ).encode("utf-8-sig")

    st.download_button(
        "Descargar reporte CSV",
        data=csv,
        file_name=f"reporte_{seleccion.lower()}.csv",
        mime="text/csv"
    )


# ---------------- PIE DE PÁGINA ----------------

st.divider()
st.caption("LexGestión © 2026")