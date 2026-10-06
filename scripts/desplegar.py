"""Crea o actualiza tu agente con sus cuatro piezas: instrucciones, base de conocimiento,
skill y herramientas. Uso: python scripts/desplegar.py [carpeta]   (por defecto: mi-agente)"""
import io
import sys
from comun import (cliente, carpeta, cargar_agente, leer_estado, guardar_estado, huella,
                   TALLER, MODELO_DEFAULT, RUTA_CONOCIMIENTO)

base = carpeta(sys.argv[1] if len(sys.argv) > 1 else None)
datos = cargar_agente(base)
estado = leer_estado(base)
c = cliente()
piezas = ["instrucciones"]

# 1) Base de conocimiento: sube los .md de conocimiento/ (solo los que cambiaron)
archivos = {}
for md in sorted((base / "conocimiento").glob("*.md")):
    contenido = md.read_bytes()
    previo = estado.get("archivos", {}).get(md.name)
    if previo and previo["hash"] == huella(contenido):
        archivos[md.name] = previo
        continue
    subido = c.beta.files.upload(file=(md.name, io.BytesIO(contenido), "text/markdown"))
    archivos[md.name] = {"file_id": subido.id, "hash": huella(contenido)}
    print(f"📚 Conocimiento subido: {md.name}")
if len(archivos) > 6:
    sys.exit("Máximo 6 documentos de conocimiento por agente.")
estado["archivos"] = archivos
if archivos:
    piezas.append("conocimiento")

# 2) Skill: sube skill/ (SKILL.md y archivos de apoyo) como skill propia
skills = []
skill_dir = base / "skill"
skill_md = skill_dir / "SKILL.md"
nombre_skill = ""
if skill_md.exists() and "name:" in skill_md.read_text(encoding="utf-8"):
    import yaml
    texto = skill_md.read_text(encoding="utf-8")
    frontmatter = yaml.safe_load(texto.split("---")[1])
    nombre_skill = frontmatter["name"]
    rutas = sorted(p for p in skill_dir.rglob("*") if p.is_file())
    hash_skill = huella(*[p.read_bytes() for p in rutas])
    paquete = [(f"{nombre_skill}/{p.relative_to(skill_dir).as_posix()}", io.BytesIO(p.read_bytes())) for p in rutas]
    if not estado.get("skill_id"):
        sk = c.beta.skills.create(files=paquete, display_name=f"{nombre_skill} · {datos['autor']}"[:255])
        estado["skill_id"] = sk.id
        print(f"🧩 Skill creada: {nombre_skill}")
    elif estado.get("skill_hash") != hash_skill:
        c.beta.skills.versions.create(estado["skill_id"], files=paquete)
        print(f"🧩 Skill actualizada: {nombre_skill}")
    estado["skill_hash"] = hash_skill
    skills = [{"type": "custom", "skill_id": estado["skill_id"]}]
    piezas.append("skill")

# 3) Herramientas: lectura de archivos (para conocimiento y skill) y web, sin bash ni escritura
web = bool(datos.get("web"))
configs = [{"name": n, "enabled": True} for n in ("read", "glob", "grep")]
if web:
    configs += [{"name": "web_search", "enabled": True},
                {"name": "web_fetch", "enabled": True, "max_content_tokens": 8000}]
    piezas.append("web")
herramientas = [{"type": "agent_toolset_20260401", "default_config": {"enabled": False}, "configs": configs}]

# 4) Instrucciones + sección automática que le explica al agente sus recursos
extra = ["\n\n# Recursos disponibles"]
if archivos:
    extra.append(f"- Base de conocimiento: documentos en {RUTA_CONOCIMIENTO}/: "
                 + ", ".join(archivos) + ". Antes de responder sobre esos temas, consultalos con la herramienta "
                 "read (podés listarlos con glob y buscar con grep). Si un dato no está ahí, decí que no lo tenés.")
if skills:
    extra.append(f"- Skill \"{nombre_skill}\": usala cuando la tarea coincida con su descripción.")
if web:
    extra.append("- Web: podés buscar (web_search) y leer páginas (web_fetch) para información actual o externa. "
                 "Mencioná la fuente.")
sistema = datos["instrucciones"].rstrip() + ("\n".join(extra) if len(extra) > 1 else "")

meta = {
    "taller": TALLER,
    "autor": str(datos["autor"])[:100],
    "empresa_o_area": str(datos["empresa_o_area"])[:200],
    "nombre_agente": str(datos["nombre"])[:100],
    "piezas": ",".join(piezas),
    "archivos": ";".join(f"{a['file_id']}:{n}" for n, a in archivos.items())[:512],
    "skill": nombre_skill[:100],
}
campos = dict(name=f"{datos['nombre']} · {datos['autor']}"[:120], description=datos["descripcion"],
              system=sistema, model=datos.get("modelo") or MODELO_DEFAULT,
              tools=herramientas, skills=skills, metadata=meta)

if estado.get("agent_id"):
    agente = c.beta.agents.update(estado["agent_id"], **campos)
    accion = "actualizado"
else:
    agente = c.beta.agents.create(**campos)
    estado["agent_id"] = agente.id
    accion = "creado"

estado.pop("sesion_id", None)  # la próxima prueba arranca con la versión nueva
guardar_estado(base, estado)
print(f"✅ Agente {accion}: {agente.name}")
print(f"   ID: {agente.id} · versión {agente.version}")
print(f"   Piezas: {', '.join(piezas)}")
print("   Ya aparece en la galería del taller.")
