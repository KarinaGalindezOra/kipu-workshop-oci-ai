from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "propuesta-workshops-ia-oci-v2.docx"

NAVY = "17365D"
BLUE = "D9EAF7"
PALE_BLUE = "F4F8FC"
GRID = "D9D9D9"
BLACK = RGBColor(0, 0, 0)


def set_cell_shading(cell, fill: str) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, color: str = GRID) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:color"), color)


def set_cell_margins(cell, top: int = 110, start: int = 130, bottom: int = 110, end: int = 130) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
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


def set_repeat_table_header(row) -> None:
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_run_font(run, size: float, bold: bool = False, color=BLACK) -> None:
    run.font.name = "Aptos"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color


def add_body_paragraph(doc, text: str, *, space_after: int = 8) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.space_after = Pt(space_after)
    paragraph.paragraph_format.line_spacing = 1.15
    set_run_font(paragraph.add_run(text), 10.5)


def add_bullets(doc, items: list[str]) -> None:
    for item in items:
        paragraph = doc.add_paragraph(style="List Bullet")
        paragraph.paragraph_format.space_after = Pt(4)
        paragraph.paragraph_format.line_spacing = 1.08
        set_run_font(paragraph.add_run(item), 10.25)


def add_heading(doc, text: str, level: int) -> None:
    paragraph = doc.add_paragraph(style=f"Heading {level}")
    paragraph.paragraph_format.space_before = Pt(15 if level == 1 else 9)
    paragraph.paragraph_format.space_after = Pt(6)
    set_run_font(paragraph.add_run(text), 15 if level == 1 else 11.5, bold=True)


def add_workshop(doc, number: int, title: str, objective: str, activities: list[str], outcome: str, message: str) -> None:
    add_heading(doc, f"Workshop {number}  {title}", 1)

    add_heading(doc, "Objetivo", 2)
    add_body_paragraph(doc, objective)

    add_heading(doc, "Qué harán los participantes", 2)
    add_bullets(doc, activities)

    add_heading(doc, "Resultado esperado", 2)
    add_body_paragraph(doc, outcome)

    add_heading(doc, "Mensaje clave", 2)
    add_body_paragraph(doc, message, space_after=10)


def configure_styles(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(10.5)

    for name in ("Title", "Heading 1", "Heading 2"):
        style = doc.styles[name]
        style.font.name = "Aptos"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
        style.font.color.rgb = BLACK

    if "Small Caption" not in doc.styles:
        caption = doc.styles.add_style("Small Caption", WD_STYLE_TYPE.PARAGRAPH)
        caption.font.name = "Aptos"
        caption.font.size = Pt(9)
        caption.font.color.rgb = RGBColor(80, 80, 80)


def add_footer(section) -> None:
    footer = section.footer
    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    paragraph.paragraph_format.space_before = Pt(0)
    run = paragraph.add_run("Propuesta de workshops de IA empresarial en OCI")
    set_run_font(run, 8, color=RGBColor(90, 90, 90))


def build_document() -> None:
    doc = Document()
    configure_styles(doc)
    section = doc.sections[0]
    section.top_margin = Inches(0.78)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.82)
    section.right_margin = Inches(0.82)
    add_footer(section)

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.LEFT
    title.paragraph_format.space_after = Pt(14)
    set_run_font(title.add_run("Propuesta de workshops de IA empresarial en OCI"), 24, bold=True)

    intro = doc.add_paragraph()
    intro.paragraph_format.space_after = Pt(13)
    intro.paragraph_format.line_spacing = 1.2
    set_run_font(
        intro.add_run(
            "Propuesta de tres sesiones técnicas e independientes para expertos en inteligencia artificial, "
            "desarrolladores y arquitectos. Cada workshop puede cursarse de forma autónoma; en conjunto, "
            "ofrecen una ruta opcional que va desde el contexto y la memoria, hacia los datos empresariales "
            "y la construcción de agentes API-first en OCI."
        ),
        11,
    )

    overview = doc.add_table(rows=1, cols=3)
    overview.autofit = False
    overview.columns[0].width = Inches(1.78)
    overview.columns[1].width = Inches(2.45)
    overview.columns[2].width = Inches(2.95)
    headers = ["Workshop", "Enfoque", "Resultado"]
    for cell, text in zip(overview.rows[0].cells, headers):
        set_cell_shading(cell, NAVY)
        set_cell_border(cell)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_run_font(p.add_run(text), 9.5, bold=True, color=RGBColor(255, 255, 255))
    set_repeat_table_header(overview.rows[0])

    rows = [
        ("1  Memoria", "Memoria procedural, contexto y tokens", "Evidencia OCI de recuperación aislada y tokens reales"),
        ("2  Datos", "Agentes con Autonomous AI Database y AI Vector Search", "Agente RAG con evidencia y trazabilidad"),
        ("3  Agentes", "OCI Generative AI Responses API y herramientas", "Agente API-first con salida estructurada y validación"),
    ]
    for index, row_values in enumerate(rows):
        row = overview.add_row()
        for cell, text in zip(row.cells, row_values):
            if index % 2 == 1:
                set_cell_shading(cell, PALE_BLUE)
            set_cell_border(cell)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            set_run_font(p.add_run(text), 9.2, bold=(cell is row.cells[0]))

    add_body_paragraph(
        doc,
        "Todos los ejercicios se realizan con datos sintéticos. No requieren usar código, documentación, "
        "credenciales ni información de producción del cliente.",
        space_after=12,
    )

    add_workshop(
        doc,
        1,
        "Economía de Tokens y Memoria de Decisiones en OCI",
        "Diseñar y validar una memoria procedural para agentes que reutilice decisiones de ingeniería, "
        "evite repetir contexto innecesario en los prompts y demuestre con telemetría de OCI Generative AI "
        "la reducción real de tokens de entrada por participante y equipo.",
        [
            "Persistir procedimientos sintéticos mediante Oracle AI Agent Memory SDK sobre Autonomous Database.",
            "Recuperar solo la regla relevante desde un alcance individual o compartido.",
            "Ejecutar dos inferencias reales y comparar los tokens, la latencia y la calidad reportados por OCI.",
            "Validar que un alcance de control no aparezca en la recuperación del participante.",
            "Generar evidencia de persistencia, recuperación, aislamiento y reducción real de tokens de entrada.",
        ],
        "Cada participante obtiene evidencia técnica de que la memoria procedural persiste en Autonomous Database, "
        "recupera la regla correcta dentro de su alcance y reduce tokens de entrada reportados por OCI Generative AI "
        "sin perder el comportamiento esperado.",
        "Los agentes no deben repetir todo el contexto ni recordar todo indiscriminadamente. La memoria debe ser "
        "específica, recuperable y delimitada por identidad y propósito; la reducción se demuestra con telemetría "
        "del proveedor, no con una estimación local.",
    )

    add_workshop(
        doc,
        2,
        "Agentes con Autonomous AI Database y AI Vector Search",
        "Construir un agente dentro de Autonomous AI Database que combine Select AI Agent, AI Vector Search, "
        "metadatos y datos empresariales para responder con evidencia y aplicar el patrón adecuado a información "
        "documental y estructurada.",
        [
            "Cargar documentos sintéticos versionados y fragmentarlos con metadatos de fuente, versión y sección.",
            "Generar embeddings y almacenar vectores en Autonomous AI Database.",
            "Recuperar fragmentos relevantes mediante AI Vector Search y filtros de metadatos.",
            "Construir un flujo RAG que responda con referencias a la evidencia recuperada.",
            "Distinguir cuándo el agente debe recuperar conocimiento documental y cuándo consultar datos estructurados mediante SQL controlado.",
        ],
        "Cada equipo obtiene un agente RAG que responde sobre información sintética versionada, cita su fuente y "
        "declara explícitamente cuando la evidencia disponible no permite una respuesta confiable.",
        "El valor de un agente empresarial no depende solo del modelo: depende de su capacidad para encontrar datos "
        "actuales, trazables y gobernados sin inventar información.",
    )

    add_workshop(
        doc,
        3,
        "Agentes API First con OCI Generative AI",
        "Implementar un agente API-first mediante OCI Generative AI Responses API que utilice una herramienta "
        "controlada, produzca una salida estructurada y sea validado antes de aceptar su resultado.",
        [
            "Ejecutar un agente base desde Python mediante OCI Generative AI Responses API.",
            "Definir instrucciones, límites de comportamiento y el formato esperado de la respuesta.",
            "Incorporar una única herramienta mediante Function Calling para consultar una especificación sintética aprobada.",
            "Observar el ciclo de decisión del agente: solicitud, llamada a herramienta, resultado y respuesta final.",
            "Generar un plan de cambio como JSON estructurado y validarlo contra especificaciones y pruebas de regresión.",
            "Ejecutar un caso negativo para comprobar que el agente no propone cambios sin evidencia suficiente.",
        ],
        "Cada equipo termina con un flujo de ingeniería asistido por IA que entrega una propuesta de cambio revisable, "
        "con evidencia y pruebas ejecutables, además de criterios para adoptar agentes API-first en OCI.",
        "La salida del modelo es un borrador. La aceptación depende de herramientas controladas, evidencia, revisión humana y pruebas automatizadas.",
    )

    add_heading(doc, "Resultado de la ruta completa", 1)
    add_body_paragraph(
        doc,
        "Al completar los tres workshops, los participantes podrán diseñar soluciones de IA empresarial en OCI que "
        "administren contexto de forma eficiente, usen datos empresariales con trazabilidad y construyan agentes con "
        "herramientas y controles de ingeniería verificables.",
    )

    for section in doc.sections:
        add_footer(section)
    doc.core_properties.title = "Propuesta de workshops de IA empresarial en OCI"
    doc.core_properties.subject = "Objetivos y actividades de los workshops OCI"
    doc.core_properties.author = "Oracle"
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build_document()
