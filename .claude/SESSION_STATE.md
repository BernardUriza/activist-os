# SESSION STATE — 2026-06-18 (~15:00 CST)

## Quick Summary
**Activist OS quedó ENTREGADO al Band of Agents Hackathon (lablab.ai), dentro del
deadline (19 jun 9:00 AM CST).** La sesión pulió el contraste del `/app`, arregló
el root cause de que prod servía MOCK en vez de BAND (CORS), grabó el demo con
videopipe, generó deck+cover, y completó la submission en lablab.ai (confirmación
"Congratulations! You have successfully submitted…"). Args del save: *"segundo
hackathon entregado"* — éste es el 2º hackathon que Bernard cierra.

## Estado del repo
- **Branch:** `main` (única rama; pusheado).
- **Uncommitted:** solo `web/next-env.d.ts` (generado por Next, se deja). Todo lo
  demás commiteado + pusheado.
- **Últimos commits:** `4bc062d` gitignore `.submission/` · `728d712` docs→friendly
  domain · `b7c7905` VIDEO_SCRIPT→friendly · `113ed5d` contrast pass del /app.

## Lo entregado (Free Intelligence · Track 3 — Regulated & High-Stakes)
- **Submission lablab.ai CONFIRMADA** (team `free-intelligence`, evento
  `band-of-agents-hackathon`). Receipt: pantalla "Congratulations!" + "View your
  submission".
- Título **Activist OS** · Categories: Non-Profit, Productivity · Technologies:
  Band Control Plane, Band Agentic Mesh, Anthropic Claude.
- **Video** narrado (Azure TTS onyx) + captions, 1920×1220, 51s · **Deck PDF**
  6 slides 16:9 · ambos subidos al storage de lablab.
- GitHub `github.com/BernardUriza/activist-os` · Platform "Other" (Azure) ·
  Demo `https://aos.bernarduriza.com/app`.
- Artefactos en `~/Desktop/activist-os-{demo.mp4,deck.pdf,cover.png}` y copia en
  repo `./.submission/` (gitignored).

## Decisiones / hechos clave de la sesión
1. **Friendly URL** es el canónico: `aos.bernarduriza.com` (no el hostname
   `*.azurestaticapps.net`). Docs judge-facing actualizados.
2. **Root cause MOCK→BAND**: la Container App ya tenía `TRANSPORT=band`; faltaba
   `aos.bernarduriza.com` en `CORS_ALLOW_ORIGINS` → el browser caía a mock. Se
   agregó vía `az containerapp update`; prod ahora corre `LIVE · BAND` con room
   chip real.
3. **Submission wizard de lablab**: navegar Back resetea uploads + corrompe el
   save (payload vacío → "Unexpected error"). Un **pase forward limpio** tras
   reload lo resolvió. (Codificado como regla, abajo.)
4. El **cover image** (opcional) NO se subió por automation; queda como drag-drop
   manual si Bernard lo quiere (View your submission → editar).

## Reglas registradas esta sesión (engineering-playbook, pusheadas)
- `audience-aware-communication.md` — preferir el friendly/custom domain sobre el
  platform hostname.
- `fi-runner-azure-deploy.md` — CORS_ALLOW_ORIGINS debe incluir el friendly domain.
- `video-recording-workflow.md` — autorecorder seed-not-stream + verify-not-black.
- `chrome-devtools-multistep-form-submission.md` (NUEVO, `07ef2c9`) — conducir
  wizards de submission multi-paso.
- Backlog en videopipe: `autorecorder-external-clip-dir.md`.

## To Resume
La entrega está HECHA y verificada — no hay acción crítica pendiente. Si Bernard
retoma: (a) opcional, subir el cover image en "View your submission"; (b) el video
final vive en `picturelock/build/activist-demo-final.mp4` por si quiere re-cortar;
(c) deadline ya cubierto (19 jun 9 AM CST). El producto está LIVE+BAND en
`aos.bernarduriza.com/app`.
