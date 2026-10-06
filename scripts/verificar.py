"""Verifica que la conexión con Managed Agents funciona. Uso: python scripts/verificar.py"""
from comun import cliente, entorno, agentes_del_taller

c = cliente()
try:
    env = entorno(c)
    total = len(agentes_del_taller(c))
except Exception as e:
    raise SystemExit(f"No pude conectarme con Managed Agents: {type(e).__name__}: {e}")
print("✅ Conexión OK")
print(f"   Entorno del taller: {env.name}")
print(f"   Agentes del taller publicados hasta ahora: {total}")
