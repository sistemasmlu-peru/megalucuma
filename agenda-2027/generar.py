# -*- coding: utf-8 -*-
"""
Genera el interior completo del Planner 2027 (agenda-2027.html) a partir de:
  - el documento "Planner 2027" de Canva (orden de secciones y textos)
  - los bocetos de la dueña (hoja semanal, panorama, frase)
  - el modelo de la agenda 2026 (eventos, rutina, objetivos, calendario)
Uso:  python3 agenda-2027/generar.py      (luego se convierte a PDF con Playwright)
"""
import datetime as dt, re, os, html

AQUI = os.path.dirname(os.path.abspath(__file__))
estilos = re.search(r'<style>(.*?)</style>', open(os.path.join(AQUI, 'muestra.html')).read(), re.S).group(1)
estilos = estilos.split('/* vista previa en pantalla */')[0]

AÑO = 2027
MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
ABR = ['ENE','FEB','MAR','ABR','MAY','JUN','JUL','AGO','SEP','OCT','NOV','DIC']
DIAS = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
# Color por estación (4 colores de marca). Rosé se oscurece un poco para que el texto blanco se lea.
COLOR_MES = ['#4c1825']*3 + ['#4a4526']*3 + ['#694463']*3 + ['#9a6e65']*3

# ---------------------------------------------------------------- santoral y feriados 2027
# (mes, día): (texto, feriado, precepto)
F = {}
def f(m, d, t, fer=0, pre=0): F[(m, d)] = (t, fer, pre)
f(1,1,'Santa María, Madre de Dios',1,1); f(1,6,'Epifanía del Señor'); f(1,10,'Bautismo del Señor'); f(1,24,'San Francisco de Sales'); f(1,28,'Santo Tomás de Aquino')
f(2,2,'Presentación del Señor'); f(2,10,'Miércoles de Ceniza'); f(2,11,'Nuestra Señora de Lourdes'); f(2,22,'Cátedra de San Pedro')
f(3,19,'San José'); f(3,21,'Domingo de Ramos'); f(3,25,'Jueves Santo',1); f(3,26,'Viernes Santo',1); f(3,28,'Domingo de Resurrección')
f(4,4,'Domingo de la Divina Misericordia'); f(4,5,'Anunciación del Señor'); f(4,25,'San Marcos Evangelista'); f(4,29,'Santa Catalina de Siena')
f(5,1,'San José Obrero · Día del Trabajo',1); f(5,9,'Ascensión del Señor'); f(5,13,'Nuestra Señora de Fátima'); f(5,14,'San Matías Apóstol'); f(5,16,'Pentecostés'); f(5,23,'Santísima Trinidad'); f(5,24,'María Auxiliadora'); f(5,27,'Corpus Christi'); f(5,31,'Visitación de la Virgen')
f(6,4,'Sagrado Corazón de Jesús'); f(6,5,'Inmaculado Corazón de María'); f(6,7,'Batalla de Arica',1); f(6,13,'San Antonio de Padua'); f(6,29,'San Pedro y San Pablo',1,1)
f(7,3,'Santo Tomás Apóstol'); f(7,16,'Nuestra Señora del Carmen'); f(7,23,'Día de la Fuerza Aérea',1); f(7,26,'San Joaquín y Santa Ana'); f(7,28,'Fiestas Patrias',1); f(7,29,'Fiestas Patrias',1)
f(8,6,'Transfiguración del Señor · Batalla de Junín',1); f(8,15,'Asunción de la Virgen María'); f(8,28,'San Agustín'); f(8,30,'Santa Rosa de Lima',1)
f(9,8,'Natividad de la Virgen María'); f(9,14,'Exaltación de la Santa Cruz'); f(9,15,'Nuestra Señora de los Dolores'); f(9,29,'Santos Arcángeles')
f(10,1,'Santa Teresita del Niño Jesús'); f(10,2,'Santos Ángeles Custodios'); f(10,4,'San Francisco de Asís'); f(10,7,'Nuestra Señora del Rosario'); f(10,8,'Combate de Angamos',1); f(10,18,'Señor de los Milagros')
f(11,1,'Todos los Santos',1,1); f(11,2,'Fieles Difuntos'); f(11,3,'San Martín de Porres'); f(11,21,'Cristo Rey'); f(11,27,'Virgen de la Medalla Milagrosa'); f(11,28,'I Domingo de Adviento')
f(12,6,'San Nicolás'); f(12,8,'Inmaculada Concepción',1,1); f(12,9,'Batalla de Ayacucho',1); f(12,12,'Virgen de Guadalupe'); f(12,25,'Navidad del Señor',1,1); f(12,26,'Sagrada Familia'); f(12,28,'Santos Inocentes')

# ---------------------------------------------------------------- textos del documento de Canva
CARATULAS = [
 ('¿Quién es el Espíritu Santo?','Juan 14, 16-17 · Catecismo, 685-686',
  ['El Espíritu Santo no es una fuerza impersonal ni una energía que podamos controlar. Es la tercera Persona de la Santísima Trinidad, verdadero Dios junto al Padre y al Hijo. Jesús lo promete a sus discípulos como el Paráclito, aquel que permanece con ellos y los conduce a la verdad.',
   'Conocer al Espíritu Santo es entrar en una relación más profunda con Dios, reconocer su presencia y aprender a vivir como hijos suyos.'],
  '¿Qué lugar ocupa el Espíritu Santo en mi oración y en mis decisiones cotidianas?'),
 ('El Espíritu que da vida','Génesis 1, 2 · Salmo 104, 30',
  ['Desde el comienzo, la Escritura nos presenta al Espíritu de Dios en relación con la creación. Él es dador de vida y obra en nosotros para hacernos participar de la vida nueva que Cristo nos ha ganado.',
   'La vida espiritual no consiste únicamente en esforzarnos por ser mejores. También consiste en dejarnos renovar por la gracia de Dios, permitiéndole transformar aquello que necesita ser purificado, fortalecido y vivificado en nosotros.'],
  '¿En qué aspecto de mi vida necesito pedirle a Dios que renueve mi corazón?'),
 ('María, dócil a la acción del Espíritu','Lucas 1, 35-38 · Hechos 1, 14',
  ['En la Anunciación, María recibe el anuncio del ángel y responde con una disponibilidad que cambiará la historia. La acción del Espíritu Santo está en el centro de este misterio, y la respuesta de María nos muestra una fe que escucha y se entrega.',
   'Su docilidad no es pasividad: es una confianza que la dispone a acoger la voluntad de Dios y a ponerse en camino. Con ella aprendemos que escuchar al Señor puede exigir valentía, incluso cuando todavía no conocemos todo lo que vendrá.'],
  '¿Qué respuesta generosa me está pidiendo Dios en este momento?'),
 ('El Espíritu viene en ayuda de nuestra debilidad','Romanos 8, 26-27',
  ['Hay momentos en los que no sabemos qué pedir, nos faltan las palabras o sentimos que nuestra oración es pobre. San Pablo nos recuerda que el Espíritu viene en ayuda de nuestra debilidad e intercede por nosotros.',
   'No necesitas presentarte ante Dios con una oración perfecta. Puedes acudir a Él con sencillez, ofrecerle tus preocupaciones y permanecer en su presencia. También en nuestra pobreza podemos aprender a orar.'],
  '¿Qué necesito poner hoy ante Dios, incluso si no encuentro las palabras para expresarlo?'),
 ('Pentecostés: recibimos el envío','Hechos 2, 1-11',
  ['Los discípulos estaban reunidos cuando descendió sobre ellos el Espíritu Santo. Aquellos hombres, antes temerosos, recibieron la fortaleza necesaria para anunciar a Cristo.',
   'Pentecostés nos recuerda que la vida cristiana no está llamada a encerrarse en sí misma. El Espíritu nos reúne en la Iglesia, nos fortalece y nos impulsa a dar testimonio del Evangelio allí donde vivimos: en nuestra familia, nuestro trabajo y nuestras relaciones.'],
  '¿En qué lugar concreto puedo dar hoy testimonio de Cristo?'),
 ('Los signos de su presencia','Mateo 3, 16 · Hechos 2, 1-4 · Catecismo, 694-701',
  ['Agua, fuego, viento, nube, unción y paloma: la Biblia utiliza imágenes que nos ayudan a contemplar la acción del Espíritu Santo. El agua evoca la vida nueva; el fuego, su poder transformador; el viento, su libertad; y la paloma recuerda su manifestación en el bautismo de Jesús.',
   'Estos signos no encierran al Espíritu ni agotan el misterio de su presencia. Nos ayudan a comprender, mediante realidades visibles, algo de la obra invisible de Dios.'],
  '¿Qué signo bíblico me ayuda hoy a comprender mejor la acción del Espíritu Santo?'),
 ('Los siete dones del Espíritu Santo','Isaías 11, 2-3 · Catecismo, 1830-1831',
  ['Sabiduría, entendimiento, consejo, fortaleza, ciencia, piedad y temor de Dios: estos son los siete dones que la tradición católica reconoce en la acción del Espíritu Santo.',
   'No son habilidades que conquistamos por nuestro propio esfuerzo, sino disposiciones que nos hacen más dóciles a su acción. Nos ayudan a vivir nuestra fe, comprender mejor las cosas de Dios y responder con mayor fidelidad a su gracia.'],
  '¿Qué don necesito pedir de manera especial para vivir con mayor fidelidad mi vocación?'),
 ('Los frutos del Espíritu','Gálatas 5, 22-23 · Catecismo, 1832',
  ['El Espíritu Santo obra silenciosamente en el corazón que se abre a su gracia. Como una semilla que crece y da fruto, nuestra vida se transforma cuando permitimos que Dios purifique nuestros deseos, ordene nuestros afectos y nos enseñe a amar como Cristo.',
   'Los frutos del Espíritu son signos de esa transformación: amor (caridad), alegría, paz, paciencia, longanimidad, benignidad, bondad, mansedumbre, fidelidad, modestia, continencia y castidad. No son virtudes que conquistamos únicamente con nuestro esfuerzo, sino frutos de la gracia que actúa en nosotros y a la que estamos llamados a responder con libertad y generosidad.',
   'Cada pequeña decisión de amar, cada renuncia al egoísmo y cada acto de fidelidad pueden convertirse en tierra fértil para que estos frutos maduren en nuestra vida.'],
  '¿Qué fruto del Espíritu Santo necesito cultivar hoy para parecerme más a Cristo?'),
 ('Aprender a discernir','Romanos 12, 2 · 1 Tesalonicenses 5, 19-21',
  ['No todo deseo intenso es una llamada de Dios, ni toda emoción agradable significa que estemos eligiendo lo mejor. Discernir es examinar lo que sucede en nuestro interior y preguntarnos hacia dónde nos conduce, a la luz del Evangelio.',
   'La oración, la Palabra de Dios, la enseñanza de la Iglesia y el consejo prudente nos ayudan a examinar nuestras decisiones. No necesitamos resolverlo todo de inmediato: podemos aprender a reconocer los movimientos del corazón con paciencia y humildad.'],
  '¿Qué decisión necesito examinar con más calma y poner en oración?'),
 ('Consolación y desolación','Salmo 143, 10 · Ejercicios espirituales, 316-317',
  ['San Ignacio nos enseña a prestar atención a los movimientos interiores que experimentamos en nuestra relación con Dios. La consolación nos orienta hacia la fe, la esperanza y el amor; la desolación puede traer oscuridad, inquietud y desaliento en la vida espiritual.',
   'No debemos confundirlas simplemente con emociones positivas y negativas. Lo importante es examinar qué está ocurriendo en el corazón, qué dirección toma y cómo afecta nuestra relación con Dios. En tiempos de desolación, san Ignacio aconseja no abandonar precipitadamente los buenos propósitos ni tomar decisiones importantes desde la confusión.'],
  '¿Qué me ayuda a permanecer fiel a Dios cuando no siento consuelo?'),
 ('Un solo Espíritu, muchos dones','1 Corintios 12, 4-7 · Catecismo, 798-801',
  ['El Espíritu Santo distribuye dones diversos para el bien común. No todos recibimos las mismas capacidades ni estamos llamados a realizar las mismas tareas, pero cada uno puede contribuir a la edificación de la Iglesia.',
   'Nuestros talentos no son únicamente para nuestro beneficio. Cuando los ponemos al servicio de los demás con caridad y humildad, se convierten en una forma concreta de responder a la gracia recibida.'],
  '¿Qué don o capacidad puedo poner hoy al servicio de los demás?'),
 ('Permanecer y seguir respondiendo','Gálatas 5, 25 · Filipenses 1, 6',
  ['Llegar al final del año no significa haberlo hecho todo bien ni haber comprendido cada paso. Significa que podemos volver la mirada hacia Dios, agradecer su fidelidad, reconocer nuestras faltas y comenzar de nuevo.',
   'La vida en el Espíritu es un camino de crecimiento y conversión, significa renovar cada día nuestra disponibilidad, confiando en que Dios sigue obrando en nosotros.'],
  'Al mirar este año, ¿dónde reconozco la gracia de Dios y qué deseo confiarle para el año que viene?'),
]

DONES = [
 ('Sabiduría','Nos ayuda a mirar la vida con los ojos de Dios y a reconocer lo que verdaderamente nos conduce a Él. Nos permite gustar de las cosas de Dios y ordenar nuestras decisiones según su amor, sin quedarnos en lo superficial.'),
 ('Entendimiento','Ilumina nuestra inteligencia para comprender más profundamente las verdades de la fe y descubrir el sentido de la Palabra de Dios. Nos ayuda a penetrar en el misterio de su presencia y de su obra, más allá de lo que percibimos a simple vista.'),
 ('Consejo','Nos ayuda a discernir qué es lo correcto en las situaciones concretas de la vida y a elegir los medios adecuados para obrar según la voluntad de Dios. Nos dispone a escuchar antes de actuar y a buscar el bien propio y el de los demás.'),
 ('Fortaleza','Nos da firmeza para perseverar en el bien, afrontar las dificultades y permanecer fieles a Dios incluso cuando seguirlo exige sacrificio. Nos sostiene tanto en las grandes pruebas como en el esfuerzo silencioso de cada día.'),
 ('Ciencia','Nos permite reconocer a Dios en la creación, en los acontecimientos y en nuestra propia historia. Nos enseña a mirar las cosas creadas con rectitud, a descubrir su lugar en el plan de Dios y a no confundir los bienes pasajeros con nuestro fin último.'),
 ('Piedad','Despierta en nosotros un amor filial hacia Dios, a quien reconocemos como Padre, y nos mueve a relacionarnos con Él con confianza y reverencia. También nos hace más sensibles a las necesidades de los demás, fortaleciendo nuestra fraternidad y nuestro deseo de servir.'),
 ('Temor de Dios','No es miedo a Dios, sino reverencia amorosa ante su grandeza y un profundo deseo de no separarnos de Él. Nos ayuda a rechazar el pecado, reconocer nuestra necesidad de su gracia y vivir con humildad, confiando en su misericordia.'),
]

FRUTOS = [
 ('Amor','Es el primero de los frutos del Espíritu Santo, fundamento y raíz de todos los demás. Siendo Él la infinita caridad, o sea, el Amor Infinito, es lógico que comunique al alma su llama, haciéndole amar a Dios con todo el corazón, con todas las fuerzas y con toda la mente, y al prójimo por amor a Dios. Donde falta este amor no puede encontrarse ninguna acción sobrenatural, ningún mérito para la vida eterna, ninguna verdadera y completa felicidad. Es lógico, también, que la caridad sea un dulcísimo fruto, porque amar a Dios es alcanzar el propio fin en la tierra y es el principio de esta unión en la eternidad.'),
 ('Alegría','Es el fruto que emana espontáneamente de la caridad, como el perfume de la flor, la luz del sol, el calor del fuego. Da al alma un gozo profundo, producto de la satisfacción que se tiene de la victoria lograda sobre sí mismo y de haber hecho el bien. Esta alegría no se apaga en las tribulaciones: crece por medio de ellas. Es alegría desbordada.'),
 ('Paz','La verdadera alegría lleva en sí la paz, que es su perfección, porque supone y garantiza el tranquilo goce del objeto amado. El objeto amado, por excelencia, no puede ser otro sino Dios, y de ahí que la paz sea la tranquila seguridad de poseerlo y estar en su gracia. Esta es la paz del Señor, que supera todo sentido, como dice San Pablo (Flp 4, 7), pues es una alegría que supera todo goce fundado en la carne o en las cosas materiales, y para obtenerla debemos inmolar todo a Dios.'),
 ('Paciencia','Siendo la vida una permanente lucha contra enemigos visibles e invisibles, y contra las fuerzas del mundo y del infierno, es necesaria mucha paciencia para superar las turbaciones que estas luchas producen en nosotros, y para encontrarnos en armonía con las criaturas con que tratamos, de diferente carácter, educación y aspiraciones, y a menudo dominadas por ideas fijas de todo tipo.'),
 ('Longanimidad','Este fruto del Espíritu Santo confiere al alma una amplitud de vista y de generosidad por las cuales sabe esperar la hora de la Divina Providencia cuando ve que se retrasa el cumplimiento de sus designios, y sabe tener bondad y paciencia con el prójimo, sin cansarse por su resistencia y su oposición. Longanimidad es lo mismo que gran coraje y gran ánimo en las dificultades que se oponen al bien; es un ánimo sobrenaturalmente grande para concebir y ejecutar las obras de la verdad.'),
 ('Benignidad','Es disposición constante a la indulgencia y a la afabilidad en el hablar, en el responder y en el actuar. Se puede ser bueno sin ser benigno, teniendo un trato rudo y áspero con los demás; la benignidad vuelve sociable y dulce en las palabras y en el trato, a pesar de la rudeza y aspereza de los demás. Es una gran señal de la santidad de un alma y de la acción en ella del Espíritu Santo.'),
 ('Bondad','Es el afecto que se tiene en beneficiar al prójimo. Es como el fruto de la benignidad para quien sufre y necesita ayuda. La bondad, efecto de la unión del alma con Dios, bondad infinita, infunde el espíritu cristiano sobre el prójimo, haciendo el bien y sanando a imitación de Jesucristo.'),
 ('Mansedumbre','La mansedumbre se opone a la ira y al rencor: a la ira que quiere imponerse a los demás y al rencor que quiere vengarse por las ofensas recibidas. La mansedumbre hace al cristiano paloma sin hiel, cordero sin ira, dulzura en las palabras y en el trato frente a la prepotencia de los demás.'),
 ('Fidelidad','Mantener la palabra dada, ser puntuales en los compromisos y horarios, es virtud que glorifica a Dios, que es verdad. Quien promete sin cumplir, quien fija hora para un encuentro y llega tarde, quien es cortés delante de una persona y luego la desprecia a sus espaldas, falta a la sencillez de la paloma sugerida por Jesucristo e induce a los demás a la incertidumbre en las relaciones sociales.'),
 ('Modestia','La modestia, como lo dice su nombre, pone el modo, es decir, regula la manera apropiada y conveniente en el vestir, en el hablar, en el caminar, en el reír, en el jugar. Como reflejo de la calma interior, guarda nuestros ojos para que no se fijen en cosas vulgares e indecorosas, reflejando en ellos la pureza del alma, y armoniza nuestros labios uniendo a la sonrisa la simplicidad y la caridad, excluyendo de todo ello lo áspero y maleducado.'),
 ('Continencia','La continencia mantiene el orden en el interior del hombre y, como indica su nombre, contiene en los justos límites la concupiscencia, no solo en lo que atañe a los placeres sensuales, sino también en lo que concierne al comer, al beber, al dormir, al divertirse y en los otros placeres de la vida material. La satisfacción de todos estos instintos, que asemejan al hombre a los animales, es ordenada por la continencia, que tiene como fin el amor a Dios.'),
 ('Castidad','La castidad es la victoria conseguida sobre la carne y hace del cristiano templo vivo del Espíritu Santo. El alma casta, ya sea virgen o casada (porque también existe la castidad conyugal, en el perfecto orden y empleo del matrimonio), reina sobre su cuerpo en gran paz y siente en ella la inefable alegría de la íntima amistad de Dios, habiendo dicho Jesús: «Felices los limpios de corazón, porque verán a Dios».'),
]

# ---------------------------------------------------------------- CSS adicional para la agenda completa
CSS = r"""
.pagina-num{position:absolute;bottom:7mm;font-size:6.5pt;color:var(--rose);letter-spacing:.1em}
.verso .pagina-num{right:20mm}.recto .pagina-num{left:20mm}
.titulo-pag{font-family:'Fraunces',serif;font-style:italic;font-weight:400;font-size:20pt;color:var(--m,var(--borgona));margin-bottom:1mm;line-height:1.05}
.sub-pag{font-size:7pt;color:var(--suave);margin-bottom:4mm;line-height:1.4}
.txt p{font-size:7.6pt;line-height:1.5;margin-bottom:2mm;text-align:justify;hyphens:auto}
.txt h4{font-family:'Fraunces',serif;font-size:9.5pt;font-weight:500;color:var(--borgona);margin:2.4mm 0 .6mm}
.txt h4 span{color:var(--oro);font-style:italic;margin-right:1.5mm}
.txt .canto{font-family:'Fraunces',serif;font-style:italic;color:var(--uva);text-align:center;font-size:8.2pt;line-height:1.4;margin:3mm 6mm}
.dos-col{columns:2;column-gap:5mm}
.dos-col .item{break-inside:avoid}
.frutos p{font-size:6.7pt;line-height:1.45;margin-bottom:1.6mm}
.frutos h4{font-size:8.8pt;margin-top:0}
/* datos personales */
.datos .marca{text-align:center;margin:6mm 0 8mm}
.datos .marca b{display:block;font-family:'Fraunces',serif;font-weight:400;font-size:28pt;color:var(--borgona);font-style:italic}
.datos .marca span{font-size:7pt;letter-spacing:.35em;color:var(--oro);font-weight:800}
.campo{display:flex;align-items:flex-end;gap:2mm;height:9mm;border-bottom:.2mm solid #b9a8a3;font-size:7pt;font-weight:700;color:var(--uva);letter-spacing:.05em}
.datos .nota{margin-top:7mm;font-family:'Fraunces',serif;font-style:italic;font-size:8.4pt;color:var(--borgona);text-align:center;line-height:1.4}
/* calendario anual */
.anual{display:grid;grid-template-columns:repeat(3,1fr);gap:4mm 4mm}
.mini h5{font-family:'Fraunces',serif;font-style:italic;font-weight:400;font-size:8.6pt;color:var(--borgona);margin-bottom:1mm;text-align:center}
.mini .g{display:grid;grid-template-columns:repeat(7,1fr);text-align:center;font-size:5.6pt;row-gap:.9mm}
.mini .g .w{font-weight:800;color:var(--oro);font-size:4.8pt}
.mini .g .fer{color:var(--feriado);font-weight:800;font-style:italic}
.mini .g .dom{color:var(--borgona);font-weight:700}
.leyenda{margin-top:5mm;font-size:6pt;color:var(--suave);text-align:center}
.leyenda b{color:var(--feriado);font-style:italic}
/* listas genéricas */
.tabla-lista{width:100%;border-collapse:collapse;font-size:6pt}
.tabla-lista th{background:var(--m);color:#fff;font-weight:700;letter-spacing:.08em;text-transform:uppercase;font-size:5.4pt;padding:1.4mm 1mm}
.tabla-lista td{border-bottom:.2mm solid #cdb9b2;height:6.1mm}
.tabla-lista td.c{width:9mm;text-align:center;color:var(--oro)}
.doce-box{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(4,1fr);gap:2.2mm;height:calc(100% - 22mm)}
.colec{display:grid;grid-template-columns:repeat(3,1fr);grid-template-rows:repeat(3,1fr);gap:3mm;height:calc(100% - 28mm)}
.colec div{border:.3mm dashed var(--oro);border-radius:1.5mm}
.victorias{columns:2;column-gap:5mm;height:calc(100% - 22mm)}
.victorias div{height:7.5mm;border-bottom:.2mm solid #cdb9b2;font-size:7pt;color:var(--oro);display:flex;align-items:flex-end;padding-bottom:.6mm}
.collage{position:absolute;inset:22mm 0 0 0;border:.3mm dashed var(--oro);border-radius:2mm}
.collage span{position:absolute;font-family:'Fraunces',serif;font-style:italic;font-size:8pt;color:var(--uva);background:#fff;padding:0 1.5mm}
.fotos{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:5mm;height:calc(100% - 22mm)}
.polaroid{background:#fff;border:.25mm solid #cdb9b2;padding:3mm 3mm 9mm;box-shadow:0 .4mm 1.2mm rgba(0,0,0,.08);position:relative}
.polaroid:nth-child(odd){transform:rotate(-1.5deg)}.polaroid:nth-child(even){transform:rotate(1.2deg)}
.polaroid div{height:100%;background:var(--fondo-rose)}
.polaroid::after{content:"";position:absolute;left:3mm;right:3mm;bottom:3.5mm;border-bottom:.2mm solid #cdb9b2}
.puntos-pag{position:absolute;inset:0;background-image:radial-gradient(circle,#c9b6b0 .22mm,transparent .3mm);background-size:5mm 5mm;background-position:2.5mm 2.5mm}
.dones-v{display:flex;flex-direction:column;gap:3.2mm;margin-top:2mm}
.dones-v .d{display:flex;align-items:center;gap:3mm}
.dones-v img{width:6mm}
.dones-v b{font-family:'Fraunces',serif;font-weight:400;font-style:italic;font-size:13pt;color:var(--borgona);width:34mm}
.dones-v i{flex:1;border-bottom:.2mm solid #cdb9b2;height:6mm}
.reverso{background:var(--m)}
.reverso .orn{position:absolute;inset:-10mm -18mm;background:url(img/ornamento.png) center/cover no-repeat;opacity:.35}
.cm2 .mis{flex:1;border:.2mm solid #b9a8a3;border-radius:1mm;padding:1.4mm 2mm;height:15mm;display:flex;flex-direction:column}
.cm2 .mis .k{font-size:5.4pt;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--m)}
.cm2 .mis p{font-size:6.2pt;line-height:1.35;color:var(--tinta);margin-top:.6mm}
.cm2 .qr2{width:15mm;height:15mm;border:.2mm dashed var(--oro);font-size:4.6pt;color:var(--suave);display:flex;align-items:center;justify-content:center;text-align:center;line-height:1.2;padding:1mm}
.cm2 .notas-col{border:.18mm solid #b9a8a3;display:flex;flex-direction:column}
.cm2 .notas-col .lin{flex:1;--lc:#e1d3ce}
.cm2 .santoral2{border-top:2mm solid var(--m);padding:1.4mm 1.8mm}
.cm2 .santoral2 .k{font-family:'Fraunces',serif;font-size:7pt;color:var(--m);margin-bottom:.6mm}
.cm2 .santoral2 li{list-style:none;font-size:4.9pt;line-height:1.42;font-style:italic;color:var(--tinta)}
.cm2 .santoral2 li.fer{color:var(--feriado)}.cm2 .santoral2 li.pre{font-weight:800}
.sw .dh.fuera{opacity:.55}
.lin-s{border-bottom:.2mm solid #cdb9b2;height:7.5mm}
.pend-txt{font-size:5.5pt;color:var(--feriado);font-style:italic}
"""

# ---------------------------------------------------------------- utilidades
def esc(t): return html.escape(t, quote=False)
def lineas(n, cls='ln'): return f'<div class="{cls}"></div>' * n
FONDO = '<div class="fondo-orn"></div>'

def pag(cls, cuerpo, folio='', color='#4c1825', extra=''):
    return {'cls': cls, 'html': cuerpo, 'folio': folio, 'color': color, 'extra': extra}

def banda(t): return f'<div class="banda">{esc(t)}</div>'

def feriado_txt(m, d):
    x = F.get((m, d)); return x

# ---------------------------------------------------------------- páginas del inicio
def p_datos():
    campos = ['Nombre','Celular','Correo','Dirección','Cumpleaños','En caso de emergencia llamar a','Teléfono']
    c = ''.join(f'<div class="campo">{esc(x)}:</div>' for x in campos)
    return pag('datos', f'''<div class="safe">
      <div class="marca"><img src="img/llama.png" style="width:9mm;display:block;margin:0 auto 2mm"><b>Megalücuma</b><span>PLANNER {AÑO}</span></div>
      <div class="eyebrow" style="margin-bottom:2mm">Esta agenda pertenece a</div>{c}
      <div class="nota">Si encuentras esta agenda, por favor ayúdame a recuperarla.<br>¡Dios te lo pague!</div></div>''', 'Planner 2027')

def p_frutos(parte):
    items = FRUTOS[:6] if parte == 0 else FRUTOS[6:]
    ini = 0 if parte == 0 else 6
    h = ''.join(f'<div class="item"><h4><span>{i+ini+1}.º</span>{t}</h4><p>{esc(x)}</p></div>' for i, (t, x) in enumerate(items))
    tit = '<div class="titulo-pag">Los frutos del Espíritu Santo</div><div class="sub-pag">Gálatas 5, 22-23</div>' if parte == 0 else ''
    return pag('txt frutos', f'<div class="safe">{tit}<div class="dos-col">{h}</div></div>', 'Los frutos del Espíritu Santo')

def p_dones_intro():
    return pag('txt', f'''<div class="safe">
      <div class="titulo-pag">Los siete dones del Espíritu Santo</div><div class="sub-pag">De la fragilidad a la audacia</div>
      <p>Imagina a los discípulos después de la Resurrección. Habían caminado con Jesús, escuchado sus enseñanzas y contemplado sus obras, pero todavía había mucho que no alcanzaban a comprender. Amaban a su Maestro y querían seguirlo, pero cuando llegó la hora de la prueba, el miedo pudo más: huyeron y lo dejaron solo.</p>
      <p><b>¡Cuánto necesitaban la fuerza del Espíritu Santo!</b></p>
      <p>En Pentecostés, sus corazones se llenaron de una valentía nueva. El Espíritu les abrió el entendimiento, fortaleció su fe y los impulsó a anunciar a Cristo sin temor. Aquellos hombres que antes habían vacilado se convirtieron en testigos audaces del Resucitado.</p>
      <p>Y tú, ¿no estás llamado también a dejarte transformar por Él? No tengas miedo. El mismo Espíritu Santo que sostuvo a los apóstoles quiere fortalecerte para vivir tu fe con fidelidad, dar testimonio de Cristo y responder con generosidad a su llamada.</p>
      <div class="canto">♪ Tengo que gritar, tengo que arriesgar, ¡ay de mí si no lo hago!<br>¿Cómo escapar de ti? ¿Cómo no hablar, si tu voz me quema dentro?</div>
      <p>Que el fuego del Espíritu Santo despierte también en ti el deseo de no guardar para ti el amor que has recibido.</p>
      <h4>Los dones del Espíritu Santo</h4>
      <p>Son disposiciones sobrenaturales que el Espíritu Santo infunde en nuestra alma para hacernos dóciles a su acción y ayudarnos a vivir como hijos de Dios. Nos iluminan, fortalecen y orientan para responder con fidelidad a su gracia.</p>
    </div>''', 'Los dones del Espíritu Santo')

def p_dones_lista():
    h = ''.join(f'<h4><span>✦</span>Don de {t[0].lower()+t[1:]}</h4><p>{esc(x)}</p>' for t, x in DONES)
    return pag('txt', f'<div class="safe" style="top:16mm">{h}</div>', 'Los dones del Espíritu Santo')

def p_dones_tercera():
    d = ''.join(f'<div class="d"><img src="img/llama.png"><b>{t}</b><i></i></div>' for t, _ in DONES)
    return pag('', f'''<div class="safe">{banda('Mis dones y frutos')}
      <div class="sub-pag" style="text-align:center">Sabiduría, entendimiento, consejo, fortaleza, ciencia, piedad y temor de Dios.<br>¿Cómo los veo obrar en mi vida? ¿Cuál quiero pedir este año?</div>
      <div class="dones-v">{d}</div>
      <div class="t titulo-sec" style="margin-top:6mm">El fruto que quiero cultivar este año</div>{lineas(3,'ln lin-s')}
    </div>''', 'Los dones del Espíritu Santo')

def mini_mes(y, m, con_fer=True):
    first = (dt.date(y, m, 1).weekday()); dias = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)).day
    cel = ''.join(f'<span class="w">{x}</span>' for x in 'LMMJVSD') + '<span></span>' * first
    for d in range(1, dias + 1):
        x = F.get((m, d)) if (con_fer and y == AÑO) else None
        dom = dt.date(y, m, d).weekday() == 6
        cls = 'fer' if (x and x[1]) else ('dom' if dom else '')
        cel += f'<span class="{cls}">{d}</span>'
    return f'<div class="mini"><h5>{MESES[m-1]}</h5><div class="g">{cel}</div></div>'

def p_anual(y):
    leyenda = '<div class="leyenda"><b>Naranja</b>: feriados en el Perú</div>' if y == AÑO else ''
    return pag('', f'<div class="safe">{banda(f"Calendario {y}")}<div class="anual">{"".join(mini_mes(y, m) for m in range(1,13))}</div>{leyenda}</div>', f'Calendario {y}')

def p_doce(titulo, sub='', color='#694463'):
    cajas = ''.join(f'<div class="mesbox"><h5>{m}</h5><div class="lin"></div></div>' for m in MESES)
    s = f'<div class="sub-pag" style="text-align:center;margin:-2mm 0 2.5mm">{esc(sub)}</div>' if sub else ''
    return pag('eventos', f'{FONDO}<div class="safe">{banda(titulo)}{s}<div class="doce-box">{cajas}</div></div>', titulo, color)

def p_prop():
    arco = lambda t: f'''<div class="arco"><h4>{t}</h4><div class="q obj">Objetivo</div><div class="ln lin"></div>
      <div class="q">¿Por qué es importante?</div><div class="ln lin"></div><div class="q">¿Qué necesito?</div><div class="ln lin"></div>
      <div class="q">Estrategia</div><div class="ln lin" style="flex:1"></div></div>'''
    return pag('prop', f'{FONDO}<div class="safe">{banda("Propósitos trimestrales")}<div class="cuatro">{"".join(arco(t) for t in ["Ene · Feb · Mar","Abr · May · Jun","Jul · Ago · Sep","Oct · Nov · Dic"])}</div></div>', 'Propósitos trimestrales')

def p_collage():
    etiquetas = [('Viaje','top:-2mm;left:6mm'),('Paseo','top:-2mm;right:8mm'),('Actividades','top:45%;left:-1mm;transform:rotate(-90deg) translateX(-50%);transform-origin:left'),
                 ('Personas que visitar','bottom:-2mm;left:6mm'),('Algo nuevo que preparar','bottom:-2mm;right:6mm')]
    e = ''.join(f'<span style="{s}">{t}</span>' for t, s in etiquetas)
    return pag('', f'<div class="safe">{banda("Collage creativo")}<div class="collage">{e}</div></div>', 'Collage creativo')

def p_peliculas():
    filas = ''.join('<tr><td></td><td class="c">○</td><td class="c">○</td><td class="c">☆☆☆</td></tr>' for _ in range(23))
    return pag('', f'''<div class="safe">{banda("Películas, documentales y videos")}
      <div class="sub-pag" style="text-align:center;margin-top:-2mm">Los que voy viendo o tengo pendientes</div>
      <table class="tabla-lista"><tr><th style="text-align:left">Título</th><th>Pendiente</th><th>Visto</th><th>Me gustó</th></tr>{filas}</table></div>''', 'Películas', '#694463')

def p_habla():
    cajas = ''.join(f'<div class="mesbox"><h5>{m}</h5><div class="lin"></div></div>' for m in MESES)
    return pag('eventos', f'''{FONDO}<div class="safe">{banda("Habla, Señor, que tu siervo escucha")}
      <div class="sub-pag" style="text-align:center;margin:-2mm 0 2.5mm">Mis oraciones al Espíritu Santo</div><div class="doce-box">{cajas}</div></div>''', 'Habla, Señor', '#4c1825')

def p_coleccion():
    return pag('', f'''<div class="safe">{banda("Mi colección")}
      <div class="sub-pag" style="text-align:center;margin-top:-1mm">Colecciona algo que puedas pegar aquí. Desde envolturas de algo particular, boletos, tickets, códigos de barra, lo que sea que te haya llamado la atención. ¡Será lindo verlo completamente lleno!</div>
      <div class="colec">{"<div></div>"*9}</div></div>''', 'Mi colección', '#4a4526')

def p_victorias():
    v = ''.join('<div>✦</div>' for _ in range(40))
    return pag('', f'<div class="safe">{banda("Pequeñas victorias")}<div class="victorias">{v}</div></div>', 'Pequeñas victorias', '#9a6e65')

def p_rutina():
    horas = [f'{h}:{m:02d}' for h in range(5, 23) for m in (0, 20, 40)][:-2]
    mitad = (len(horas) + 1) // 2
    col = lambda hs: '<div>' + ''.join(f'<div class="h"><b>{h}</b><span></span></div>' for h in hs) + '</div>'
    return pag('rutina', f'<div class="safe">{banda("Mi rutina diaria")}<div class="horas">{col(horas[:mitad])}{col(horas[mitad:])}</div><div class="notas"><em>Notas:</em></div></div>', 'Mi rutina diaria')

# ---------------------------------------------------------------- calendario highlights (doble página)
def semanas_cal(m):
    first = dt.date(AÑO, m, 1); ini = first - dt.timedelta(days=first.weekday())
    dias = (dt.date(AÑO + (m == 12), m % 12 + 1, 1) - first).days
    filas = -(-(first.weekday() + dias) // 7)
    return ini, filas

def p_highlights(m):
    color = COLOR_MES[m-1]; ini, filas = semanas_cal(m)
    def celda(fecha, fila, colu):
        st = f'grid-row:{fila+2};grid-column:{colu}'
        if fecha.month != m: return f'<div class="c vacio" style="{st}"></div>'
        x = F.get((m, fecha.day)); fer = 'fer' if (x and x[1]) else ''
        return f'<div class="c {fer}" style="{st}"><span class="n">{fecha.day}</span></div>'
    izq = ''.join(f'<div class="dw">{d}</div>' for d in DIAS[:4]); der = ''.join(f'<div class="dw">{d}</div>' for d in DIAS[4:]) + '<div class="dw">Notas</div>'
    for r in range(filas):
        for c in range(7):
            fe = ini + dt.timedelta(days=r*7 + c)
            if c < 4: izq += celda(fe, r, c + 1)
            else: der += celda(fe, r, c - 3)
    fest = ''.join(f'<li class="{"fer" if v[1] else ""} {"pre" if v[2] else ""}">{d} {esc(v[0])}</li>' for (mm, d), v in sorted(F.items()) if mm == m)
    der += f'<div class="notas-col" style="grid-row:2 / span {filas};grid-column:4"><div class="lin"></div><div class="santoral2"><div class="k">Santoral y feriados</div><ul>{fest}</ul></div></div>'
    rows = f'grid-template-rows:6mm repeat({filas},1fr)'
    a = pag('cm cm2', f'''<div class="safe"><div class="cab"><h2>{MESES[m-1]}</h2><div class="fr"><span class="pend-txt">Frase bonita del mes (pendiente)</span></div></div>
         <div class="rejilla" style="{rows}">{izq}</div></div>''', f'{MESES[m-1]} · Highlights', color)
    b = pag('cm cm2', f'''<div class="pestana-mes" style="top:{16 + (m-1)*12.5}mm">{ABR[m-1]}</div><div class="safe"><div class="cab" style="gap:2.5mm">
         <div class="mis"><span class="k">💌 Misión secreta del mes</span><p class="pend-txt">(Pendiente)</p></div>
         <div class="qr2">QR<br>recetas o videos</div></div>
         <div class="rejilla" style="{rows}">{der}</div></div>''', f'{MESES[m-1]} · Highlights', color)
    return (a, b)

# ---------------------------------------------------------------- sección mensual
def p_caratula(m):
    t, ref, ps, med = CARATULAS[m-1]; color = COLOR_MES[m-1]
    pp = ''.join(f'<p>{esc(x)}</p>' for x in ps)
    largo = sum(len(x) for x in ps) > 650
    estilo = ' style="font-size:7.2pt"' if largo else ''
    cuerpo = f'''<div class="orn"></div><div class="pestana" style="top:{16 + (m-1)*12.5}mm;background:var(--oro)"><span>{MESES[m-1].upper()}</span></div>
      <div class="safe"><div class="num">{m:02d} · {AÑO}</div><div class="mes">{MESES[m-1]}</div>
      <h2>{esc(t)}</h2><div class="ref">{esc(ref)}</div><div{estilo}>{pp}</div>
      <div class="meditar"><span>Para meditar</span>{esc(med)}</div></div>'''
    return pag('caratula', cuerpo, '', color, f'background:{color}')

def p_reverso(m):
    return pag('reverso', '<div class="orn"></div>', '', COLOR_MES[m-1])

def p_panorama(m):
    color = COLOR_MES[m-1]; L = lambda n: lineas(n)
    bulbo = '<svg viewBox="0 0 100 120"><defs><pattern id="pd{m}" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r=".7" fill="#c9b6b0"/></pattern></defs><path d="M50 6C27 6 12 23 12 44c0 15 8 24 15 32 5 6 7 11 7 17h32c0-6 2-11 7-17 7-8 15-17 15-32C88 23 73 6 50 6z" fill="url(#pd{m})" stroke="COL" stroke-width="1.4"/><path d="M35 99h30M37 106h26M42 113h16" stroke="COL" stroke-width="1.4" stroke-linecap="round"/><path d="M8 14l6 5M92 14l-6 5M2 44h6M98 44h-6" stroke="#c3934b" stroke-width="1.6" stroke-linecap="round"/></svg>'.replace('{m}', str(m)).replace('COL', color)
    nube = '<svg viewBox="0 0 120 90"><defs><pattern id="pn{m}" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r=".7" fill="#c9b6b0"/></pattern></defs><path d="M28 80c-14 0-22-9-22-20 0-10 7-17 16-19-1-14 10-26 25-26 9 0 16 4 20 10 4-4 10-6 16-6 14 0 25 11 25 24v2c7 3 11 9 11 16 0 11-9 19-21 19z" fill="url(#pn{m})" stroke="COL" stroke-width="1.3"/></svg>'.replace('{m}', str(m)).replace('COL', color)
    a = pag('pn', f'''<div class="safe">
      <div class="pn-cab"><div class="titulo">Panorama<br>del mes</div><p>{MESES[m-1]} {AÑO}<br>Un espacio para organizar, descubrir, disfrutar y agradecer a Dios.</p></div>
      <div class="frase"><div class="t">Frase del mes <span>o cita bíblica</span></div>{L(2)}</div>
      <div class="t">Este mes quiero poner especial atención en mis 3 prioridades</div>
      <div class="prio"><div class="caja pts"><b>1</b></div><div class="caja pts"><b>2</b></div><div class="caja pts"><b>3</b></div></div>
      <div class="tri" style="height:50mm;margin-bottom:3mm">
        <div class="caja compras"><div class="t">Compras importantes</div>{L(7)}</div>
        <div class="caja arquito pts" style="text-align:center;padding-top:4mm"><div class="t">Pendientes<br>en casa</div></div>
        <div class="caja balance"><div class="t">Balance del mes</div><div class="f">Presupuesto<span>S/</span></div><div class="f">Ingreso extra<span>S/</span></div><div class="f">Gastos<span>S/</span></div><div class="f">Ahorro<span>S/</span></div></div>
      </div>
      <div class="tri" style="height:44mm">
        <div class="descub"><div class="cinta-t">Pequeños descubrimientos</div><div class="f">Canción:<i></i></div><div class="f">Lugar:<i></i></div><div class="f">Receta:<i></i></div><div class="f">Otro:<i></i></div></div>
        <div style="display:flex;flex-direction:column"><div class="cinta-t" style="align-self:center">No olvidar</div><div class="caja pts" style="flex:1"><span class="pin"></span></div></div>
        <div style="display:flex;flex-direction:column"><div class="cinta-t" style="align-self:center">Fechas importantes</div><div class="caja" style="flex:1">{L(5)}</div></div>
      </div></div>''', f'{MESES[m-1]} · Panorama', color)
    b = pag('pn', f'''<div class="safe">
      <div class="manos"><h3>Este mes pongo en tus manos, <i>Espíritu Santo</i></h3>
        <div class="tabla"><div><span>Alma</span></div><div><span>Corazón</span></div><div><span>Salud</span></div><div><span>Mente</span></div><div class="otros"><span>Otros:</span></div></div></div>
      <div class="masmenos"><div class="mm"><div class="t">♡ Hacer más de</div>{L(3)}<div class="t" style="margin-top:2.5mm">⊘ Hacer menos de</div>{L(3)}</div>
        <div class="caja gracias-box"><div class="gt">Gracias, Señor, por los regalos de este mes</div></div></div>
      <div class="abajo">
        <div class="forma"><div class="t">Una idea</div>{bulbo}</div>
        <div class="forma"><div class="t">Algo que quiero aprender o retomar</div>{nube}</div>
        <div class="caja visitar"><div class="t">Visitar a:</div><div class="f">1<i></i></div><div class="f">2<i></i></div><div class="f">3<i></i></div></div>
        <div class="caja gusto"><div class="t">Un pequeño gusto para mí</div><div class="ola"></div><div class="ola"></div><div class="ola"></div><div class="ola"></div></div>
        <div class="caja pts"></div>
        <div class="caja reflex"><div class="t">Una reflexión</div><p>Un pensamiento, oración o algo que me hizo mirar las cosas de otra manera.</p></div>
      </div></div>''', f'{MESES[m-1]} · Panorama', color)
    return (a, b)

VASO = '<svg viewBox="0 0 10 12"><path d="M1 1h8l-1.2 10H2.2z" fill="#fff" stroke="#694463" stroke-width=".8"/></svg>'
BOCAS = ['M5.5 11.5q4.5 5 9 0','M6 12.5q4 3 8 0','M6.5 13h7','M6 14q4-3 8 0','M7 14.5q3-4 6 0','M5.5 15q4.5-5 9 0']
CARA = lambda b: f'<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="9" fill="#fff" stroke="#694463" stroke-width="1.1"/><circle cx="7" cy="8" r="1" fill="#694463"/><circle cx="13" cy="8" r="1" fill="#694463"/><path d="{b}" fill="none" stroke="#694463" stroke-width="1.1" stroke-linecap="round"/></svg>'
PERSONA = '<svg viewBox="0 0 20 20" style="width:4.6mm;height:4.6mm;flex:none"><circle cx="11" cy="3.5" r="2" fill="#694463"/><path d="M10 6l-2 6 3 2-1 5M10 6l3 5 3 1M8 12l-3 1M9 8l-4 2" fill="none" stroke="#694463" stroke-width="1.4" stroke-linecap="round"/></svg>'
TRK = f'''<div class="trk"><div class="tt">Mi encuentro con Dios</div>
  <div class="dios">{"".join(f"<span><i></i>{t}</span>" for t in ["Oración personal","Santísimo","Rosario","Denario","Misa"])}</div>
  <div class="fila"><span class="lb">¿Comiste saludable?</span><span class="lb">Sí<span class="cb"></span></span><span class="lb">No<span class="cb"></span></span></div>
  <div class="fila"><span class="lb" style="width:7mm">¡Hidrátate!</span><div class="vasos">{VASO*8}</div><div class="sueno"><div class="lb">☾ Sueño</div><span class="h"></span><span class="lb"> h</span></div></div>
  <div class="act">{PERSONA}<div class="ls"><div></div><div></div></div></div>
  <div><div class="lb" style="text-align:center;margin-bottom:.5mm">Mood</div><div class="mood">{"".join(CARA(b) for b in BOCAS)}</div></div></div>'''

def semanas_mes(m):
    first = dt.date(AÑO, m, 1)
    ini = first + dt.timedelta(days=7 - first.weekday()) if first.weekday() >= 5 else first - dt.timedelta(days=first.weekday())
    n = 4 if m == 2 else 5
    return [ini + dt.timedelta(weeks=i) for i in range(n)]

def p_semana(m, lunes, k):
    color = COLOR_MES[m-1]
    def col(fe, fin=False):
        x = F.get((fe.month, fe.day)) if fe.year == AÑO else None
        imp = f'<span style="color:{"var(--feriado)" if x and x[1] else "var(--oro)"};{"font-weight:800" if x and x[2] else ""}">{esc(x[0])}</span>' if x else ''
        fuera = ' fuera' if fe.month != m else ''
        return f'<div class="col"><div class="dh{fuera}"><small>Día:</small><b>{DIAS[fe.weekday()]}</b><span class="num">{fe.day}</span></div><div class="imp">✦ {imp}</div><div class="{"rayas" if fin else "puntos"}"></div>{"" if fin else TRK}</div>'
    d = [lunes + dt.timedelta(days=i) for i in range(7)]
    fol = f'{MESES[m-1]} · Semana {k}'
    a = pag('sw', f'<div class="safe"><div class="cols">{col(d[0])}{col(d[1])}{col(d[2])}</div></div>', fol, color)
    b = pag('sw', f'<div class="safe"><div class="cols">{col(d[3])}{col(d[4])}<div class="finde">{col(d[5],True)}{col(d[6],True)}</div></div></div>', fol, color)
    return (a, b)

def p_lo_mejor(m):
    return pag('', f'<div class="safe">{banda("Lo mejor del mes")}<div class="fotos">{"<div class=polaroid><div></div></div>"*4}</div></div>', f'{MESES[m-1]} · Lo mejor del mes', COLOR_MES[m-1])

def p_puntos(t='Notas'):
    return pag('', '<div class="puntos-pag"></div>', t)

def p_despedida():
    return pag('txt', f'''<div class="safe" style="display:flex;flex-direction:column;justify-content:center">
      <img src="img/llama.png" style="width:10mm;margin:0 auto 3mm">
      <div class="titulo-pag" style="text-align:center">Despedida</div>
      <p class="pend-txt" style="text-align:center;font-size:7pt">(Pendiente: el documento de Canva no trae aún el texto de despedida 2027)</p>
      <div style="margin-top:6mm">{lineas(12, 'ln lin-s')}</div>
      <div class="firma"><em>Estás en mis oraciones,</em><b>Megalücuma</b></div></div>''', 'Despedida')

# ================================================================ CORRECCIONES 14.11.2026
import sys
REVISION = '--revision' in sys.argv

CSS += r"""
/* Lo que veo y leo */
.vl-grid{display:grid;grid-template-columns:repeat(4,1fr);grid-template-rows:repeat(4,1fr);gap:2.6mm 2.4mm;height:calc(100% - 22mm)}
.vl{display:flex;flex-direction:column;gap:1mm}
.vl .pega{flex:1;border:.3mm dashed var(--oro);border-radius:1mm;background:rgba(255,255,255,.85)}
.vl .est{text-align:center;color:var(--oro);font-size:8pt;letter-spacing:.6mm;line-height:1}
.vl .tit{border-bottom:.2mm solid #cdb9b2;height:3.6mm}
.vl-leyenda{display:flex;justify-content:center;gap:3mm;font-size:5.6pt;color:var(--suave);margin:-2mm 0 2.5mm}
.vl-leyenda b{color:var(--m)}
.tabla-lista td.t{width:4.8mm;text-align:center;color:#cdb9b2;font-size:6pt}
.tabla-lista th.t{width:4.8mm;padding:1.4mm 0}
.tabla-lista td.e{width:16mm;text-align:center;color:var(--oro);font-size:6pt;letter-spacing:.3mm}
/* Panorama reorganizado */
.pn2 .manos .tabla div{height:21mm}
.pn2 .masmenos{grid-template-columns:42mm 1fr;margin:3mm 0}
.pn2 .reflex2{display:grid;grid-template-columns:1fr 34mm;gap:2.5mm;height:44mm}
.pn2 .reflex2 .caja.r{background:var(--fondo-rose);border-color:var(--oro)}
.pn2 .reflex2 .r .gt{font-family:'Fraunces',serif;font-style:italic;font-size:8.5pt;color:var(--m)}
.pn2 .reflex2 .r p{font-size:5.6pt;color:var(--suave);font-style:italic;margin-top:.5mm}
.pn2 .abajo2{display:grid;grid-template-columns:1fr 1fr 30mm;gap:2.5mm;height:43mm}
.forma2{position:relative;border-radius:1mm}
.forma2 svg{position:absolute;inset:0;width:100%;height:100%}
.forma2 .t2{position:absolute;left:0;right:0;text-align:center;font-family:'Fraunces',serif;font-style:italic;font-size:7.6pt;color:var(--m);line-height:1.15}
.pn2 .prio{margin-bottom:3mm}
.pn2 .prio .caja{height:21mm}
.pn2 .tri.a{height:44mm;margin-bottom:3mm}
.pn2 .tri.b{height:40mm;margin-bottom:3mm}
"""

def p_veo_leo():
    caja = '<div class="vl"><div class="pega"></div><div class="tit"></div><div class="est">☆☆☆☆☆</div></div>'
    tipos = [('L','libro'),('P','película'),('D','documental'),('V','video'),('T','obra de teatro')]
    ley = '<div class="vl-leyenda">' + ''.join(f'<span><b>{a}</b> {b}</span>' for a, b in tipos) + '</div>'
    filas = ''.join('<tr><td></td>' + '<td class="t">○</td>'*5 + '<td class="e">☆☆☆☆☆</td></tr>' for _ in range(22))
    a = pag('eventos', f'''{FONDO}<div class="safe">{banda("Lo que veo y leo")}
      <div class="sub-pag" style="text-align:center;margin:-2mm 0 2.5mm">Pega la portada, la entrada o el afiche, y califícalo</div>
      <div class="vl-grid">{caja*16}</div></div>''', 'Lo que veo y leo · tracker', '#4a4526')
    b = pag('', f'''<div class="safe">{banda("Lo que veo y leo")}{ley}
      <table class="tabla-lista"><tr><th style="text-align:left">Título</th>{"".join(f'<th class="t">{x}</th>' for x,_ in tipos)}<th>Me gustó</th></tr>{filas}</table></div>''',
      'Lo que veo y leo · tracker', '#4a4526')
    return (a, b)

def p_highlights(m):
    """Calendario mensual en doble página, igual al modelo de la agenda 2026."""
    color = COLOR_MES[m-1]; ini, filas = semanas_cal(m)
    fest = [(d, v) for (mm, d), v in sorted(F.items()) if mm == m]
    span_f = 2 if (len(fest) > 6 or filas == 6) else 1
    def celda(fe, fila, colu):
        st = f'grid-row:{fila+2};grid-column:{colu}'
        if fe.month != m: return f'<div class="c vacio" style="{st}"></div>'
        x = F.get((m, fe.day)); fer = 'fer' if (x and x[1]) else ''
        return f'<div class="c {fer}" style="{st}"><span class="n">{fe.day}</span></div>'
    izq = ''.join(f'<div class="dw">{d}</div>' for d in DIAS[:4])
    der = ''.join(f'<div class="dw">{d}</div>' for d in DIAS[4:]) + '<div class="dw">Pendientes del mes</div>'
    for r in range(filas):
        for c in range(7):
            fe = ini + dt.timedelta(days=r*7 + c)
            if c < 4: izq += celda(fe, r, c + 1)
            else: der += celda(fe, r, c - 3)
    n_pend = filas - 1 - span_f
    der += f'<div class="pend lin" style="grid-row:2 / span {n_pend};grid-column:4;--lc:#d9c8c2;background-position:0 1mm"></div>'
    lis = ''.join(f'<li class="{"fer" if v[1] else ""} {"pre" if v[2] else ""}">{d} {esc(v[0])}</li>' for d, v in fest)
    der += f'<div class="festivos" style="grid-row:{2+n_pend} / span {span_f};grid-column:4"><div class="t">Días festivos</div><ul>{lis}</ul></div>'
    der += f'<div class="mision" style="grid-row:{filas+1};grid-column:4"><div class="cinta">Misión secreta<br>del mes ✦</div><b>(Título)</b><p>(Pendiente)</p></div>'
    rows = f'grid-template-rows:6mm repeat({filas},1fr)'
    a = pag('cm', f'''<div class="safe"><div class="cab"><h2>{MESES[m-1]}</h2><div class="fr"><i>«Frase bonita del mes (pendiente)».</i> — <b>Autor</b></div></div>
         <div class="rejilla" style="{rows}">{izq}</div></div>''', f'{MESES[m-1]} · Highlights', color)
    b = pag('cm', f'''<div class="pestana-mes" style="top:{16 + (m-1)*12.5}mm">{ABR[m-1]}</div><div class="safe"><div class="cab">
         <div class="player"><div class="ico">▶</div><div class="info"><div class="tt">Canción o video del mes (pendiente)</div><div class="bar"></div><div class="ctl"><span>⏮</span><span class="pl">▶</span><span>⏭</span></div></div></div>
         <div class="qrbox">QR</div></div>
         <div class="rejilla" style="{rows}">{der}</div></div>''', f'{MESES[m-1]} · Highlights', color)
    return (a, b)

def p_panorama(m):
    """Panorama reorganizado: izquierda lo espiritual, derecha lo práctico (corrección 14.11)."""
    color = COLOR_MES[m-1]; L = lambda n: lineas(n)
    pat = f'<defs><pattern id="pp{m}" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r=".55" fill="#c9b6b0"/></pattern></defs>'
    bulbo = f'''<svg viewBox="0 0 100 130" preserveAspectRatio="xMidYMid meet">{pat}
      <path d="M50 14C28 14 14 30 14 50c0 14 7 23 14 31 5 6 7 11 7 17h30c0-6 2-11 7-17 7-8 14-17 14-31 0-20-14-36-36-36z" fill="url(#pp{m})" stroke="{color}" stroke-width="1.3"/>
      <rect x="36" y="101" width="28" height="6" rx="3" fill="none" stroke="{color}" stroke-width="1.3"/><rect x="38" y="109" width="24" height="6" rx="3" fill="none" stroke="{color}" stroke-width="1.3"/><path d="M44 118h12" stroke="{color}" stroke-width="1.3" stroke-linecap="round"/>
      <g stroke="#c3934b" stroke-width="1.5" stroke-linecap="round"><path d="M50 2v6M14 12l4 4M86 12l-4 4M2 48h6M98 48h-6"/></g></svg>'''
    nube = f'''<svg viewBox="0 0 130 100" preserveAspectRatio="xMidYMid meet">{pat}
      <path d="M30 88C15 88 6 78 6 66c0-11 8-19 18-21-1-16 11-29 28-29 10 0 18 5 23 12 4-4 11-7 18-7 16 0 28 12 28 27v2c7 3 12 10 12 18 0 12-10 20-23 20z" fill="url(#pp{m})" stroke="{color}" stroke-width="1.3"/>
      <g fill="#c3934b"><path d="M112 12l1.2-3 1.2 3 3 1.2-3 1.2-1.2 3-1.2-3-3-1.2z"/><path d="M14 20l1-2.4 1 2.4 2.4 1-2.4 1-1 2.4-1-2.4-2.4-1z"/></g></svg>'''
    a = pag('pn pn2', f'''<div class="safe">
      <div class="pn-cab"><div class="titulo">Panorama<br>del mes</div><p>{MESES[m-1]} {AÑO}<br>Un espacio para organizar, descubrir, disfrutar y agradecer a Dios.</p></div>
      <div class="frase"><div class="t">Frase del mes <span>o cita bíblica</span></div>{L(2)}</div>
      <div class="manos"><h3>Este mes pongo en tus manos, <i>Espíritu Santo</i></h3>
        <div class="tabla"><div><span>Alma</span></div><div><span>Corazón</span></div><div><span>Salud</span></div><div><span>Mente</span></div><div class="otros"><span>Otros:</span></div></div></div>
      <div class="masmenos"><div class="mm"><div class="t">♡ Hacer más de</div>{L(3)}<div class="t" style="margin-top:2.5mm">⊘ Hacer menos de</div>{L(3)}</div>
        <div class="caja gracias-box"><div class="gt">Gracias, Señor, por los regalos de este mes</div></div></div>
      <div class="reflex2">
        <div class="caja r pts"><div class="gt">Una reflexión para guardar</div><p>Un pensamiento, oración o algo que me hizo mirar las cosas de otra manera.</p></div>
        <div class="caja gusto"><div class="t">Un pequeño gusto para mí</div><div class="ola"></div><div class="ola"></div><div class="ola"></div><div class="ola"></div><div class="ola"></div></div>
      </div></div>''', f'{MESES[m-1]} · Panorama', color)
    b = pag('pn pn2', f'''<div class="safe">
      <div class="t">Este mes… mis 3 prioridades</div>
      <div class="prio"><div class="caja pts"><b>1</b></div><div class="caja pts"><b>2</b></div><div class="caja pts"><b>3</b></div></div>
      <div class="tri a">
        <div class="caja compras"><div class="t">Compras importantes</div>{L(6)}</div>
        <div class="caja arquito pts" style="text-align:center;padding-top:4mm"><div class="t">Pendientes<br>en casa</div></div>
        <div class="caja balance"><div class="t">Balance del mes</div><div class="f">Presupuesto<span>S/</span></div><div class="f">Ingreso extra<span>S/</span></div><div class="f">Gastos<span>S/</span></div><div class="f">Ahorro<span>S/</span></div></div>
      </div>
      <div class="tri b">
        <div class="descub"><div class="cinta-t">Pequeños descubrimientos</div><div class="f">Canción:<i></i></div><div class="f">Lugar:<i></i></div><div class="f">Receta:<i></i></div><div class="f">Otro:<i></i></div></div>
        <div style="display:flex;flex-direction:column"><div class="cinta-t" style="align-self:center">No olvidar</div><div class="caja pts" style="flex:1"><span class="pin"></span></div></div>
        <div style="display:flex;flex-direction:column"><div class="cinta-t" style="align-self:center">Fechas importantes</div><div class="caja" style="flex:1">{L(4)}</div></div>
      </div>
      <div class="abajo2">
        <div class="forma2">{bulbo}<div class="t2" style="top:42%">Una<br>idea</div></div>
        <div class="forma2">{nube}<div class="t2" style="top:52%">Algo que quiero<br>retomar o aprender</div></div>
        <div class="caja visitar"><div class="t">Visitar a:</div><div class="f">1<i></i></div><div class="f">2<i></i></div><div class="f">3<i></i></div><div class="f">4<i></i></div></div>
      </div></div>''', f'{MESES[m-1]} · Panorama', color)
    return (a, b)

# ---------------------------------------------------------------- reutiliza páginas ya diseñadas en la muestra
muestra = open(os.path.join(AQUI, 'muestra.html')).read()
def seccion(patron):
    return re.search(patron, muestra, re.S).group(0)
hola = re.findall(r'<section class="page (?:verso|recto) hola">.*?</section>', muestra, re.S)
oracion = seccion(r'<section class="page verso oracion">.*?</section>')
frase = seccion(r'<section class="page verso frasep">.*?</section>')
def crudo(s):  # convierte una <section> existente en página
    cls = re.search(r'class="page (?:verso|recto) ?([^"]*)"', s).group(1)
    cuerpo = re.search(r'<section[^>]*>(.*)</section>', s, re.S).group(1)
    cuerpo = re.sub(r'<div class="folio">.*?</div>', '', cuerpo)
    return pag(cls, cuerpo, 'Planner 2027')

# ---------------------------------------------------------------- orden de la agenda (documento de Canva)
doc = []   # cada elemento: página suelta o tupla (izquierda, derecha) que debe caer en doble página
doc += [p_datos()]                                         # 1  Megalücuma + datos personales
doc += [(crudo(hola[0]), crudo(hola[1]))]                   # 2  Hola
doc += [crudo(frase)]                                       # 3  Frase del año
doc += [crudo(oracion)]                                     # 4  Oración al Espíritu Santo
doc += [(p_dones_intro(), p_dones_lista())]                 # 5  Los 7 dones
doc += [(p_frutos(0), p_frutos(1))]                         # 6  Los frutos
doc += [p_dones_tercera()]                                  # 7  Tercera hoja de dones y frutos
doc += [(p_anual(AÑO), p_anual(AÑO + 1))]                   # 8  Calendario 2027 + 2028
doc += [p_doce('Eventos importantes')]                      # 9
doc += [p_prop()]                                           # 10
doc += [p_collage()]                                        # 11
doc += [p_veo_leo()]                                        # 12-13 Lo que veo y leo (corrección 14.11)
doc += [p_habla()]                                          # 14
doc += [p_coleccion()]                                      # 15
doc += [p_victorias()]                                      # 16
doc += [p_rutina()]                                         # 17
for m in range(1, 13): doc += [p_highlights(m)]             # 18 Calendario highlights, uno tras otro
for m in range(1, 13):                                      # 19-22 Sección de cada mes
    doc += [p_caratula(m)]   # el reverso de la carátula es la página izquierda del Panorama
    doc += [p_panorama(m)]
    sems = semanas_mes(m)
    if REVISION: sems = sems[1:2]   # PDF de revisión: solo una semana por mes
    for k, l in enumerate(sems, 1): doc += [p_semana(m, l, 2 if REVISION else k)]
    doc += [p_lo_mejor(m)]
doc += [p_despedida()]                                      # Despedida
doc += [p_puntos() for _ in range(8)]                       # Hojas de puntitos libres

# ---------------------------------------------------------------- paginación: dobles páginas siempre izquierda-derecha
paginas = []
for x in doc:
    if isinstance(x, tuple):
        if len(paginas) % 2 == 0: paginas.append(p_puntos())   # la próxima sería derecha: se agrega una hoja de notas
        paginas += list(x)
    else:
        # la carátula siempre a la derecha
        if x['cls'] == 'caratula' and len(paginas) % 2 == 1: paginas.append(p_puntos())
        paginas.append(x)
while len(paginas) % 4: paginas.append(p_puntos())   # múltiplo de 4 para imprenta

out = []
for i, p in enumerate(paginas, 1):
    lado = 'recto' if i % 2 else 'verso'
    fol = f'<div class="folio">{esc(p["folio"])}</div>' if p['folio'] else ''
    num = f'<div class="pagina-num">{i}</div>' if p['cls'] not in ('caratula', 'reverso') else ''
    out.append(f'<section class="page {lado} {p["cls"]}" style="--m:{p["color"]};{p["extra"]}">{p["html"]}{fol}{num}</section>')

doc_html = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Planner 2027 · Interior</title>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..700;1,9..144,300..600&family=Nunito:ital,wght@0,400..800;1,400..600&display=swap" rel="stylesheet">
<style>{estilos}{CSS}
@media screen{{body{{background:#e9e4e1;padding:10mm;display:flex;flex-wrap:wrap;gap:6mm;justify-content:center}}.page{{box-shadow:0 1mm 4mm rgba(0,0,0,.18)}}}}
</style></head><body>
{chr(10).join(out)}
</body></html>'''
open(os.path.join(AQUI, 'agenda-2027-revision.html' if REVISION else 'agenda-2027.html'), 'w').write(doc_html)
print('páginas:', len(paginas))
