# Taller RKD · Creá tu primer agente con Claude Code y Managed Agents

Template del taller presencial de RockingData (7/10/2026).

**Para participantes:** abrí este repo desde el link del taller en Claude Code web
y decile a Claude: *"Arrancamos el taller"*. Claude te guía en todo.

**Las cuatro piezas de un agente:** instrucciones, base de conocimiento, skill y herramienta.

**Para facilitadores:**
- `CLAUDE.md`: protocolo que sigue Claude Code (entrevista, reglas, flujo).
- `plantilla/`: carpeta base. Cada participante trabaja en `mi-agente/`, ignorada por git.
- `scripts/`: verificar, convertir (Word/Excel/PDF → texto), desplegar, probar y listar.
- `ejemplos/viaticos/` y `ejemplos/andes-market/`: agentes completos con las cuatro piezas.
- `docs/`: resumen de la API y tarjeta de ataques para imprimir.
- `galeria/`: prompt para construir la galería en Replit.

Variable de entorno en Claude Code web: `TALLER_API_KEY`.
Todos los agentes llevan `metadata.taller = "rkd-taller-0710"` y comparten el entorno
`taller-rkd-0710`. Al terminar: revocar la key y archivar los agentes.
