# Megalücuma

Papelería católica con misión. Este repositorio reúne la marca y las herramientas digitales.

## Registro de clientes y campañas (`web/`)

Sitio estático publicado en Vercel, con datos en Supabase (proyecto `megalucuma`).

- `/` formulario público general para unirse a la comunidad.
- `/c/<enlace>` formulario de una campaña, con su banner, detalles, color y fecha de cierre.
- `/equipo` panel interno: ver, editar y exportar registros; crear y editar campañas y subir banners.
  Se entra con un enlace enviado al correo. Solo entran los correos de la tabla `equipo`.

Para dar acceso a alguien al panel, en Supabase → SQL:

```sql
insert into public.equipo (email) values ('nuevo@correo.com');
```

Seguridad (reglas RLS en Supabase): el público solo puede enviar su registro y ver campañas activas;
solo el equipo puede leer, editar o borrar registros y gestionar campañas.

## Marca

- `marca/ADN-de-marca.md`: misión, visión, valores, manifiesto y paleta.
- `assets/`: logo, ornamento dorado, paleta y fotos de las agendas (Borgoña, Rosé, Olivo, Uva).
- `app-clientes/`: primera versión interna (artifact de Claude), reemplazada por `web/equipo`.
