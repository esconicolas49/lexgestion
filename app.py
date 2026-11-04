import streamlit as st
from pathlib import Path
from datetime import date
from database import init_db, add_client, get_clients, add_case, get_cases, add_task, get_tasks, save_document, get_documents

ROOT = Path(__file__).parent
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

st.set_page_config(page_title="LexGestión | Firma jurídica", page_icon="⚖️", layout="wide")
init_db()

css = (ROOT / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚖️ LexGestión")
    st.caption("Plataforma interna · Prototipo")
    page = st.radio("NAVEGACIÓN", [
        "Resumen", "Clientes", "Casos", "Tareas", "Documentos", "Solicitudes de asesoría"
    ])
    st.divider()
    st.caption("Versión inicial de demostración")
    st.warning("No cargues información real ni documentos confidenciales en este prototipo.")

def header(title, subtitle):
    st.markdown(f'<div class="page-header"><div class="eyebrow">LEXGESTIÓN · FIRMA JURÍDICA</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

if page == "Resumen":
    header("Centro de operaciones", "Una vista general de clientes, procesos y actividades.")
    clients, cases, tasks, docs = get_clients(), get_cases(), get_tasks(), get_documents()
    c1,c2,c3,c4 = st.columns(4)
    for col, label, value in zip([c1,c2,c3,c4], ["Clientes registrados","Casos registrados","Tareas registradas","Documentos cargados"], [len(clients),len(cases),len(tasks),len(docs)]):
        col.markdown(f'<div class="metric"><span>{label}</span><strong>{value}</strong></div>', unsafe_allow_html=True)
    st.subheader("Actividad reciente")
    if tasks:
        st.dataframe(tasks[:8], use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay tareas. Crea una desde el módulo Tareas.")
    st.subheader("Casos recientes")
    if cases:
        st.dataframe(cases[:8], use_container_width=True, hide_index=True)
    else:
        st.info("Todavía no hay casos registrados.")

elif page == "Clientes":
    header("Directorio de clientes", "Registra y consulta la información básica de contacto.")
    with st.expander("＋ Registrar cliente", expanded=False):
        with st.form("client_form", clear_on_submit=True):
            name = st.text_input("Nombre completo / Razón social *")
            email = st.text_input("Correo electrónico")
            phone = st.text_input("Teléfono")
            notes = st.text_area("Notas internas (no incluir datos sensibles en esta demo)")
            submitted = st.form_submit_button("Guardar cliente", type="primary")
            if submitted:
                if not name.strip():
                    st.error("El nombre es obligatorio.")
                else:
                    add_client(name.strip(), email.strip(), phone.strip(), notes.strip())
                    st.success("Cliente guardado.")
                    st.rerun()
    rows = get_clients()
    st.dataframe(rows, use_container_width=True, hide_index=True) if rows else st.info("No hay clientes registrados.")

elif page == "Casos":
    header("Expedientes y casos", "Asocia cada asunto con un cliente y controla su estado.")
    clients = get_clients()
    if not clients:
        st.info("Primero registra al menos un cliente en el módulo Clientes.")
    else:
        with st.expander("＋ Crear caso", expanded=False):
            names = {f'{c["name"]} · #{c["id"]}': c["id"] for c in clients}
            with st.form("case_form", clear_on_submit=True):
                title = st.text_input("Nombre del asunto *")
                client_label = st.selectbox("Cliente", list(names))
                area = st.selectbox("Área", ["Civil","Comercial","Laboral","Familia","Administrativo","Penal","Otra"])
                status = st.selectbox("Estado", ["En estudio","Activo","Pendiente","Cerrado"])
                responsible = st.text_input("Abogado responsable")
                deadline = st.date_input("Próxima fecha importante", value=None)
                submitted = st.form_submit_button("Guardar caso", type="primary")
                if submitted:
                    if not title.strip():
                        st.error("El nombre del caso es obligatorio.")
                    else:
                        add_case(title.strip(), names[client_label], area, status, responsible.strip(), deadline.isoformat() if deadline else "")
                        st.success("Caso guardado.")
                        st.rerun()
    rows = get_cases()
    st.dataframe(rows, use_container_width=True, hide_index=True) if rows else st.info("No hay casos registrados.")

elif page == "Tareas":
    header("Tareas y seguimiento", "Organiza actividades y evita que los pendientes queden sin responsable.")
    with st.expander("＋ Crear tarea", expanded=False):
        with st.form("task_form", clear_on_submit=True):
            title = st.text_input("Descripción de la tarea *")
            responsible = st.text_input("Responsable")
            due = st.date_input("Fecha límite", value=date.today())
            priority = st.selectbox("Prioridad", ["Baja","Media","Alta","Urgente"])
            status = st.selectbox("Estado", ["Pendiente","En progreso","Completada"])
            submitted = st.form_submit_button("Crear tarea", type="primary")
            if submitted:
                if not title.strip():
                    st.error("La descripción es obligatoria.")
                else:
                    add_task(title.strip(), responsible.strip(), due.isoformat(), priority, status)
                    st.success("Tarea creada.")
                    st.rerun()
    rows = get_tasks()
    st.dataframe(rows, use_container_width=True, hide_index=True) if rows else st.info("No hay tareas registradas.")

elif page == "Documentos":
    header("Centro documental", "Carga archivos de prueba y asócialos a un expediente.")
    st.warning("En esta versión los archivos se guardan localmente sin cifrado ni control de acceso. Usa únicamente documentos ficticios.")
    cases = get_cases()
    if not cases:
        st.info("Crea un caso antes de asociar documentos.")
    else:
        case_options = {f'{c["title"]} · #{c["id"]}': c["id"] for c in cases}
        chosen = st.selectbox("Asociar al caso", list(case_options))
        uploaded = st.file_uploader("Seleccionar archivo", type=["pdf","docx","doc","png","jpg","jpeg","xlsx"])
        if st.button("Guardar documento", type="primary", disabled=uploaded is None):
            safe_name = Path(uploaded.name).name.replace(" ", "_")
            stored = f"{date.today().isoformat()}_{safe_name}"
            target = UPLOAD_DIR / stored
            target.write_bytes(uploaded.getbuffer())
            save_document(uploaded.name, str(target.relative_to(ROOT)), case_options[chosen])
            st.success("Archivo guardado en el entorno local.")
            st.rerun()
    docs = get_documents()
    if docs:
        st.dataframe(docs, use_container_width=True, hide_index=True)
    else:
        st.info("No hay documentos cargados.")

elif page == "Solicitudes de asesoría":
    header("Solicitudes de asesoría", "Formulario público de demostración para captar nuevos contactos.")
    with st.form("request_form", clear_on_submit=True):
        name = st.text_input("Nombre")
        email = st.text_input("Correo")
        phone = st.text_input("Teléfono")
        topic = st.selectbox("Motivo de consulta", ["Asesoría general","Derecho civil","Derecho comercial","Derecho laboral","Otro"])
        description = st.text_area("Cuéntanos brevemente qué necesitas")
        consent = st.checkbox("Autorizo el tratamiento de mis datos para que la firma pueda contactarme.")
        sent = st.form_submit_button("Enviar solicitud", type="primary")
        if sent:
            if not name.strip() or not (email.strip() or phone.strip()) or not consent:
                st.error("Completa el nombre, un medio de contacto y la autorización.")
            else:
                st.success("Solicitud recibida en esta demostración. En producción debe almacenarse en un módulo privado y activar un aviso al equipo.")
                st.info("No envíes información confidencial ni detalles protegidos por secreto profesional en este formulario de prueba.")

st.markdown('<div class="footer">LexGestión · Prototipo de desarrollo · No apto para expedientes reales</div>', unsafe_allow_html=True)
