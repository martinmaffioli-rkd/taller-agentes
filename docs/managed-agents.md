# Managed Agents en una página

Claude Managed Agents está en beta: todas las llamadas llevan el header
`anthropic-beta: managed-agents-2026-04-01` (los SDKs lo agregan solos).

| Concepto | Qué es | En este taller |
|---|---|---|
| **Agente** | Modelo + instrucciones + herramientas + skills. Se crea una vez, se usa por ID y tiene versiones. | `mi-agente/` |
| **Entorno** | Sandbox en la nube donde corren las sesiones | Uno compartido: `taller-rkd-0710` |
| **Sesión** | Una conversación, con historial y archivos montados | Cada prueba o chat en la galería |
| **Eventos** | Mensajes entre tu app y el agente, por streaming | `user.message` → `agent.message` |

## Las cuatro piezas y cómo se implementan

| Pieza | Implementación |
|---|---|
| Instrucciones | `system` del agente |
| Base de conocimiento | Archivos subidos con la Files API y montados en cada sesión (`resources`, tipo `file`) en `/mnt/session/uploads/conocimiento/`. El agente los lee con las herramientas `read`, `glob` y `grep`. |
| Skill | Carpeta con `SKILL.md` subida con `client.beta.skills.create` y referenciada en `skills` del agente. El agente ve solo nombre y descripción hasta que la necesita. |
| Herramienta | `agent_toolset_20260401` con todo apagado salvo `read`, `glob`, `grep`, `web_search` y `web_fetch` |

## Llamadas que usan los scripts (SDK de Python ≥ 1.11)

```python
c = anthropic.Anthropic(api_key=os.environ["TALLER_API_KEY"])
f = c.beta.files.upload(file=("topes.md", contenido, "text/markdown"))
sk = c.beta.skills.create(files=[("rendir-gastos/SKILL.md", contenido)])
a = c.beta.agents.create(name=..., model=..., system=..., metadata={...},
        skills=[{"type": "custom", "skill_id": sk.id}],
        tools=[{"type": "agent_toolset_20260401", "default_config": {"enabled": False},
                "configs": [{"name": "read", "enabled": True}, {"name": "web_search", "enabled": True}, ...]}])
s = c.beta.sessions.create(agent=a.id, environment_id=env.id,
        resources=[{"type": "file", "file_id": f.id, "mount_path": "/mnt/session/uploads/conocimiento/topes.md"}],
        budget={"type": "limit", "max_list_cost": {"amount": "500", "currency": "USD"}})
with c.beta.sessions.events.stream(s.id) as stream:
    c.beta.sessions.events.send(s.id, events=[{"type": "user.message",
        "content": [{"type": "text", "text": "hola"}]}])
    for ev in stream:   # agent.tool_use → usa una herramienta; agent.message → texto; session.status_idle → terminó
        ...
```

## Para después del taller

Conectar el agente a sistemas reales (MCP, herramientas propias), darle bash para
procesar archivos, programar ejecuciones o correr el sandbox en infraestructura propia.
Documentación: https://platform.claude.com/docs/en/managed-agents/overview
