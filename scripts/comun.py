"""Funciones compartidas por los scripts del taller. No hace falta tocar este archivo."""
import hashlib
import json
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True

RAIZ = Path(__file__).resolve().parent.parent
TALLER = "rkd-taller-0710"            # etiqueta que usa la galería para encontrar los agentes
NOMBRE_ENTORNO = "taller-rkd-0710"    # entorno compartido por todos los agentes del taller
CARPETA_DEFAULT = RAIZ / "mi-agente"  # carpeta de trabajo de cada participante (ignorada por git)
RUTA_CONOCIMIENTO = "/mnt/session/uploads/conocimiento"
TOPE_SESION_CENTAVOS = "500"          # USD 5 por sesión de prueba, como máximo
MODELO_DEFAULT = "claude-haiku-4-5-20251001"


def cliente():
    # Usamos TALLER_API_KEY (y no ANTHROPIC_API_KEY) para que Claude Code no la
    # confunda con su propia autenticación: la key es solo para los scripts.
    key = os.environ.get("TALLER_API_KEY")
    if not key:
        sys.exit("Falta la API key del taller. Cargala en las variables de entorno de Claude Code como TALLER_API_KEY.")
    try:
        import anthropic
    except ImportError:
        sys.exit("Faltan dependencias: pip install -q anthropic pyyaml openpyxl python-docx pypdf fpdf2")
    return anthropic.Anthropic(api_key=key)


def entorno(c):
    """Devuelve el entorno compartido del taller; si no existe, lo crea."""
    for env in c.beta.environments.list():
        if env.name == NOMBRE_ENTORNO:
            return env
    return c.beta.environments.create(
        name=NOMBRE_ENTORNO,
        config={"type": "cloud", "networking": {"type": "limited", "allow_package_managers": False}},
    )


def carpeta(arg=None):
    ruta = Path(arg).resolve() if arg else CARPETA_DEFAULT
    if not (ruta / "agente.yaml").exists():
        sys.exit(f"No encuentro {ruta.name}/agente.yaml. Copiá la carpeta plantilla/ a mi-agente/ y completala.")
    return ruta


def cargar_agente(ruta):
    import yaml
    datos = yaml.safe_load((ruta / "agente.yaml").read_text(encoding="utf-8"))
    faltan = [k for k in ("nombre", "autor", "empresa_o_area", "descripcion", "instrucciones")
              if not str(datos.get(k) or "").strip() or "Claude Code escribe" in str(datos.get(k))]
    if faltan:
        sys.exit(f"Falta completar en agente.yaml: {', '.join(faltan)}")
    return datos


def leer_estado(ruta):
    archivo = ruta / ".estado.json"
    return json.loads(archivo.read_text()) if archivo.exists() else {}


def guardar_estado(ruta, estado):
    (ruta / ".estado.json").write_text(json.dumps(estado, indent=2, ensure_ascii=False))


def huella(*contenidos):
    h = hashlib.sha256()
    for c in contenidos:
        h.update(c if isinstance(c, bytes) else str(c).encode())
    return h.hexdigest()[:16]


def recursos_de(estado):
    """Archivos de conocimiento para montar en cada sesión."""
    return [{"type": "file", "file_id": a["file_id"], "mount_path": f"{RUTA_CONOCIMIENTO}/{nombre}"}
            for nombre, a in estado.get("archivos", {}).items()]


def es_del_taller(agente):
    meta = getattr(agente, "metadata", None) or {}
    return meta.get("taller") == TALLER and not getattr(agente, "archived_at", None)


def agentes_del_taller(c):
    return [a for a in c.beta.agents.list() if es_del_taller(a)]
