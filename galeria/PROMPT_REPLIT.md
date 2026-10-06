Construí una web app llamada "Galería de Agentes · Taller RKD" para un taller presencial de RockingData. Implementala completa ahora, sin pedirme confirmación.

## Qué hace
Muestra en una grilla todos los agentes de IA que crean los participantes del taller con Claude Managed Agents (API de Anthropic) y permite chatear con cualquiera de ellos. Se proyecta en pantalla y también se usa desde el celular.

## Stack
- Backend Node.js + Express con el SDK oficial `@anthropic-ai/sdk` (versión 0.131 o superior).
- Frontend en HTML, CSS y JavaScript servido por el mismo Express (sin frameworks pesados).
- Secrets de Replit: `ANTHROPIC_API_KEY` y `ACCESS_CODE`. La API key NUNCA llega al navegador.

## API de Managed Agents (beta; el SDK agrega el header `managed-agents-2026-04-01`)
```js
import Anthropic from "@anthropic-ai/sdk";
const client = new Anthropic(); // lee ANTHROPIC_API_KEY

// Listar agentes del taller (auto-paginado): filtrar por metadata.taller === "rkd-taller-0710" y archived_at == null
for await (const a of client.beta.agents.list()) { /* a.id, a.name, a.description, a.metadata, a.version, a.updated_at */ }

// Entorno compartido: buscar por nombre "taller-rkd-0710"; si no existe, crearlo
for await (const e of client.beta.environments.list()) { /* e.id, e.name */ }
await client.beta.environments.create({ name: "taller-rkd-0710",
  config: { type: "cloud", networking: { type: "limited", allow_package_managers: false } } });

// Crear una sesión (una por conversación) con tope de gasto de USD 3
const session = await client.beta.sessions.create({ agent: agentId, environment_id: envId,
  title: "Galería", budget: { type: "limit", max_list_cost: { amount: "300", currency: "USD" } } });

// Enviar un mensaje y leer la respuesta por streaming: abrir el stream ANTES de enviar
const stream = await client.beta.sessions.events.stream(session.id);
await client.beta.sessions.events.send(session.id, { events: [
  { type: "user.message", content: [{ type: "text", text: userText }] } ] });
for await (const ev of stream) {
  if (ev.type === "agent.message") { /* ev.content: bloques con type "text" → reenviar al navegador */ }
  if (ev.type === "session.status_idle") break;
}
```
Docs: https://platform.claude.com/docs/en/managed-agents/quickstart

## Endpoints del backend
- `POST /api/login` { code } → valida contra ACCESS_CODE y setea cookie de sesión. Todo lo demás requiere esa cookie.
- `GET /api/agents` → lista de agentes del taller: id, nombre (`metadata.nombre_agente` o `name`), autor (`metadata.autor`), empresa (`metadata.empresa_o_area`), descripción, versión, updated_at. Cache de 10 segundos.
- `POST /api/chat/:agentId/session` → crea una sesión nueva y devuelve su id.
- `POST /api/chat/:sessionId/message` { text } → responde por Server-Sent Events con el texto del agente a medida que llega y un evento final "done". Máximo 20 mensajes por sesión y 500 caracteres por mensaje.
- Manejo de errores claro: si la API falla, devolver un mensaje en español ("El agente no respondió, probá de nuevo").

## Frontend
1. Pantalla de acceso: campo para el código del taller.
2. Galería: grilla de tarjetas (nombre del agente grande, autor, empresa o área, descripción, "v{versión}"). Se actualiza sola cada 10 segundos y las tarjetas nuevas aparecen con una animación sutil. Contador "N agentes en el taller" arriba. Botón "Chatear" en cada tarjeta.
3. Chat: al abrir una tarjeta se crea una sesión nueva. Encabezado con nombre y autor del agente, burbujas de usuario y agente, indicador "pensando…" mientras espera (la primera respuesta puede tardar unos segundos: mostrar "Despertando al agente…"). Botón "Nueva conversación" y botón "Volver a la galería". El texto del agente se va mostrando a medida que llega.
4. Responsive: en celular la grilla pasa a una columna y el chat ocupa toda la pantalla.

## Identidad visual RockingData (modo oscuro)
- Fondo #0B0B0B, tarjetas #141414, borde sutil #2A2A2A, texto #FFFFFF y secundario #A0A0A0.
- Acento amarillo #FFD600 para botones, contador y detalles; texto negro sobre amarillo.
- Títulos en Barlow Condensed Bold (Google Fonts) en mayúsculas; cuerpo en Inter.
- Título de la galería: "GALERÍA DE AGENTES" con subtítulo "Taller · Armá tu propia Estrategia de Data & AI · RockingData".

## Cierre
Implementá todo ahora. Si falta ANTHROPIC_API_KEY, la app debe arrancar igual y mostrar en la galería el aviso "Falta configurar la API key del taller".

## Actualización: las cuatro piezas (instrucciones, conocimiento, skill, herramienta)
- Base de conocimiento: `metadata.archivos` trae pares `file_id:nombre.md` separados por `;`. Al crear cada sesión,
  pasar `resources` con un elemento por archivo: `{ type: "file", file_id, mount_path: "/mnt/session/uploads/conocimiento/" + nombre }`.
- Tope por conversación: USD 3 (`amount: "300"`).
- Tarjetas: insignias según `metadata.piezas` (🌐 Web, 📚 Conocimiento, 🧩 Skill) y nombre de la skill (`metadata.skill`).
- Chat: mostrar en vivo los eventos cuyo tipo contiene `tool_use` como una línea gris (🌐 Buscando en la web: consulta /
  🌐 Leyendo página / 📄 Consultando documento / 🔍 Revisando documentos / 🧩 Usando su skill si la ruta leída incluye "skill").
