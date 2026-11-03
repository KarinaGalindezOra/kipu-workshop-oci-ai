"""Append the verified Lab 1 secure-deployment procedure to the editable runbook."""

from __future__ import annotations

from docx import Document
from docx.enum.text import WD_BREAK
from docx.shared import Pt

DOCUMENT_PATH = "docs/procedimiento_aprovisionamiento_oci_workshop_khipu.docx"
SECTION_TITLE = "Actualización del Laboratorio 1 Despliegue seguro por equipo"


def add_code_block(document: Document, command: str) -> None:
    """Add one editable command paragraph with a readable monospaced font."""

    paragraph = document.add_paragraph()
    run = paragraph.add_run(command)
    run.font.name = "Consolas"
    run.font.size = Pt(9)


def add_bullet(document: Document, text: str) -> None:
    """Add a standard editable bullet using the document's existing style."""

    document.add_paragraph(text, style="List Bullet")


def main() -> None:
    """Update the procedure exactly once and preserve all prior sections."""

    document = Document(DOCUMENT_PATH)
    if any(paragraph.text.strip() == SECTION_TITLE for paragraph in document.paragraphs):
        return

    document.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    document.add_heading(SECTION_TITLE, level=1)
    document.add_paragraph(
        "El Laboratorio 1 incorpora un mecanismo de despliegue por equipo que se puede "
        "ensayar sin crear recursos OCI. El participante modifica y valida un bundle "
        "procedural sintético; el servicio decide el alcance desde una identidad verificada. "
        "El dashboard se mantiene como evidencia visual, no como sustituto del algoritmo "
        "ni de las pruebas."
    )

    document.add_heading("Estado verificado", level=2)
    add_bullet(
        document,
        "El algoritmo local recupera procedimientos solo dentro del alcance del equipo "
        "y la consulta cruzada devuelve cero resultados.",
    )
    add_bullet(
        document,
        "El gateway FastAPI de ensayo valida un token temporal y deriva el equipo en el "
        "servidor. No confía en un team_id escrito libremente por el cliente.",
    )
    add_bullet(
        document,
        "Un token de Payments no puede publicar un bundle declarado como Integrations y "
        "no puede recuperar los procedimientos de ese equipo.",
    )
    add_bullet(
        document,
        "El gateway está ligado a 127.0.0.1, no contiene credenciales OCI y no se conecta "
        "a Autonomous AI Database.",
    )

    document.add_heading("Ensayo local controlado por facilitación", level=2)
    document.add_paragraph(
        "Este ensayo es una validación técnica previa. El secreto de firma se configura "
        "solo en el entorno local del facilitador mediante un mecanismo aprobado. No se "
        "incluye en comandos, bundles, archivos compartidos, capturas de pantalla ni "
        "terminales de participantes."
    )
    document.add_paragraph("1. Instalar las dependencias necesarias en el entorno del facilitador.")
    add_code_block(document, 'python -m pip install -e ".[lab01,lab01-gateway,dev]"')
    document.add_paragraph(
        "2. Configurar LAB01_WORKSHOP_TOKEN_SECRET de forma segura en la sesión local del "
        "facilitador y confirmar que no queda en el repositorio ni en el historial de comandos."
    )
    document.add_paragraph("3. Iniciar el gateway únicamente en loopback.")
    add_code_block(document, "python -m lab01_agent_memory.deployment_api")
    document.add_paragraph(
        "4. Desde otra terminal del mismo facilitador, emitir un token temporal para el equipo "
        "que participará en el ensayo. El comando muestra el token, no el secreto de firma."
    )
    add_code_block(
        document,
        "python labs/lab01_agent_memory/scripts/issue_local_team_token.py --team-id team-payments",
    )
    document.add_paragraph(
        "5. Ejecutar la prueba automatizada que comprueba la publicación autorizada y el "
        "aislamiento entre equipos."
    )
    add_code_block(document, "python -m pytest labs/lab01_agent_memory/tests/test_deployment_api.py -q")
    document.add_paragraph(
        "Resultado esperado: dos pruebas correctas. Si una prueba falla, no se habilita "
        "ninguna publicación remota; se corrige primero la frontera de identidad."
    )

    document.add_heading("Puerta antes del despliegue remoto en Khipu", level=2)
    document.add_paragraph(
        "El gateway local no es un endpoint compartido del evento. La publicación hacia OCI "
        "permanece deshabilitada hasta que Khipu apruebe y se ensaye la identidad remota, el "
        "acceso del servicio a secretos, la conexión con el store de AI Agent Memory y la "
        "prueba de aislamiento end to end."
    )
    add_bullet(document, "Identidad remota de cada equipo definida y aprobada por Khipu.")
    add_bullet(document, "Credencial del servicio almacenada en OCI Vault y no distribuida a participantes.")
    add_bullet(document, "Memory store existente y aplicación configurada para exigirlo, sin creación concurrente.")
    add_bullet(document, "Prueba end to end con dos bundles sintéticos y evidencia de aislamiento bidireccional.")
    add_bullet(document, "Logs revisados para confirmar que no contienen secretos ni cadenas de conexión.")

    document.save(DOCUMENT_PATH)


if __name__ == "__main__":
    main()
