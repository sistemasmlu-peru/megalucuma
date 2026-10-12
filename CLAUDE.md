# Megalücuma: contexto del proyecto

Megalücuma es una marca peruana de **papelería católica** (agendas, journals, stickers). Este repo contiene su
**sistema de preventas y registro de clientes**, que reemplaza un Google Form, más los recursos de marca.

El dueño del proyecto no es programador: explícale todo en español, simple y paso a paso.
Toda la interfaz (textos, botones y errores) va en **español de Perú**.

## Qué hay en producción

| Qué | URL | Para quién |
|---|---|---|
| Registro general | https://megalucuma.vercel.app | Clientes (bio de Instagram, QR) |
| Página de una preventa/campaña | https://megalucuma.vercel.app/c/<slug> | Clientes |
| Panel del equipo | https://megalucuma.vercel.app/equipo | Equipo (login por enlace al correo) |

## Arquitectura

- **Sitio estático sin build** en `web/` (HTML + CSS + JS puro), publicado en **Vercel**.
- **Supabase** para la base de datos, el login del equipo y el almacenamiento de archivos.
- `web/assets/supabase.js` es supabase-js v2.45.4 (UMD) **copiado al repo**. No hay npm ni bundler.
- `web/assets/config.js` tiene la URL y la clave **publicable** de Supabase. Es seguro exponerla: el acceso lo
  controlan las reglas RLS. **Nunca** pongas la `service_role` key en el front.
- `web/vercel.json`: `cleanUrls` y el rewrite `/c/:slug → /`. Con `cleanUrls` el destino debe ser `/`, no `/index.html`.

```
web/
  index.html          Formulario público: registro general o preventa (/c/<slug>), con compra por Yape/Plin
  equipo/index.html   Panel del equipo: pestañas Registros, Pedidos y Campañas (+ Datos de pago)
  assets/estilos.css  Tokens de marca y componentes compartidos
  assets/config.js    URL + clave publicable de Supabase
  assets/supabase.js  supabase-js UMD (+ 591.supabase.js, el chunk que carga)
  assets/*.png|webp|jpg  logo blanco, ornamento dorado, foto de agendas
  vercel.json
supabase/esquema-actual.sql  Copia de referencia de la función crear_pedido y de todas las políticas RLS
marca/ADN-de-marca.md        Misión, visión, valores, manifiesto y paleta
assets/                      Originales de marca (logo, ornamento, fotos, paleta)
app-clientes/                Primera versión (artifact de claude.ai). Obsoleta, reemplazada por web/equipo
```

## Servicios e identificadores

- **Supabase**: proyecto `megalucuma`, id/ref `idobzbqiichowelwgjeq`, región sa-east-1, organización "Mlu-Lab"
  (plan free). URL `https://idobzbqiichowelwgjeq.supabase.co`.
  - Auth: el Site URL y la Redirect URL (`https://megalucuma.vercel.app/equipo`) ya están configurados.
  - El login del equipo es por enlace mágico (`signInWithOtp`). Solo entran los correos de la tabla `equipo`.
- **Vercel**: proyecto `megalucuma` (`prj_VhAivdZsEbP5baWyvW2pJCRpU9f1`), equipo `team_fxI84NSTjZOjopiZUOyhIRNd`
  (slug `sistemasmlu-1151s-projects`). Root directory: `web`. Sin framework.
  - La protección de Vercel (SSO) aplica **solo a previews**. Producción es pública, y debe seguir así.
- **GitHub**: `sistemasmlu-peru/megalucuma`. **La rama de producción es `claude/eager-ramanujan-qnprej`**
  (fue la primera rama del repo). Un push a esa rama publica en producción.
  - A veces el webhook de Vercel no dispara. Si el deploy no aparece, lánzalo a mano:
    `vercel --prod` desde `web/`, o desde el dashboard con "Redeploy".

## Base de datos (schema `public`)

- `campanas`: preventas. `slug` (único, a-z0-9 y guiones), `titulo`, `bajada`, `detalle`, `banner_url`,
  `tema` (borgona|rose|olivo|uva), `boton`, `mensaje_gracias`, `activa`, `cierra` (fecha),
  `link_tienda`, `venta_activa`, `productos` jsonb `[{nombre, precio, con_color}]`.
- `clientes`: `nombre`, `celular`, `email`, `dni`, `direccion`, `referencia`, `distrito`, `provincia`
  (en la UI se llama "Provincia y departamento"), `cumple`, `canal` ("¿cómo nos conociste?"), `comentario`
  (del cliente), `notas` (internas del equipo), `productos` text[] (los marca el equipo), `acepta_novedades`,
  `acepta_datos`, `origen` (formulario|equipo), `campana_id`.
  Columnas antiguas que ya no se usan en la UI: `instagram`, `ciudad`, `color`.
- `pedidos`: `codigo` (6 caracteres), `cliente_id`, `campana_id`, `items` jsonb
  `[{producto, color, cantidad, precio}]`, `envio`, `total` (incluye el envío), `metodo` (yape|plin),
  `comprobante` (ruta en el bucket), `estado` (por_confirmar|pagado|enviado|entregado|cancelado),
  `es_regalo`, `regalo_para`, `comentario`, `notas`.
- `ajustes`: una sola fila (`id = 1`) con `yape_numero`, `plin_numero`, `titular`, `whatsapp` (con 51),
  `link_tienda`, `costo_envio` (10 por defecto). El equipo la edita en Campañas → "Datos de pago".
- `equipo`: correos con acceso al panel. Agregar a alguien:
  `insert into public.equipo (email) values ('correo@gmail.com');` (siempre en minúsculas).
- `privado.es_equipo()`: función SECURITY DEFINER que usan todas las políticas. Está en el schema `privado`,
  que no se expone por la API.
- `public.crear_pedido(datos jsonb)`: RPC pública (SECURITY DEFINER, a propósito) que en una sola transacción:
  valida todos los campos obligatorios, que se aceptó el envío y que la campaña está activa y vendiendo;
  **calcula el total con los precios de la campaña + `ajustes.costo_envio`** (no confía en el navegador);
  crea el cliente y el pedido, y devuelve el código. El advisor de Supabase la marca como WARN: es esperado.

### Storage

- `banners`: bucket público. Solo el equipo sube, cambia o borra.
- `comprobantes`: bucket **privado**, de 8 MB. Cualquiera puede subir, solo con nombre `<uuid>.<ext>`. Solo el
  equipo puede ver (con URL firmada) y borrar.

### Reglas de seguridad (RLS)

- Público (anon): ve solo las campañas activas y no vencidas; inserta en `clientes` (solo registro); llama a
  `crear_pedido`; sube comprobantes; lee `ajustes`. **No puede leer** clientes ni pedidos.
- El equipo (autenticado y en `equipo`) puede todo sobre clientes, pedidos, campañas y ajustes.
- El detalle está en `supabase/esquema-actual.sql`. Después de cada cambio de esquema revisa los advisors de
  seguridad y prueba las políticas con `set local role anon` dentro de una transacción con `rollback`.

## Flujo del cliente (preventa con venta activa)

1. Llena sus datos. Todos son obligatorios (nombre, DNI, teléfono, correo, dirección, referencia, distrito,
   provincia y departamento, cumpleaños, cómo nos conoció), menos el comentario adicional. "Es para regalo"
   abre una caja obligatoria de "para quién es".
2. Elige "Yape o Plin", "En la web" (botón a `link_tienda`) o "Solo registrarme".
3. Con Yape/Plin: arma el pedido (producto, color y cantidad), se suma el envío (S/ 10, con casilla obligatoria
   "Acepto el costo de envío"), paga al número que muestra y sube la captura.
4. Ve su código de pedido y un botón de WhatsApp (al número de `ajustes.whatsapp`) con el mensaje ya escrito.

Arriba, en la página de una campaña, dice **"Preventa"** debajo del logo.

## Marca

- Paleta (los nombres de las agendas): **Borgoña** `#4c1825`, **Rosé** `#bb8d83`, **Olivo** `#4a4526`
  (`#463f21` en la paleta original), **Uva** `#694463`. Oro de los ornamentos: `#c3934b`.
- Tipografías: **Fraunces** (títulos) y **Nunito** (texto), desde Google Fonts.
- Logo "MLü": `web/assets/logo-blanco.png` (blanco, para fondos oscuros) y `assets/logo-naranja.png`.
- Tono: cálido, cercano, de fe católica. Ver `marca/ADN-de-marca.md`.

## Cómo trabajar en este repo

- Antes de publicar, revisa la sintaxis del JS de cada página. Por ejemplo:
  `node -e "const h=require('fs').readFileSync('web/index.html','utf8');[...h.matchAll(/<script>([\s\S]*?)<\/script>/g)].forEach(m=>new Function(m[1]))"`
- Prueba local: `npx http-server web -p 8080` y abre `http://localhost:8080/?c=<slug>`.
  La ruta `/c/<slug>` solo funciona en Vercel.
- Los cambios de base de datos se hacen con migraciones en Supabase (MCP de Supabase o SQL Editor). Usa
  `create or replace`; evita `drop` sobre datos reales sin confirmarlo con el dueño.
- Cuida que todo funcione en celular: la mayoría de los clientes entra desde Instagram o WhatsApp.

## Pendientes

- Nombre del **titular del Yape** (se pone en Campañas → Datos de pago).
- **Link exacto** de la página de agendas en megalucuma.com (hoy apunta a la portada).
- Agregar `megalucumalab@gmail.com` y `megalucuma@gmail.com` a la tabla `equipo` cuando el dueño lo confirme.
- Hay un pedido de prueba de S/ 75 en la base. El dueño puede borrarlo desde Pedidos → Eliminar.
- El registro sin compra (insert directo en `clientes`) valida los campos obligatorios solo en el navegador.
  Si hace falta, se puede pasar a una RPC como `crear_pedido`.
- La primera app (artifact en claude.ai, `app-clientes/`) quedó obsoleta. Se puede borrar.
- Siguiente trabajo que pidió el dueño: **mockups y carrusel para Instagram** con la línea gráfica de la marca.
- Opcional: dominio propio (p. ej. `registro.megalucuma.com`) apuntando al proyecto de Vercel.
