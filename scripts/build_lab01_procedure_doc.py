"""Build the editable Spanish operating procedure for the Lab 1 rehearsal."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "procedimiento_aprovisionamiento_oci_workshop_khipu.docx"

DARK_BLUE = "17365D"
MID_BLUE = "D9EAF7"
PALE_BLUE = "F3F8FC"
LIGHT_GRAY = "D9D9D9"
BLACK = RGBColor(0, 0, 0)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    tc_pr.append(shading)


def set_cell_margins(cell, top: int = 100, start: int = 120, bottom: int = 100, end: int = 120) -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_border(cell, color: str = LIGHT_GRAY) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = qn(f"w:{edge}")
        element = borders.find(tag)
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def set_column_width(cell, width_cm: float) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(width_cm * 567)))
    tc_w.set(qn("w:type"), "dxa")


def set_font(run, size: float | None = None, bold: bool | None = None, color=BLACK) -> None:
    run.font.name = "Aptos"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    if size is not None:
        run.font.size = Pt(size)
    if bold is not None:
        run.bold = bold
    run.font.color.rgb = color


def add_text(paragraph, text: str, *, bold: bool = False, size: float = 10.5) -> None:
    run = paragraph.add_run(text)
    set_font(run, size=size, bold=bold)


def add_paragraph(doc: Document, text: str = "", *, before: float = 0, after: float = 6, bold_lead: str | None = None) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.12
    if bold_lead and text.startswith(bold_lead):
        add_text(paragraph, bold_lead, bold=True)
        add_text(paragraph, text[len(bold_lead) :])
    else:
        add_text(paragraph, text)


def add_bullet(doc: Document, text: str, level: int = 0) -> None:
    paragraph = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    paragraph.paragraph_format.space_after = Pt(2)
    paragraph.paragraph_format.line_spacing = 1.05
    add_text(paragraph, text, size=10.2)


def add_number(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph(style="List Number")
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.line_spacing = 1.05
    add_text(paragraph, text, size=10.2)


def add_heading(doc: Document, text: str, level: int = 1) -> None:
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    paragraph.paragraph_format.space_before = Pt(13 if level == 1 else 9)
    paragraph.paragraph_format.space_after = Pt(5)
    run = paragraph.add_run(text)
    set_font(run, size=15 if level == 1 else 12.5, bold=True)


def add_code(doc: Document, code: str) -> None:
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    cell = table.cell(0, 0)
    set_cell_shading(cell, PALE_BLUE)
    set_cell_border(cell, "B7C9D6")
    set_cell_margins(cell, top=120, start=150, bottom=120, end=150)
    paragraph = cell.paragraphs[0]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0
    run = paragraph.add_run(code)
    run.font.name = "Consolas"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Consolas")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Consolas")
    run.font.size = Pt(8.7)
    run.font.color.rgb = BLACK
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def add_table(doc: Document, headers: list[str], rows: list[list[str]], widths: list[float]) -> None:
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    table.style = "Table Grid"
    header_row = table.rows[0]
    set_repeat_table_header(header_row)
    for index, heading in enumerate(headers):
        cell = header_row.cells[index]
        set_column_width(cell, widths[index])
        set_cell_shading(cell, DARK_BLUE)
        set_cell_border(cell)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_text(paragraph, heading, bold=True, size=9.2)
        paragraph.runs[0].font.color.rgb = RGBColor(255, 255, 255)
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(row):
            cell = cells[index]
            set_column_width(cell, widths[index])
            set_cell_border(cell)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if row_index % 2 == 1:
                set_cell_shading(cell, PALE_BLUE)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.03
            if index == 0 and len(value) < 24:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_text(paragraph, value, size=8.9)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def add_checkbox(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.left_indent = Cm(0.2)
    add_text(paragraph, "☐ ", size=10.5)
    add_text(paragraph, text, size=10.2)


def build_document() -> None:
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(1.8)
    section.bottom_margin = Cm(1.6)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(10.5)
    for name in ("Title", "Heading 1", "Heading 2"):
        style = styles[name]
        style.font.name = "Aptos"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
        style.font.color.rgb = BLACK

    footer = section.footer
    footer_paragraph = footer.paragraphs[0]
    footer_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer_paragraph.paragraph_format.space_before = Pt(5)
    add_text(footer_paragraph, "Khipu OCI AI Workshop  |  Laboratorio 1  |  Procedimiento de operación", size=8.2)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title.paragraph_format.space_after = Pt(8)
    run = title.add_run("Procedimiento de Laboratorio 1 Memoria Procedural en OCI")
    set_font(run, size=22, bold=True)
    subtitle = doc.add_paragraph()
    subtitle.paragraph_format.space_after = Pt(16)
    add_text(subtitle, "Aprovisionamiento, ejecución y validación con Oracle AI Agent Memory SDK y Autonomous AI Database", size=12.2)

    add_paragraph(
        doc,
        "Este procedimiento permite preparar y ejecutar el Laboratorio 1 del workshop de Khipu de forma controlada. El resultado que deben obtener los participantes es una prueba real: persisten reglas procedurales sintéticas en Oracle AI Agent Memory, las recuperan desde Autonomous AI Database y verifican que un alcance de control no se expone al alcance individual.",
        after=8,
    )
    add_paragraph(
        doc,
        "Decisión operativa: un trial desechable por equipo, una Autonomous AI Database y un memory store administrado por equipo. Cada participante usa su propio computador o Cloud Shell y su usuario temporal de aplicación. No se usa el tenant productivo de Khipu.",
        bold_lead="Decisión operativa: ",
        after=12,
    )

    add_heading(doc, "1 Resultado y límites del laboratorio")
    add_table(
        doc,
        ["Aspecto", "Qué se demuestra", "Límite explícito"],
        [
            ["Memoria procedural", "`add_memory` crea registros `guideline` con reglas sintéticas de ingeniería.", "No se almacenan conversaciones reales ni información de Khipu."],
            ["Recuperación", "`search` usa `user_id` exacto, `KEYWORD` y `record_types=[\"guideline\"]`.", "El alcance recupera contexto; por sí solo no es una política de autorización de producción."],
            ["Persistencia", "Una segunda ejecución encuentra procedimientos existentes en ADB sin duplicarlos.", "La evidencia JSON no contiene contraseñas, wallets ni cadenas de conexión."],
            ["Aislamiento", "El alcance individual no recupera la regla sembrada en el alcance de control.", "La producción requiere identidad autenticada, IAM, red y controles adicionales de base de datos."],
        ],
        [3.0, 7.2, 7.2],
    )

    add_heading(doc, "2 Modelo de operación por equipo")
    add_table(
        doc,
        ["Rol", "Responsabilidad", "Separación de funciones"],
        [
            ["Facilitadora", "Crea el trial, aprueba el plan de infraestructura y realiza el ensayo previo.", "No comparte credenciales administrativas ni opera como participante."],
            ["Memory owner", "Instala el paquete oficial de Agent Memory, crea el store una vez y concede acceso de runtime mínimo.", "No entrega su contraseña ni ejecuta el ejercicio como participante."],
            ["Participante", "Ejecuta Python y el SDK desde su estación, modifica reglas sintéticas y genera evidencia.", "No crea objetos, no usa `ADMIN` y no ejecuta Terraform en el día del laboratorio."],
            ["Equipo", "Comparte solo el alcance `TNN:shared` cuando la facilitadora lo indica.", "Cada integrante conserva su terminal y su usuario temporal."],
        ],
        [2.6, 7.0, 7.8],
    )

    add_heading(doc, "3 Preparación previa de la plataforma")
    add_paragraph(doc, "Esta sección se ejecuta antes del workshop por una persona autorizada. La creación de Autonomous AI Database, las políticas IAM y cualquier `terraform apply` requieren aprobación explícita del propietario del trial.")

    add_heading(doc, "3.1 Validar y aplicar infraestructura aprobada", level=2)
    add_number(doc, "Crear un trial desechable por equipo y confirmar región, crédito disponible, número de equipo, etiquetas requeridas y método de distribución segura del wallet.")
    add_number(doc, "En el repositorio, configurar los valores aprobados en el perfil `terraform/environments/trial-team`. El plan inicial debe mostrar únicamente los recursos autorizados.")
    add_number(doc, "Revisar el plan con el responsable del trial. Habilitar ADB solo cuando se haya aprobado presupuesto y configuración. No incluir contraseñas ni wallets en archivos de Terraform.")
    add_code(doc, "terraform -chdir=terraform/environments/trial-team init\nterraform -chdir=terraform/environments/trial-team fmt\nterraform -chdir=terraform/environments/trial-team validate\nterraform -chdir=terraform/environments/trial-team plan")

    add_heading(doc, "3.2 Descargar y custodiar el wallet", level=2)
    add_paragraph(doc, "Descargar el wallet mTLS desde la consola de Autonomous AI Database una vez creada la base. La consola puede solicitar o generar una contraseña de wallet; se entrega solo por un canal privado aprobado. El archivo no entra al repositorio, al ZIP de código, al dashboard ni a Object Storage público.")
    add_bullet(doc, "Crear una carpeta privada por participante o por equipo, según el método de entrega aprobado.")
    add_bullet(doc, "Conservar el archivo `tnsnames.ora` dentro del wallet. El script de sesión selecciona un alias de baja capacidad sin imprimir la cadena de conexión.")
    add_bullet(doc, "Nunca pegar contraseña, contenido del wallet, OCID ni alias completo en una grabación, chat o evidencia.")

    add_heading(doc, "3.3 Crear propietarios y usuarios temporales", level=2)
    add_paragraph(doc, "Conéctate como administrador de ADB y ejecuta los scripts SQL una vez por equipo y una vez por participante. Los scripts solicitan las contraseñas de manera interactiva. Sustituye los códigos con los asignados por el workshop.")
    add_code(doc, "@platform/bootstrap/02_create_agent_memory_owner.sql T01\n@platform/bootstrap/03_create_agent_memory_application_user.sql T01 P01\n@platform/bootstrap/03_create_agent_memory_application_user.sql T01 P02")
    add_paragraph(doc, "El usuario de aplicación es temporal y no es el propietario del esquema. El participante no recibe privilegios de creación de objetos ni privilegios administrativos de ADB.")

    add_heading(doc, "3.4 Inicializar el store con el memory owner", level=2)
    add_paragraph(doc, "Prepara una sesión privada del owner con el wallet, usuario propietario, identificador de store y DSN. Desde esa sesión, ejecuta el bootstrap una única vez. El script usa la implementación oficial para instalar el paquete de memoria en el esquema owner y luego usa `SchemaPolicy.CREATE_IF_NECESSARY` solo en esta etapa de plataforma.")
    add_code(doc, "python labs/lab01_agent_memory/scripts/bootstrap_team_memory.py --team-code T01")
    add_paragraph(doc, "El script solicita la confirmación `BOOTSTRAP`, la contraseña del owner y la contraseña del wallet. El resultado esperado incluye que el store de control existe o fue creado y finaliza con `LAB01_TEAM_MEMORY_READY`.")

    add_heading(doc, "3.5 Conceder acceso mínimo de runtime", level=2)
    add_paragraph(doc, "Como memory owner, ejecuta el siguiente script por cada usuario temporal de aplicación. El script no crea objetos ni escribe datos; concede exclusivamente los permisos necesarios para operar un store ya existente.")
    add_code(doc, "@platform/bootstrap/04_grant_agent_memory_runtime_access.sql <APPLICATION_USER> <MEMORY_STORE_ID>")
    add_table(
        doc,
        ["Permiso concedido", "Motivo", "No se concede"],
        [
            ["DML en tablas administradas del store", "Permite que el SDK persista y consulte las `guideline` del ejercicio.", "`CREATE`, `ALTER`, `DROP` o administración de ADB."],
            ["`EXECUTE` en `DBMS_AGENT_MEMORY_STORE`", "Permite validar y usar el paquete público de runtime.", "Acceso al paquete interno o instalación por el participante."],
            ["`SELECT` en `AGENT_MEMORY_STORES`", "Permite validar el registro del store owner con `REQUIRE_EXISTING`.", "Administración o modificación del registro."],
            ["Lectura del property graph del store", "Permite la recuperación administrada por Agent Memory.", "Acceso a stores de otros equipos."],
        ],
        [4.2, 7.4, 5.8],
    )

    add_heading(doc, "4 Preparación del participante")
    add_paragraph(doc, "El participante no realiza los pasos de plataforma. Recibe por canal privado un wallet, un usuario temporal, sus contraseñas y un archivo de sesión que contiene únicamente valores no secretos. Cada persona trabaja desde su propio computador o desde una sesión personal de Cloud Shell.")
    add_heading(doc, "4.1 Archivo privado de sesión", level=2)
    add_code(doc, "export LAB01_WALLET_DIR=\"<private_wallet_directory>\"\nexport LAB01_DB_USER=\"<assigned_application_user>\"\nexport LAB01_MEMORY_SCHEMA_OWNER=\"<team_memory_owner>\"\nexport LAB01_MEMORY_STORE_ID=\"<team_memory_store_name>\"")
    add_paragraph(doc, "LAB01_MEMORY_STORE_ID is the logical Agent Memory store name (MEMORY_STORE_NAME in ADB), not the internal MEMORY_STORE_UID. The value must have at most 16 letters, numbers, or underscores and start with a letter.")
    add_paragraph(doc, "La persona facilitadora configura `LAB01_DB_DSN` desde un alias del wallet durante la preparación. No se publica ni se añade al archivo de evidencia. El participante carga la sesión y ejecuta la comprobación sin mostrar los valores sensibles.")
    add_code(doc, "source <private_team_session_file>\nsource scripts/setup_lab01_cloudshell.sh")
    add_paragraph(doc, "Resultado esperado: `LAB01_SESSION_READY`, `LAB01_VENV_ACTIVE true`, `LAB01_WALLET_READY true` y `LAB01_MEMORY_STORE_READY true`.")

    add_heading(doc, "4.2 Instalar dependencias y revisar el algoritmo", level=2)
    add_paragraph(doc, "Los siguientes comandos se ejecutan en la copia local del repositorio. Las pruebas son locales y no crean recursos OCI.")
    add_code(doc, "python3.11 -m venv .venv\nsource .venv/bin/activate\npython -m pip install --upgrade pip\npython -m pip install -e '.[lab01,dev,ui]'\npython -m pytest labs/lab01_agent_memory/tests -q")
    add_paragraph(doc, "Antes de ejecutar, revisa `sdk_exercise.py` y `run_participant_sdk_lab.py`. La secuencia real es: abrir un pool mTLS como usuario de aplicación, construir `OracleAgentMemory` con `SchemaPolicy.REQUIRE_EXISTING`, persistir con `add_memory(..., memory_type=\"guideline\")` y recuperar con búsqueda `KEYWORD`, `user_id` exacto y `record_types=[\"guideline\"]`.")

    add_heading(doc, "5 Ejecución real del SDK")
    add_paragraph(doc, "Cada participante ejecuta el mismo programa con su código de equipo y código personal. El programa solicita la contraseña de base de datos y la del wallet de forma oculta. La salida solo escribe un JSON de evidencia seguro.")
    add_code(doc, "python labs/lab01_agent_memory/scripts/run_participant_sdk_lab.py \\\n  --bundle labs/lab01_agent_memory/exercises/team_payments_memory.json \\\n  --team-code T01 \\\n  --participant-code P01 \\\n  --output-path artifacts/lab01/t01/p01/oci-sdk-evidence.json")
    add_table(
        doc,
        ["Señal", "Interpretación"],
        [
            ["`LAB01_OCI_SDK_READY`", "El runner creó la conexión mTLS y ejecutó el SDK."],
            ["`SCHEMA_POLICY REQUIRE_EXISTING`", "El usuario de aplicación usó un store creado por el owner; no puede inicializar objetos."],
            ["`SEARCH_STRATEGY KEYWORD`", "La recuperación usa coincidencia de palabras clave, sin requerir embeddings en Lab 1."],
            ["`INDIVIDUAL_CREATED` / `INDIVIDUAL_EXISTING`", "La primera ejecución crea reglas; la repetición identifica las reglas persistidas y evita duplicados."],
            ["`PERSISTENCE_CONFIRMED True`", "La lista del SDK encuentra en ADB todas las reglas del bundle en el alcance individual."],
            ["`ISOLATION_PASS True`", "La consulta de control no recupera contenido desde el alcance individual."],
        ],
        [5.0, 12.4],
    )
    add_paragraph(doc, "La evidencia de la versión final también exige que la recuperación tenga al menos una regla `guideline`. Esto evita presentar una conexión exitosa pero una búsqueda vacía como un resultado válido.")

    add_heading(doc, "6 Variación didáctica y alcance compartido")
    add_number(doc, "Modificar una regla sintética del bundle, por ejemplo agregando una condición de evolución de esquema a la regla de compatibilidad.")
    add_number(doc, "Cambiar la consulta primaria a `api schema evolution` y repetir la ejecución. Confirmar que la regla recuperada corresponde al tipo `guideline`.")
    add_number(doc, "Cuando la facilitadora lo indique, publicar el bundle en el alcance compartido del equipo. Cada participante puede ejecutar desde su propia terminal; las inserciones son idempotentes.")
    add_code(doc, "python labs/lab01_agent_memory/scripts/run_participant_sdk_lab.py \\\n  --bundle labs/lab01_agent_memory/exercises/team_payments_memory.json \\\n  --team-code T01 \\\n  --participant-code P01 \\\n  --publish-to-team-scope \\\n  --output-path artifacts/lab01/t01/p01/oci-sdk-evidence.json")
    add_paragraph(doc, "El alcance `T01:shared` es conocimiento reutilizable del equipo. No es una sustitución de autorización. En la alternativa de un trial individual se conserva exactamente el mismo código: se asigna un equipo de una persona y se usa un código único de participante.")

    add_heading(doc, "7 Visualización y conversación de valor")
    add_paragraph(doc, "El dashboard Streamlit no reemplaza el SDK; consume el JSON que el SDK ya produjo. Se ejecuta desde el computador local, no desde Cloud Shell, para que el participante pueda abrir una interfaz visual y cargar su evidencia.")
    add_code(doc, "python -m streamlit run labs/lab01_agent_memory/ui/app.py")
    add_bullet(doc, "Mostrar los procedimientos recuperados y persistidos, sin contenido de credenciales.")
    add_bullet(doc, "Mostrar `REQUIRE_EXISTING`, `KEYWORD` y el tipo procedural `guideline`.")
    add_bullet(doc, "Mostrar la frontera individual, compartida y de control, con cero resultados cruzados.")
    add_bullet(doc, "Explicar la métrica de tokens como estimación de diseño de contexto; no es una factura OCI ni incluye todos los costos de operación.")

    add_heading(doc, "8 Guion sugerido de 180 minutos")
    add_table(
        doc,
        ["Minutos", "Actividad", "Evidencia observable"],
        [
            ["0 a 30", "Marco de Agent Memory, ADB y memoria procedural.", "Regla repetida identificada en un prompt base."],
            ["30 a 50", "Lectura del algoritmo y pruebas locales.", "Pruebas del repositorio aprobadas."],
            ["50 a 60", "Carga de sesión privada y chequeo de entorno.", "`LAB01_SESSION_READY`."],
            ["60 a 95", "Ejecución individual de `OracleAgentMemory`.", "Evidencia SDK, persistencia y recuperación de `guideline`."],
            ["95 a 120", "Cambio de una regla y repetición idempotente.", "Creados versus existentes y regla actualizada."],
            ["120 a 140", "Prueba de aislamiento contra el alcance de control.", "`ISOLATION_PASS True`."],
            ["140 a 160", "Publicación opcional al alcance compartido.", "Conteo compartido y discusión de gobernanza."],
            ["160 a 180", "Carga de evidencia en dashboard y cierre.", "Memoria real, límites de seguridad y estimación de contexto."],
        ],
        [2.0, 8.0, 7.4],
    )

    add_heading(doc, "9 Validación y resolución segura de incidencias")
    add_table(
        doc,
        ["Señal", "Diagnóstico probable", "Acción segura"],
        [
            ["Falla antes de crear `OracleAgentMemory`", "Ruta del wallet, DSN o sesión privada incompleta.", "Revisar el material privado con la facilitadora. No pedir que se publique el wallet."],
            ["Error de store o paquete", "Falta el bootstrap del owner o un grant de runtime.", "El owner valida el paquete público, DML administrado y acceso de lectura al registro del store."],
            ["Persistencia true y recuperación vacía", "Consulta no coincide con la regla o no se filtró el tipo procedural.", "Confirmar `record_types=[\"guideline\"]`, contenido del bundle y consulta."],
            ["Aislamiento false", "Código, alcance o bundle incorrecto.", "Detener la publicación compartida; revisar solo datos sintéticos y no continuar hasta corregir."],
            ["Error de credencial", "Contraseña de aplicación o wallet incorrecta o expirada.", "La facilitadora rota o reentrega el secreto por canal aprobado; no registrar el valor."],
        ],
        [4.2, 6.8, 6.4],
    )

    add_heading(doc, "10 Lista de salida y limpieza")
    for item in (
        "Cada participante conserva solo su JSON de evidencia sin secretos.",
        "La facilitadora verifica `PERSISTENCE_CONFIRMED True`, recuperación de `guideline` e `ISOLATION_PASS True` de al menos una ejecución por equipo.",
        "Las contraseñas temporales y wallets se retiran o invalidan al cierre mediante el responsable autorizado.",
        "La pausa, reanudación o destrucción de ADB se coordina fuera de la sesión y requiere aprobación explícita. No se ejecuta limpieza destructiva durante el laboratorio.",
        "El paquete de código, Terraform y la evidencia se revisan antes de reutilizarlos en otro trial o en el tenant de Khipu.",
    ):
        add_checkbox(doc, item)

    doc.core_properties.title = "Procedimiento de Laboratorio 1 Memoria Procedural en OCI"
    doc.core_properties.subject = "Khipu OCI AI Workshop Lab 1"
    doc.core_properties.author = "Khipu OCI AI Workshop"
    doc.core_properties.comments = "Editable operational procedure"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)


if __name__ == "__main__":
    build_document()
