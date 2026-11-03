from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUTPUT_PATH = Path(__file__).resolve().parents[1] / "docs" / "procedimiento_aprovisionamiento_oci_workshop_khipu.docx"


def set_cell_shading(cell, fill):
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def set_cell_border(cell, color="D9D9D9"):
    properties = cell._tc.get_or_add_tcPr()
    borders = properties.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        properties.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "4")
        element.set(qn("w:color"), color)


def set_cell_margins(cell, top=100, start=120, bottom=100, end=120):
    properties = cell._tc.get_or_add_tcPr()
    margins = properties.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        properties.append(margins)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        element = margins.find(qn(f"w:{side}"))
        if element is None:
            element = OxmlElement(f"w:{side}")
            margins.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def set_repeat_table_header(row):
    properties = row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    properties.append(repeat)


def set_width(cell, width_inches):
    cell.width = Inches(width_inches)
    properties = cell._tc.get_or_add_tcPr()
    width = properties.find(qn("w:tcW"))
    if width is None:
        width = OxmlElement("w:tcW")
        properties.append(width)
    width.set(qn("w:w"), str(int(width_inches * 1440)))
    width.set(qn("w:type"), "dxa")


def set_run_font(run, size=10.5, bold=False, color="000000"):
    run.font.name = "Aptos"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def add_text(document, text, style=None, bold_lead=None):
    paragraph = document.add_paragraph(style=style)
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.12
    if bold_lead and text.startswith(bold_lead):
        lead = paragraph.add_run(bold_lead)
        set_run_font(lead, bold=True)
        rest = paragraph.add_run(text[len(bold_lead):])
        set_run_font(rest)
    else:
        run = paragraph.add_run(text)
        set_run_font(run)
    return paragraph


def add_bullet(document, text, level=0):
    paragraph = document.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.line_spacing = 1.08
    run = paragraph.add_run(text)
    set_run_font(run, size=10.5)
    return paragraph


def add_numbered(document, title, detail):
    paragraph = document.add_paragraph(style="List Number")
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.line_spacing = 1.08
    run = paragraph.add_run(title)
    set_run_font(run, size=10.5, bold=True)
    run = paragraph.add_run(detail)
    set_run_font(run, size=10.5)
    return paragraph


def add_code(document, command):
    table = document.add_table(rows=1, cols=1)
    table.autofit = False
    cell = table.cell(0, 0)
    set_cell_shading(cell, "F3F6F8")
    set_cell_border(cell, "D9D9D9")
    set_cell_margins(cell, top=90, start=120, bottom=90, end=120)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    run = paragraph.add_run(command)
    run.font.name = "Consolas"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Consolas")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Consolas")
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0, 0, 0)
    document.add_paragraph().paragraph_format.space_after = Pt(1)


def add_status_table(document):
    table = document.add_table(rows=1, cols=3)
    table.autofit = False
    headers = ("Elemento", "Estado", "Observación")
    widths = (1.75, 1.35, 3.4)
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        set_width(cell, widths[index])
        set_cell_shading(cell, "17365D")
        set_cell_border(cell)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = paragraph.add_run(header)
        set_run_font(run, size=9.5, bold=True, color="FFFFFF")
    set_repeat_table_header(table.rows[0])
    rows = (
        ("Compartimento", "Creado", "Entorno dedicado para el piloto del workshop."),
        ("Bucket de Object Storage", "Creado", "Repositorio de activos para los laboratorios."),
        ("Autonomous AI Database", "Disponible", "Creada correctamente con 2 ECPU e iniciada para validar el Laboratorio 1."),
        (
            "AI Agent Memory",
            "Validado",
            "Store creado, recuperación aislada verificada y evidencia presentada en Khipu AI Memory Studio.",
        ),
        ("Laboratorio 2 RAG", "Validado", "Embeddings, recuperación v2 y respuesta anclada verificados con contratos sintéticos."),
        ("Laboratorio 3 API", "Validado", "Análisis, parche revisable y pruebas FastAPI v2 verificados localmente con datos sintéticos."),
        ("Políticas IAM", "No aplicadas", "El plan actual solo entrega las sentencias para su revisión; no crea grupos ni políticas."),
    )
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cell = cells[index]
            set_width(cell, widths[index])
            set_cell_border(cell)
            set_cell_margins(cell)
            if row_index % 2 == 1:
                set_cell_shading(cell, "F3F6F8")
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            paragraph = cell.paragraphs[0]
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER if index == 1 else WD_ALIGN_PARAGRAPH.LEFT
            run = paragraph.add_run(value)
            set_run_font(run, size=9.5)
    document.add_paragraph().paragraph_format.space_after = Pt(1)


def add_checklist(document, items):
    for item in items:
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.left_indent = Inches(0.15)
        paragraph.paragraph_format.space_after = Pt(3)
        run = paragraph.add_run("[ ] ")
        set_run_font(run, size=10.5, bold=True)
        run = paragraph.add_run(item)
        set_run_font(run, size=10.5)


def configure_document(document):
    section = document.sections[0]
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)

    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(10.5)

    for style_name, size in (("Title", 20), ("Heading 1", 14), ("Heading 2", 11.5)):
        style = styles[style_name]
        style.font.name = "Aptos Display" if style_name == "Title" else "Aptos"
        style._element.rPr.rFonts.set(qn("w:ascii"), style.font.name)
        style._element.rPr.rFonts.set(qn("w:hAnsi"), style.font.name)
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(12 if style_name != "Title" else 0)
        style.paragraph_format.space_after = Pt(6)

    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run("Workshop Khipu  OCI  Procedimiento de aprovisionamiento")
    set_run_font(run, size=8.5, color="555555")


def build_document():
    document = Document()
    configure_document(document)

    title = document.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = title.add_run("Procedimiento de aprovisionamiento OCI para el Workshop Khipu")
    set_run_font(run, size=20, bold=True)

    subtitle = document.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(14)
    run = subtitle.add_run("Piloto técnico en OCI Free Trial región Chicago  Octubre de 2026")
    set_run_font(run, size=11, color="404040")

    add_text(
        document,
        "Este documento registra el procedimiento reproducible para aprovisionar el entorno piloto del Workshop Khipu. El objetivo es disponer de un compartimento aislado, Object Storage y Autonomous AI Database para los laboratorios de memoria de agentes, RAG con evidencia y cambios seguros de API. El entorno se construye con Terraform desde Cloud Shell y no contiene secretos, OCID ni contraseñas.",
    )

    document.add_heading("Estado actual", level=1)
    add_status_table(document)
    add_text(
        document,
        "El piloto se aprovisionó correctamente. La primera ejecución creó el compartimento y el bucket; el reintento creó la base de datos después de corregir las validaciones de contraseña y modelo de cómputo. Terraform registró una sola creación adicional y no duplicó los recursos existentes. La ADB está disponible, el flujo mínimo de AI Agent Memory fue validado con dos equipos sintéticos y recuperación aislada, el Laboratorio 2 recuperó evidencia vectorial v2 y generó una respuesta anclada, y el Laboratorio 3 validó un cambio controlado de API con análisis, parche y pruebas.",
    )

    document.add_heading("Alcance del entorno", level=1)
    add_bullet(document, "Región objetivo: US Midwest Chicago.")
    add_bullet(document, "Compartimento dedicado: cmp-khipu-ai-workshop-dev.")
    add_bullet(document, "Bucket: khipu-ai-workshop-assets.")
    add_bullet(document, "Base de datos: Autonomous AI Database Serverless con Oracle Database 26ai y carga OLTP.")
    add_bullet(document, "Capacidad inicial de ADB: 2 ECPU y 1 TB de almacenamiento. El autoescalamiento de ECPU está deshabilitado para controlar consumo durante el piloto.")
    add_bullet(document, "IAM: las sentencias para participantes se entregan como salida revisable. No se crea ni modifica ninguna política IAM en este piloto.")

    document.add_heading("Requisitos previos", level=1)
    add_checklist(
        document,
        (
            "Cuenta de OCI Free Trial activa y sesión iniciada en la consola.",
            "Región Chicago seleccionada en la consola y en Cloud Shell.",
            "Cloud Shell disponible con permisos para crear recursos en el compartimento padre autorizado.",
            "Repositorio del workshop disponible localmente y archivo de variables de Terraform preparado fuera de Git.",
            "Disponibilidad verificada en la región de un modelo de chat y un modelo de embeddings de OCI Generative AI.",
            "Contraseña administrativa de ADB entre 12 y 30 caracteres, con mayúscula, minúscula, número y carácter especial.",
        ),
    )

    document.add_heading("Estructura relevante del repositorio", level=1)
    add_code(document, "terraform/environments/trial-chicago")
    add_text(
        document,
        "Este entorno compone módulos para compartimento, Object Storage, Autonomous Database e IAM. El módulo IAM permanece deshabilitado en el piloto; sus políticas se muestran como salida para validación del equipo antes de aplicarlas en el tenant de Khipu.",
    )

    document.add_heading("Procedimiento paso a paso", level=1)
    document.add_heading("Preparar Cloud Shell", level=2)
    add_numbered(document, "Abrir Cloud Shell. ", "Confirma que la sesión muestra la región Chicago antes de ejecutar Terraform.")
    add_numbered(document, "Copiar el paquete Terraform. ", "Sube el paquete no sensible del repositorio a Cloud Shell, extráelo en un directorio de trabajo privado y entra al entorno trial-chicago.")
    add_numbered(document, "Usar Terraform aislado. ", "La versión de Terraform se instaló en el directorio de trabajo de Cloud Shell, separada de archivos del repositorio.")
    add_code(document, "terraform version")

    document.add_heading("Configurar variables no secretas", level=2)
    add_text(
        document,
        "En terraform.tfvars se habilita la ADB, se selecciona la región Chicago y se aplican etiquetas del workshop. No se debe versionar este archivo si contiene datos específicos del tenant. Las etiquetas aplicadas son Environment, Project, Owner, CreatedBy y ManagedBy. CostCenter queda intencionalmente fuera del piloto, según la decisión del workshop.")
    add_bullet(document, "enable_autonomous_database = true")
    add_bullet(document, "autonomous_compute_count = 2")
    add_bullet(document, "autonomous_database_data_storage_size_in_tbs = 1")

    document.add_heading("Validar Terraform", level=2)
    add_numbered(document, "Inicializar proveedores. ", "Descarga y bloquea el proveedor OCI requerido por la configuración.")
    add_code(document, "terraform init")
    add_numbered(document, "Formatear y validar. ", "Confirma que la sintaxis y las referencias internas son correctas antes de planificar.")
    add_code(document, "terraform fmt -recursive\nterraform validate")
    add_numbered(document, "Revisar el plan. ", "Verifica la cantidad de recursos, el tamaño de ADB, la región y que no se creen políticas IAM no autorizadas.")
    add_code(document, "terraform plan -input=false -no-color")

    document.add_heading("Capturar la contraseña de ADB de forma segura", level=2)
    add_text(
        document,
        "La contraseña no se escribe en terraform.tfvars, archivos del repositorio, historial de comandos ni documentación. Se mantiene solamente como variable de entorno de la sesión activa de Cloud Shell. El comando oculta la entrada y muestra únicamente la confirmación PASSWORD_CAPTURED.")
    add_code(document, "read -s -p 'Enter ADB admin password (12-30 chars): ' TF_VAR_autonomous_admin_password; echo; echo PASSWORD_CAPTURED")
    add_text(document, "No se debe compartir ni registrar la contraseña. Si la sesión de Cloud Shell finaliza, es necesario capturarla nuevamente antes de un nuevo plan o apply que requiera crear la ADB.")

    document.add_heading("Aplicar infraestructura", level=2)
    add_text(document, "La ejecución debe iniciarse solo después de revisar el plan y autorizar el costo del recurso administrado.")
    add_code(document, "terraform apply -input=false -auto-approve")
    add_text(document, "La creación de ADB puede tomar varios minutos. Durante ese período se debe mantener la sesión de Cloud Shell activa y no ejecutar un segundo apply en paralelo.")

    document.add_heading("Manejo de validaciones de ADB", level=1)
    add_text(document, "El primer intento devolvió un error 400 InvalidParameter porque la contraseña administrativa superaba 30 caracteres. Este no es un error de Terraform ni de permisos OCI; es una validación del servicio Autonomous AI Database.")
    add_numbered(document, "No eliminar recursos existentes. ", "El compartimento y el bucket quedaron creados y registrados en el estado de Terraform.")
    add_numbered(document, "Capturar una nueva contraseña válida. ", "Usa entre 12 y 30 caracteres. Antes de ingresarla, cuenta los caracteres para evitar un segundo rechazo.")
    add_numbered(document, "Ejecutar terraform plan nuevamente. ", "El resultado esperado es Plan 1 to add 0 to change 0 to destroy.")
    add_numbered(document, "Corregir el modelo de cómputo si OCI rechaza OCPU. ", "Las nuevas Autonomous AI Databases en este entorno requieren ECPU. El módulo declara compute_model igual a ECPU y usa compute_count igual a 2; no utiliza cpu_core_count.")
    add_numbered(document, "Regenerar el bloqueo de proveedor en Cloud Shell cuando corresponda. ", "Si un archivo .terraform.lock.hcl creado en Windows no coincide con el proveedor Linux de Cloud Shell, se conserva como respaldo y se ejecuta terraform init -upgrade para generar el bloqueo de la plataforma correcta.")
    add_numbered(document, "Ejecutar terraform apply. ", "El resultado esperado es la creación únicamente de Autonomous AI Database.")

    document.add_heading("Validación posterior al aprovisionamiento", level=1)
    add_checklist(
        document,
        (
            "Terraform informa Apply complete sin errores.",
            "El plan posterior no propone recursos inesperados.",
            "La ADB alcanza el estado AVAILABLE.",
            "El bucket existe dentro del compartimento del workshop.",
            "No se aplicaron políticas IAM ni se expusieron secretos en consola, repositorio o documentación.",
            "OCI Generative AI en Chicago expone un modelo de chat y un modelo de embeddings aptos para los laboratorios.",
        ),
    )

    document.add_heading("Conexión segura y esquema del Laboratorio 1", level=1)
    add_text(
        document,
        "Esta sección prepara la base de datos para AI Agent Memory. El wallet, las contraseñas y los identificadores de recursos permanecen únicamente en Cloud Shell; no se copian al repositorio, a la documentación ni al chat.",
    )

    document.add_heading("Generar y proteger el wallet de instancia", level=2)
    add_numbered(document, "Preparar un directorio privado. ", "Crea el directorio en Cloud Shell y limita sus permisos antes de descargar el wallet.")
    add_code(document, 'mkdir -p "$HOME/.khipu-workshop/secrets"\nchmod 700 "$HOME/.khipu-workshop/secrets"')
    add_numbered(document, "Capturar los valores sensibles sin mostrarlos. ", "Ingresa el identificador de la ADB y la contraseña del wallet solo en la consola. El comando no debe imprimirse con valores reales ni guardarse en el historial.")
    add_code(document, "read -s -p 'ADB OCID: ' ADB_ID; echo\nread -s -p 'Wallet password: ' W; echo")
    add_numbered(document, "Generar el wallet. ", "La salida se guarda en el directorio privado; después se elimina la variable que contenía la contraseña.")
    add_code(document, 'oci db autonomous-database generate-wallet --autonomous-database-id "$ADB_ID" --password "$W" --file "$HOME/.khipu-workshop/secrets/lab01-wallet.zip" >/dev/null\nunset W\necho WALLET_DONE')
    add_numbered(document, "Descomprimir para los clientes Python. ", "Conserva también el archivo ZIP, porque SQLcl lo utiliza directamente.")
    add_code(document, 'mkdir -p "$HOME/.khipu-workshop/secrets/lab01-wallet"\nunzip -q "$HOME/.khipu-workshop/secrets/lab01-wallet.zip" -d "$HOME/.khipu-workshop/secrets/lab01-wallet"\nchmod 700 "$HOME/.khipu-workshop/secrets/lab01-wallet"')

    document.add_heading("Conectar SQLcl a la ADB", level=2)
    add_text(document, "En SQLcl se debe usar una ruta absoluta al archivo ZIP. El carácter ~ no se expande dentro del comando set cloudconfig. Reemplaza los marcadores por la ruta y el nombre de servicio que aparecen en el wallet, sin registrarlos en documentación compartida.")
    add_code(document, "sql /nolog\nset cloudconfig <absolute-path-to-lab01-wallet.zip>\nconnect admin@<database-service>")
    add_text(document, "SQLcl solicitará la contraseña de ADMIN de manera interactiva. Debe aparecer Connected. antes de ejecutar cualquier sentencia administrativa.")

    document.add_heading("Crear o recuperar el usuario propietario", level=2)
    add_text(document, "Para una instalación nueva, usa el siguiente flujo. La variable se ingresa enmascarada. Elige una contraseña de 12 a 30 caracteres y no uses comillas dobles ni el carácter ampersand.")
    add_code(document, "SET VERIFY OFF\nACCEPT LAB01PW CHAR PROMPT 'LAB01_OWNER password: ' HIDE\nCREATE USER LAB01_OWNER IDENTIFIED BY \"&LAB01PW\" DEFAULT TABLESPACE DATA TEMPORARY TABLESPACE TEMP QUOTA 500M ON DATA;\nUNDEFINE LAB01PW")
    add_text(document, "Si el usuario ya existe, no lo elimines. Para asignar o reemplazar su contraseña utiliza el flujo alternativo siguiente. Este método evita una excepción conocida del comando PASSWORD de SQLcl en esta sesión.")
    add_code(document, "SET VERIFY OFF\nACCEPT LAB01PW CHAR PROMPT 'New LAB01_OWNER password: ' HIDE\nALTER USER LAB01_OWNER IDENTIFIED BY \"&LAB01PW\";\nUNDEFINE LAB01PW")
    add_text(document, "El ingreso y la confirmación de la contraseña deben realizarlos manualmente en la consola. No compartas la contraseña en el chat ni la pegues en un comando que quede visible.")

    document.add_heading("Otorgar privilegios mínimos para AI Agent Memory", level=2)
    add_text(document, "El propietario administrado necesita crear tablas y procedimientos. CREATE JOB habilita la purga física de datos con TTL. CREATE TRIGGER y CREATE PROPERTY GRAPH habilitan memoria vinculada cuando el laboratorio la requiera.")
    add_code(document, "GRANT CREATE SESSION, CREATE TABLE, CREATE PROCEDURE, CREATE JOB, CREATE TRIGGER, CREATE PROPERTY GRAPH TO LAB01_OWNER;")

    document.add_heading("Validar el acceso del usuario propietario", level=2)
    add_text(document, "Cierra o cambia la conexión administrativa y prueba el usuario propietario. Introduce su contraseña solamente cuando SQLcl la solicite.")
    add_code(document, "connect lab01_owner@<database-service>\nSELECT USER FROM DUAL;\nSELECT privilege FROM session_privs WHERE privilege IN ('CREATE TABLE', 'CREATE PROCEDURE', 'CREATE JOB', 'CREATE TRIGGER', 'CREATE PROPERTY GRAPH') ORDER BY privilege;")
    add_checklist(
        document,
        (
            "Wallet de ADB generado y almacenado solo en el directorio privado de Cloud Shell.",
            "ADB en estado AVAILABLE antes de intentar la conexión.",
            "Usuario LAB01_OWNER creado con cuota limitada de 500 MB.",
            "Privilegios mínimos otorgados al usuario LAB01_OWNER.",
            "Acceso con LAB01_OWNER validado mediante SELECT USER FROM DUAL.",
            "Ninguna contraseña, wallet, OCID ni archivo de estado copiado al repositorio.",
        ),
    )

    document.add_heading("Recuperación ante desconexión de Cloud Shell", level=2)
    add_text(document, "Si Cloud Shell muestra Connection interrupted, no continúes un cambio de contraseña en curso. Selecciona reconnect, espera el prompt de shell, inicia una sesión SQLcl nueva y repite la conexión usando el wallet. Luego usa el flujo con ACCEPT y ALTER USER de esta sección. No repitas el comando PASSWORD de SQLcl para este caso.")

    document.add_heading("Restaurar el código de los laboratorios en Cloud Shell", level=2)
    add_text(document, "Si el directorio del proyecto no está disponible en Cloud Shell, carga el paquete de código aprobado mediante File transfers. El paquete debe contener solamente código, documentación y configuración de ejemplo; no debe incluir wallets, contraseñas, archivos .env, estados de Terraform ni datos de participantes.")
    add_text(document, "Antes de crear el entorno, confirma que Python 3.11 está disponible. Este repositorio declara >=3.11 y <3.12, por lo que Python 3.12 no es compatible.")
    add_code(document, "python3.11 --version\ncd \"$HOME\"\nunzip -q khipu-workshop-labs-source.zip -d khipu-workshop\ncd \"$HOME/khipu-workshop\"\npython3.11 -m venv .venv\nsource .venv/bin/activate\npython -m pip install --upgrade pip\npython -m pip install -e \".[lab01]\"")
    add_text(document, "El entorno .venv queda dentro del proyecto y no reutiliza un entorno creado con Python 3.12. Si la versión 3.11 no está disponible, detén el procedimiento y valida la imagen de Cloud Shell antes de cambiar las dependencias del repositorio.")

    document.add_heading("Estado de validación del Laboratorio 1", level=2)
    add_text(document, "La ADB está disponible. El wallet de instancia fue generado y descomprimido en un directorio privado de Cloud Shell. El usuario LAB01_OWNER fue creado con cuota limitada, recibió los privilegios mínimos y su conexión fue validada. El entorno del workshop debe usar Python 3.11.9 y el paquete oracleagentmemory versión 26.8.0 para los ejercicios de memoria.")

    document.add_heading("Inicializar y validar Oracle AI Agent Memory", level=1)
    add_text(document, "La validación utiliza SearchStrategy.KEYWORD y desactiva la extracción automática. Por ello, el ejercicio inicial no requiere un modelo de embeddings ni una llamada a OCI Generative AI. Su objetivo es demostrar memoria procedural persistente y recuperación acotada por equipo con datos completamente sintéticos.")

    document.add_heading("Hallazgo de privilegios en el Free Trial", level=2)
    add_text(document, "La creación del store con LAB01_OWNER fue rechazada con privilegios insuficientes por el paquete administrado de Agent Memory. El intento de otorgar la ejecución del paquete desde ADMIN también fue rechazado por la ADB. No se eliminaron ni se modificaron datos para resolverlo.")
    add_text(document, "Como excepción controlada y solo para confirmar la capacidad técnica del Free Trial, el store se creó con el esquema ADMIN después de una autorización explícita. Este no es el diseño que se usará en el tenant de Khipu ni en una implementación productiva.")

    document.add_heading("Inicializar el store del piloto", level=2)
    add_text(document, "Conéctate como el usuario que sea propietario del paquete y del store. En el Free Trial del piloto fue ADMIN. Para el tenant de Khipu se debe verificar previamente el modelo de propietario del paquete, la delegación de privilegios y el uso de un esquema dedicado de workshop.")
    add_text(document, "El inicializador usa CREATE_IF_EMPTY. Crea los objetos administrados solo cuando no existe un esquema de memoria; no repara, recrea ni elimina objetos existentes. Requiere una confirmación local antes de iniciar la creación.")
    add_code(document, "python labs/lab01_agent_memory/scripts/initialize_oci_memory.py")
    add_text(document, "Escribe CREATE solamente después de revisar el identificador del store y confirmar que el destino es el piloto. El resultado esperado es MEMORY_STORE_READY. El identificador debe tener entre 1 y 16 caracteres, comenzar con una letra y usar solo letras, números o guion bajo. Si el inicializador informa que hay objetos administrados existentes, no uses RECREATE: detén el procedimiento y realiza un preflight de esquema.")

    document.add_heading("Preparar una sesión repetible de Cloud Shell", level=2)
    add_text(document, "Cloud Shell puede reiniciar y no conserva las variables de la sesión. Desde la raíz del repositorio, el script auxiliar del Laboratorio 1 activa el entorno virtual existente, restaura el wallet privado solo si falta tnsnames.ora, selecciona un servicio de baja capacidad sin mostrar su nombre y configura valores no secretos. No muestra contraseñas, contenido de wallet, OCID ni cadenas de conexión.")
    add_code(document, "cd \"$HOME/khipu-workshop\"\nsource scripts/setup_lab01_cloudshell.sh")
    add_text(document, "La señal segura esperada es LAB01_SESSION_READY. En el Trial se usa ADMIN como valor por defecto únicamente para la validación descartable. Para el tenant de Khipu se debe definir LAB01_DB_USER con el esquema de workshop aprobado antes de ejecutar el script auxiliar.")

    document.add_heading("Cargar datos sintéticos y verificar aislamiento", level=2)
    add_text(document, "La prueba registra una guía procedural para Team A y otra para Team B. Luego consulta cada equipo con SearchScope(user_id=<team>). Este es el patrón recomendado para las búsquedas de cliente: el alcance de usuario es explícito y exacto.")
    add_code(document, "source scripts/setup_lab01_cloudshell.sh\npython labs/lab01_agent_memory/scripts/seed_oci_memory.py\npython labs/lab01_agent_memory/scripts/validate_oci_isolation.py")
    add_text(document, "Resultado validado en el piloto: TEAM_A_RESULT_COUNT fue 1, TEAM_A_ISOLATION_PASS fue True, TEAM_B_RESULT_COUNT fue 1 y TEAM_B_ISOLATION_PASS fue True. Cada respuesta contenía solamente la guía de su propio equipo. La prueba anterior, que fijaba además el alcance del agente, fue reemplazada por SearchScope(user_id=<team>) porque este es el patrón documentado y comprobado para esta recuperación de cliente.")

    document.add_heading("Presentar el Laboratorio 1 sin consola", level=2)
    add_text(document, "Khipu AI Memory Studio es la superficie principal para participantes. Se ejecuta localmente en un navegador y muestra las guías procedurales recuperadas, el límite entre equipos y una comparación visual de contexto. No recibe ni muestra wallet, contraseñas, OCID, connect strings ni otros secretos.")
    add_code(document, "python -m pip install -e \".[lab01,ui]\"\npython -m streamlit run labs/lab01_agent_memory/ui/app.py")
    add_text(document, "La interfaz diferencia el prompt que repite todas las reglas, el prompt compacto y el prompt más la memoria recuperada. Las métricas son estimaciones deterministas de diseño y no representan facturación OCI ni el costo completo del ciclo de memoria.")
    add_text(document, "Después de una validación OCI correcta, el facilitador genera un JSON de evidencia seguro. Al guardarlo localmente en artifacts/lab01/facilitator/, Khipu AI Memory Studio lo detecta automáticamente. El archivo contiene solo conteos, resultados booleanos, fecha y una marca explícita que confirma ausencia de secretos; no debe subirse a un repositorio público.")
    add_code(document, "source scripts/setup_lab01_cloudshell.sh\npython labs/lab01_agent_memory/scripts/validate_oci_isolation.py \\\n  --output-path artifacts/lab01/facilitator/oci-isolation-evidence.json")

    document.add_heading("Decisión para el tenant de Khipu", level=2)
    add_checklist(
        document,
        (
            "Confirmar el propietario del paquete DBMS_AGENT_MEMORY_STORE y las opciones autorizadas para delegar su uso.",
            "Crear un esquema dedicado del workshop solo si el modelo de privilegios de la ADB permite inicializar el store allí.",
            "Validar el seed y la búsqueda con SearchScope antes del primer día del workshop.",
            "Derivar user_id de la identidad autenticada de la aplicación, nunca de un campo libre controlado por el participante.",
            "Mantener la excepción ADMIN limitada al Free Trial personal y a datos sintéticos.",
        ),
    )

    document.add_heading("Validación del Laboratorio 2 RAG con evidencia", level=1)
    add_text(
        document,
        "El Laboratorio 2 demuestra que una aplicación de IA debe recuperar la versión solicitada del contrato antes de responder. La validación del piloto utilizó solamente dos contratos sintéticos, una versión v1 y una versión v2, sin documentos, datos ni credenciales de Khipu.",
    )

    document.add_heading("Resultado comprobado en Chicago", level=2)
    add_checklist(
        document,
        (
            "Se generaron embeddings para los dos contratos sintéticos y para una pregunta de migración, con la misma dimensión vectorial.",
            "La tabla dedicada LAB02_CONTRACT_CHUNKS almacenó un fragmento por versión con versión, sección, URI de origen, hash de contenido y vector.",
            "Una consulta por distancia coseno con filtro contract_version igual a v2 recuperó un solo fragmento: el contrato sintético de pagos v2.",
            "La validación confirmó que el filtro de versión se cumplió antes de ordenar por similitud.",
            "Un modelo de chat respondió solamente a partir del fragmento v2 recuperado; la aplicación adjuntó versión, URI de origen y sección desde los metadatos de ADB.",
        ),
    )
    add_text(
        document,
        "La prueba confirma la ingesta, la recuperación vectorial filtrada y una respuesta anclada. Para el tenant de Khipu se debe repetir la prueba con el modelo aprobado en su región y con sus políticas, red y esquema dedicado.",
    )

    document.add_heading("Crear la tabla vectorial sin borrar datos", level=2)
    add_text(
        document,
        "Conéctate al esquema dedicado del workshop mediante el wallet privado y ejecuta el script del repositorio con la dimensión aprobada. El script crea únicamente la tabla del Laboratorio 2 y su índice de metadatos. No contiene DROP ni TRUNCATE.",
    )
    add_code(document, "sql /nolog\nset cloudconfig <absolute-path-to-wallet.zip>\nconnect <lab2-owner>@<database-service>\n@labs/lab02_contract_rag/sql/01_create_contract_chunks.sql <approved-vector-dimension>")

    document.add_heading("Generar embeddings y cargar contratos", level=2)
    add_text(
        document,
        "La ingesta divide cada contrato por sección y conserva metadatos de versión y procedencia. Se usa SEARCH_DOCUMENT para los contratos y SEARCH_QUERY para la pregunta del participante. Ambos vectores deben provenir del mismo modelo aprobado y tener la misma dimensión.",
    )
    add_code(document, "oci generative-ai-inference embed-text-result embed-text --serving-mode <approved-embedding-model> --compartment-id <workshop-compartment-id> --input-type SEARCH_DOCUMENT --output-dimensions <approved-vector-dimension>")
    add_text(
        document,
        "La carga debe verificar el conteo por versión antes de continuar. El corpus se divide por secciones, de modo que contiene varios fragmentos trazables por versión. Si existen registros previos, el runner reutiliza solamente los que tengan el mismo identificador y hash de contenido; se detiene ante una colisión y no sobrescribe contenido.",
    )

    document.add_heading("Ejecutar la validación OCI repetible", level=2)
    add_text(
        document,
        "El repositorio incorpora un runner para la validación en vivo. Lee identificadores y rutas no secretas desde el archivo local .env, solicita de forma oculta la contraseña del esquema y del wallet, y guarda solo un informe de evidencia. El archivo .env no se versiona y no debe contener contraseñas.",
    )
    add_code(
        document,
        "Copy-Item .env.example .env\n# Complete only approved identifiers, connection settings, wallet path and vector dimension.\npython labs/lab02_contract_rag/scripts/run_live_validation.py `\n  --output-dir artifacts/lab02/team-01 `\n  --confirm-synthetic-load",
    )
    add_text(
        document,
        "El parámetro de confirmación representa la autorización explícita del facilitador para realizar inferencia y cargar únicamente los contratos sintéticos. El runner inserta solo fragmentos ausentes, no emite UPDATE, DELETE, DROP ni TRUNCATE, recupera la versión solicitada y escribe el resultado en artifacts/lab02/team-01/lab02-live-evidence.json.",
    )
    add_text(
        document,
        "La señal de aceptación en la terminal es VERSION_FILTER_PASS True. También se informa INSERTED_SYNTHETIC_CHUNKS, cuyo valor puede ser cero en una repetición segura, y la ruta del informe de evidencia.",
    )

    document.add_heading("Recuperar evidencia de la versión solicitada", level=2)
    add_text(
        document,
        "La consulta aplica el filtro de versión antes de seleccionar la evidencia más cercana. No es válido recuperar todas las versiones y decidir después cuál citar.",
    )
    add_code(document, "SELECT chunk_id, contract_version, source_uri, section_name\nFROM lab02_contract_chunks\nWHERE contract_version = 'v2'\nORDER BY VECTOR_DISTANCE(embedding, :query_vector, COSINE)\nFETCH FIRST 1 ROW ONLY;")
    add_text(
        document,
        "Para el corpus de dos documentos se usó distancia coseno exacta. No se requiere un índice vectorial aproximado para esta demostración. Si el corpus de Khipu crece, se debe medir latencia, precisión y volumen antes de evaluar un índice HNSW.",
    )

    document.add_heading("Formar una respuesta anclada", level=2)
    add_text(
        document,
        "El modelo de chat recibe únicamente el fragmento recuperado y una instrucción explícita de responder solo con ese contexto. La aplicación agrega la evidencia desde el resultado de ADB. Este control no depende de que el modelo reproduzca correctamente una URI o el nombre de una sección.",
    )
    add_code(document, '{"answer":"<model-answer>","evidence":[{"contract_version":"v2","source_uri":"<retrieved-source-uri>","section":"<retrieved-section>"}]}')
    add_text(
        document,
        "En el piloto, el modo de cita nativo del modelo de chat vigente no era compatible con la solicitud. El patrón de aplicación resolvió este límite sin perder trazabilidad: la respuesta textual se conserva separada de los metadatos de evidencia y estos se adjuntan de forma determinística.",
    )

    document.add_heading("Puerta de evidencia antes de la respuesta", level=2)
    add_checklist(
        document,
        (
            "El resultado contiene contract_version, source_uri y section_name.",
            "La versión del resultado coincide con la versión solicitada por la pregunta.",
            "El prompt de chat recibe solo los fragmentos recuperados; la aplicación adjunta versión, URI y sección desde los metadatos de evidencia.",
            "Una pregunta sin evidencia debe producir una respuesta de insuficiencia, no una inferencia.",
            "Solo se usan contratos sintéticos durante el workshop.",
        ),
    )

    document.add_heading("Validación del Laboratorio 3 Cambio seguro de API", level=1)
    add_text(
        document,
        "El Laboratorio 3 demuestra un flujo de ingeniería asistida por IA, pero controlado por personas y pruebas. El caso usa una API de pagos FastAPI completamente sintética. La versión v2 elimina paymentStatus, exige idempotencyKey y responde con HTTP 202 y el estado ACCEPTED. No ejecuta pagos, no despliega recursos y no utiliza código ni datos de Khipu.",
    )

    document.add_heading("Resultado comprobado localmente", level=2)
    add_checklist(
        document,
        (
            "El análisis determinista identificó tres impactos: eliminar paymentStatus, exigir idempotencyKey y cambiar la respuesta a una aceptación v2.",
            "El parche propuesto es pequeño y revisable; limita el cambio a un único endpoint sintético.",
            "Una solicitud v2 válida devuelve HTTP 202, estado ACCEPTED, payment_id y api_version igual a v2.",
            "Una solicitud sin idempotencyKey y otra con el campo heredado paymentStatus son rechazadas con HTTP 422.",
            "La suite integrada del repositorio completó 17 pruebas correctas, incluidas las cinco pruebas del Laboratorio 3.",
        ),
    )

    document.add_heading("Flujo de la sesión", level=2)
    add_text(
        document,
        "La sesión principal dura 140 minutos y reserva hasta 40 minutos para instalación, preguntas y contingencia. Primero el equipo compara el endpoint v1 con la especificación v2. Después puede usar un modelo de chat de OCI aprobado para preparar un borrador de análisis, pero ese resultado no es una aprobación ni una instrucción ejecutable. Finalmente el equipo compara el borrador con el análisis determinista, revisa el parche y ejecuta las pruebas de regresión.",
    )
    add_code(document, "python -m pip install -e \".[dev,lab01,lab03]\"\npython -m lab03_api_change.demo --output-dir artifacts/lab03/team-01\npython -m pytest labs/lab03_api_change/tests")

    document.add_heading("Controles del uso de IA", level=2)
    add_checklist(
        document,
        (
            "Entregar al modelo solamente el endpoint v1 y la especificación v2 sintéticos del repositorio.",
            "No incluir código de Khipu, contratos reales, credenciales, wallets, tokens ni información de clientes en el prompt.",
            "No permitir que el modelo haga commits, despliegues, llamadas a APIs ni aprobaciones de su propio parche.",
            "Aceptar el cambio solo después de una revisión humana y de pruebas de regresión exitosas.",
        ),
    )

    document.add_heading("Evidencia que debe conservar cada equipo", level=2)
    add_text(
        document,
        "Cada equipo debe conservar el informe de impactos generado en artifacts/lab03, el parche revisado y el resultado de las pruebas. Estos artefactos permiten explicar qué cambió, por qué era riesgoso y qué prueba evita una regresión. Los artefactos generados son de la práctica y no deben contener secretos ni datos productivos.",
    )

    document.add_heading("Runbook de preaprovisionamiento para el tenant de Khipu", level=1)
    add_text(
        document,
        "El entorno de Khipu no debe reproducir automáticamente el Free Trial. Antes de crear recursos se requiere una decisión del administrador de tenancy, de seguridad y red, del responsable de presupuesto, del propietario de base de datos y del líder del workshop. El runbook del repositorio convierte esas decisiones en una secuencia validable y reversible.",
    )

    document.add_heading("Modelo operativo recomendado", level=2)
    add_text(
        document,
        "La alternativa recomendada es un compartimento dedicado, una sola Autonomous AI Database del workshop y equipos de tres a cuatro personas. Cada equipo designa un runner para ejecutar comandos que requieran OCI o base de datos. El runner no es un administrador: usa un esquema propio del equipo, mientras que ADMIN, las políticas IAM y la operación de ADB permanecen en manos del facilitador autorizado.",
    )
    add_checklist(
        document,
        (
            "OCI Generative AI: grupo común de participantes con permiso use para chat y embeddings, más inspect para listar modelos.",
            "ADB: un usuario y esquema por equipo, por ejemplo KHIPU_WS_T01; así no hay colisión de tablas vectoriales entre equipos.",
            "AI Agent Memory: store administrado por facilitación hasta comprobar en el tenant de Khipu el propietario correcto y los privilegios requeridos.",
            "Object Storage: administrado por facilitación por defecto; la carga directa se habilita solo por grupo y prefijo de equipo aprobados.",
            "Laboratorio 3: repositorio FastAPI local y sintético; no requiere ADB, credenciales OCI ni acceso a repositorios productivos.",
        ),
    )

    document.add_heading("IAM con privilegio mínimo", level=2)
    add_text(
        document,
        "El módulo Terraform fue ajustado para que el grupo general de participantes no reciba permisos de Object Storage. Sus sentencias revisables permiten solo invocar chat y embeddings, e inspeccionar modelos. No permiten administrar ADB, IAM ni clústeres de IA dedicados.",
    )
    add_text(
        document,
        "Si Khipu aprueba que un equipo cargue documentos sintéticos directamente, se crea previamente un grupo de identidad exclusivo del equipo y se habilita una asignación team_object_access. La política resultante limita el bucket y un prefijo, por ejemplo team-01. Permite crear y leer objetos conocidos; no permite listar, sobrescribir ni borrar objetos. Un grupo común para todos los equipos no constituye aislamiento entre equipos.",
    )
    add_code(document, "allow group <team-group> to manage objects in compartment <workshop-compartment> where all {target.bucket.name='<workshop-bucket>', target.object.name='team-01/*', any{request.permission='OBJECT_CREATE', request.permission='OBJECT_READ'}}")

    document.add_heading("Preparar los esquemas por equipo", level=2)
    add_text(
        document,
        "El administrador de base de datos ejecuta el script no destructivo del repositorio una vez por equipo. El script pide la contraseña de manera interactiva, crea el usuario solo si no existe, asigna una cuota limitada de 512 MB y otorga únicamente CREATE SESSION, CREATE TABLE, CREATE INDEX y CREATE PROCEDURE. No restablece contraseñas ni elimina datos.",
    )
    add_code(document, "sql /nolog\nset cloudconfig <absolute-path-to-wallet.zip>\nconnect admin@<database-service>\n@platform/bootstrap/01_create_team_schema.sql T01")
    add_text(
        document,
        "La contraseña del equipo se entrega por un canal de secretos aprobado por Khipu solo a su runner. No se entrega la contraseña ADMIN. El wallet y cualquier contraseña quedan fuera de Git, chat, correo no protegido, Object Storage y prompts de IA. Cada equipo crea la tabla vectorial del Laboratorio 2 dentro de su propio esquema.",
    )

    document.add_heading("Decisión de red y credenciales", level=2)
    add_checklist(
        document,
        (
            "Con Cloud Shell y wallet mTLS: validar antes el canal de entrega seguro del wallet y la contraseña del esquema al runner de cada equipo.",
            "Con endpoint privado: validar conectividad desde el entorno real de los runners antes de crear la ADB para el evento.",
            "Sin acceso directo de participantes a ADB: usar la alternativa segura de facilitación, donde los equipos conducen el análisis y el facilitador ejecuta el paso vivo de base de datos.",
        ),
    )

    document.add_heading("Tiempos y puertas de ensayo", level=2)
    add_text(
        document,
        "Estimación de trabajo activo: entre 60 y 90 minutos para aprobaciones y decisiones; 45 minutos para preparar y revisar el plan Terraform; 60 minutos más 15 minutos por equipo para recursos y esquemas; dos horas para el ensayo completo; y entre 20 y 30 minutos de smoke test el día del workshop. Los tiempos excluyen esperas de aprobación y de aprovisionamiento de servicios.",
    )
    add_checklist(
        document,
        (
            "La región, el compartimento, las identidades, la red, el presupuesto y el modelo de credenciales están aprobados.",
            "Terraform valida y el plan muestra solamente los recursos y políticas aprobados.",
            "Los modelos de chat y embeddings aprobados están disponibles en la región elegida.",
            "La conexión ADB, los esquemas por equipo y el almacenamiento de documentos sintéticos fueron ensayados.",
            "Los tres laboratorios superan sus puertas de evidencia con datos sintéticos.",
            "Existe un responsable asignado para iniciar y detener la ADB en cada fecha del workshop, además de un responsable de reversión.",
        ),
    )

    document.add_heading("Operación y control de costos", level=1)
    add_text(document, "Para el piloto, la base de datos puede detenerse manualmente cuando no esté en uso. Al detener ADB se deja de consumir cómputo, aunque el almacenamiento continúa facturándose o consumiendo cuota según el tipo de cuenta.")
    add_text(document, "Antes de una sesión práctica, se debe iniciar la ADB y confirmar que alcance AVAILABLE antes de entregar acceso a los participantes.")
    add_code(document, "ADB_ID=$(../../../../bin/terraform output -raw autonomous_database_id)\noci db autonomous-database start --autonomous-database-id \"$ADB_ID\" --wait-for-state AVAILABLE")
    add_text(document, "Para detenerla nuevamente después de una práctica, usa el siguiente comando y espera la confirmación STOPPED.")
    add_code(document, "ADB_ID=$(../../../../bin/terraform output -raw autonomous_database_id)\noci db autonomous-database stop --autonomous-database-id \"$ADB_ID\" --wait-for-state STOPPED")
    add_text(document, "El estado de Terraform puede contener atributos sensibles. En este piloto permanece en Cloud Shell y no debe copiarse al repositorio, a un bucket público ni a herramientas de mensajería. Para el tenant de Khipu se recomienda definir backend remoto cifrado y un procedimiento formal de secretos con OCI Vault.")

    document.add_heading("Limpieza y reversión", level=1)
    add_text(document, "La destrucción del entorno elimina recursos del piloto y puede borrar datos. Solo debe ejecutarse con aprobación explícita, después de respaldar los artefactos que se deseen conservar.")
    add_code(document, "terraform plan -destroy\nterraform destroy")
    add_text(document, "No ejecutar estos comandos sobre un compartimento compartido ni sobre el tenant de Khipu sin validar el alcance del estado de Terraform.")

    document.add_heading("Próximos pasos para el workshop", level=1)
    add_bullet(document, "Iniciar la ADB antes de preparar el Laboratorio 2 y detenerla nuevamente mientras permanezca ociosa.")
    add_bullet(document, "Repetir la prueba completa del Laboratorio 2 en el tenant de Khipu con el modelo vigente y la política de red aprobada.")
    add_bullet(document, "Completar el laboratorio de AI Agent Memory con memoria procedural, aislamiento de contexto y comparación de tokens.")
    add_bullet(document, "Realizar un ensayo facilitado del Laboratorio 3 con el repositorio FastAPI sintético y confirmar que cada equipo puede ejecutar sus pruebas.")
    add_bullet(document, "Antes del evento, transformar este piloto en un runbook para el tenant de Khipu, incorporando grupos, políticas aprobadas, preaprovisionamiento y estrategia por equipos.")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    document.save(OUTPUT_PATH)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    build_document()
