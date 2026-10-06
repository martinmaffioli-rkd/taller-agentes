"""Lista los agentes publicados en el taller. Uso: python scripts/listar.py"""
from comun import cliente, agentes_del_taller

agentes = agentes_del_taller(cliente())
print(f"{len(agentes)} agentes en el taller:\n")
for a in agentes:
    m = a.metadata or {}
    print(f"• {m.get('nombre_agente', a.name)} — {m.get('autor', '?')} ({m.get('empresa_o_area', '')})")
    print(f"  piezas: {m.get('piezas', '')} · {a.description or ''}")
