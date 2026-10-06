"""Le manda un mensaje a tu agente y muestra la respuesta y las herramientas que usa.
Uso: python scripts/probar.py "mensaje"                 (sigue la misma conversación)
     python scripts/probar.py --nueva "mensaje"         (arranca una conversación nueva)
     python scripts/probar.py --carpeta ejemplos/viaticos "mensaje"
"""
import sys
import time
from comun import cliente, entorno, carpeta, leer_estado, guardar_estado, recursos_de, TOPE_SESION_CENTAVOS

args = sys.argv[1:]
nueva = "--nueva" in args
args = [a for a in args if a != "--nueva"]
ruta = None
if "--carpeta" in args:
    i = args.index("--carpeta")
    ruta = args[i + 1]
    del args[i:i + 2]
if not args:
    sys.exit('Uso: python scripts/probar.py "mensaje"')

base = carpeta(ruta)
estado = leer_estado(base)
if not estado.get("agent_id"):
    sys.exit("Primero desplegá el agente: python scripts/desplegar.py")

c = cliente()
inicio = time.time()
if nueva or not estado.get("sesion_id"):
    sesion = c.beta.sessions.create(
        agent=estado["agent_id"], environment_id=entorno(c).id, title="Prueba desde Claude Code",
        resources=recursos_de(estado),
        budget={"type": "limit", "max_list_cost": {"amount": TOPE_SESION_CENTAVOS, "currency": "USD"}},
    )
    estado["sesion_id"] = sesion.id
    guardar_estado(base, estado)
sid = estado["sesion_id"]

ICONOS = {"web_search": "🌐 buscando en la web", "web_fetch": "🌐 leyendo una página",
          "read": "📄 leyendo un documento", "glob": "📂 mirando sus documentos", "grep": "🔍 buscando en sus documentos"}
print(f"🧑 {args[0]}\n")
primera = None
with c.beta.sessions.events.stream(sid) as stream:
    c.beta.sessions.events.send(sid, events=[{"type": "user.message", "content": [{"type": "text", "text": args[0]}]}])
    for ev in stream:
        if "tool_use" in ev.type:
            nombre = getattr(ev, "name", "herramienta")
            entrada = getattr(ev, "input", None) or {}
            detalle = entrada.get("query") or entrada.get("url") or entrada.get("file_path") or entrada.get("path") or ""
            print(f"   [{ICONOS.get(nombre, '🔧 ' + nombre)}] {detalle}"[:160])
        elif ev.type == "agent.message":
            for b in ev.content:
                if b.type == "text":
                    if primera is None:
                        primera = time.time() - inicio
                        print("🤖 ", end="")
                    print(b.text, end="", flush=True)
        elif ev.type == "session.status_idle":
            break

total = time.time() - inicio
print(f"\n\n⏱  primera respuesta: {primera or total:.1f}s · total: {total:.1f}s")
