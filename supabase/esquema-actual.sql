-- Copia de referencia del estado actual de la base (proyecto Supabase idobzbqiichowelwgjeq).
-- No es una migración para ejecutar tal cual: sirve para entender la lógica y las reglas.

-- =====================================================================
-- Función pública para crear pedidos (la llama web/index.html con sb.rpc)
-- =====================================================================
CREATE OR REPLACE FUNCTION public.crear_pedido(datos jsonb)
 RETURNS text
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
declare
  camp public.campanas;
  item jsonb;
  prod jsonb;
  lineas jsonb := '[]'::jsonb;
  total numeric(10,2) := 0;
  cant int;
  color text;
  nuevo_cliente uuid;
  cod text;
  letras constant text := 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  t text;
  envio_costo numeric(10,2);
begin
  if coalesce((datos->>'acepta_datos')::boolean, false) is not true then
    raise exception 'Falta la autorización de datos';
  end if;
  select * into camp from public.campanas
   where id = (datos->>'campana_id')::uuid and activa and venta_activa
     and (cierra is null or cierra >= (now() at time zone 'America/Lima')::date);
  if camp.id is null then raise exception 'La campaña no está disponible para compras'; end if;
  if jsonb_typeof(datos->'items') <> 'array' or jsonb_array_length(datos->'items') not between 1 and 20 then
    raise exception 'Pedido vacío o demasiado grande';
  end if;
  if coalesce((datos->>'acepta_envio')::boolean, false) is not true then raise exception 'Debes aceptar el costo de envío'; end if;
  if (datos->>'metodo') not in ('yape','plin') then raise exception 'Método de pago inválido'; end if;
  if (datos->>'comprobante') !~ '^[0-9a-f-]{36}\.(jpg|jpeg|png|webp|heic|heif|pdf)$' then
    raise exception 'Falta el comprobante de pago';
  end if;
  foreach t in array array['nombre','celular','dni','email','direccion','referencia','distrito','provincia','cumple','canal'] loop
    if char_length(trim(coalesce(datos->>t, ''))) < 2 then raise exception 'Falta completar: %', t; end if;
  end loop;

  for item in select * from jsonb_array_elements(datos->'items') loop
    select p into prod from jsonb_array_elements(camp.productos) p where p->>'nombre' = item->>'producto' limit 1;
    if prod is null then raise exception 'Producto no disponible: %', item->>'producto'; end if;
    cant := (item->>'cantidad')::int;
    if cant is null or cant not between 1 and 20 then raise exception 'Cantidad inválida'; end if;
    color := nullif(item->>'color', '');
    if coalesce((prod->>'con_color')::boolean, false) then
      if color is null or color not in ('borgona','rose','olivo','uva') then raise exception 'Elige un color para %', prod->>'nombre'; end if;
    else
      color := null;
    end if;
    total := total + cant * (prod->>'precio')::numeric;
    lineas := lineas || jsonb_build_object('producto', prod->>'nombre', 'color', color, 'cantidad', cant, 'precio', (prod->>'precio')::numeric);
  end loop;

  insert into public.clientes (cumple, canal, nombre, celular, email, dni, direccion, referencia, distrito, provincia,
                               acepta_novedades, acepta_datos, campana_id, origen)
  values (
    nullif(datos->>'cumple', '')::date, nullif(left(trim(datos->>'canal'), 60), ''), trim(datos->>'nombre'), trim(datos->>'celular'), nullif(trim(datos->>'email'), ''),
    trim(datos->>'dni'), trim(datos->>'direccion'), nullif(trim(datos->>'referencia'), ''),
    trim(datos->>'distrito'), trim(datos->>'provincia'),
    coalesce((datos->>'acepta_novedades')::boolean, false), true, camp.id, 'formulario')
  returning id into nuevo_cliente;

  loop
    cod := '';
    for i in 1..6 loop
      cod := cod || substr(letras, 1 + floor(random() * 32)::int, 1);
    end loop;
    exit when not exists (select 1 from public.pedidos where codigo = cod);
  end loop;

  select coalesce(costo_envio, 0) into envio_costo from public.ajustes where id = 1;
  total := total + coalesce(envio_costo, 0);
  insert into public.pedidos (envio, codigo, cliente_id, campana_id, items, total, metodo, comprobante, es_regalo, regalo_para, comentario)
  values (coalesce(envio_costo, 0), cod, nuevo_cliente, camp.id, lineas, total, datos->>'metodo', datos->>'comprobante',
          coalesce((datos->>'es_regalo')::boolean, false),
          case when coalesce((datos->>'es_regalo')::boolean, false) then nullif(left(trim(datos->>'regalo_para'), 500), '') end,
          nullif(left(trim(datos->>'comentario'), 1000), ''));
  return cod;
end; $function$;
-- Permisos: revoke execute from public; grant execute to anon, authenticated.

-- privado.es_equipo(): SECURITY DEFINER, search_path ''
--   select exists (select 1 from public.equipo where email = lower(coalesce(auth.jwt() ->> 'email', '')));
--   Ejecutable solo por authenticated. Schema privado no expuesto por la API.

-- Permisos de columnas para anon en clientes (insert directo del registro sin compra):
--   grant insert (nombre, celular, email, instagram, ciudad, cumple, canal, color, acepta_novedades, acepta_datos,
--                 campana_id, dni, direccion, referencia, distrito, provincia, comentario) on public.clientes to anon;

-- =====================================================================
-- Políticas RLS vigentes
-- =====================================================================
-- public.ajustes: equipo edita ajustes UPDATE TO authenticated USING (privado.es_equipo()) CHECK (privado.es_equipo())
-- public.ajustes: todos leen ajustes SELECT TO anon,authenticated USING (true)
-- public.campanas: equipo crea/edita/elimina/ve campanas -> authenticated con privado.es_equipo()
-- public.campanas: publico ve campanas activas SELECT TO anon USING (activa AND (cierra IS NULL OR cierra >= hoy en America/Lima))
-- public.clientes: equipo registra/lee/edita/elimina -> authenticated con privado.es_equipo()
-- public.clientes: publico registra INSERT TO anon CHECK (origen = 'formulario' AND acepta_datos = true AND notas IS NULL AND productos = '{}')
-- public.equipo: equipo ve equipo SELECT TO authenticated USING (privado.es_equipo())
-- public.pedidos: equipo lee/edita/elimina -> authenticated con privado.es_equipo()  (inserta solo crear_pedido)
-- storage.objects banners: equipo sube/cambia/borra (bucket público para lectura)
-- storage.objects comprobantes: publico sube (anon, authenticated) CHECK (bucket_id = 'comprobantes' AND name ~ '^[0-9a-f-]{36}\.(jpg|jpeg|png|webp|heic|heif|pdf)$')
-- storage.objects comprobantes: equipo ve / borra (bucket privado, 8 MB, imágenes y PDF)
