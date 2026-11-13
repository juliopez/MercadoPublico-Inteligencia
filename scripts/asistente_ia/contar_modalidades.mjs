// Motor de consulta aislado del asistente IA. No modifica ETL ni frontend.
// Uso: node scripts/asistente_ia/contar_modalidades.mjs 2026-11
const BASE = "https://juliopez.github.io/MercadoPublico-Inteligencia/frontend-v2/";
const periodo = process.argv[2] || "2026-11";
if (!/^20\d{2}-(0[1-9]|1[0-2])$/.test(periodo)) throw Error("Período inválido");

async function json(path) {
  const url = new URL(path, BASE);
  if (url.origin !== new URL(BASE).origin ||
      !url.pathname.startsWith(new URL(BASE + "data/").pathname)) {
    throw Error("Ruta de datos no autorizada");
  }
  const r = await fetch(url, { headers: { Accept: "application/json" } });
  if (!r.ok) throw Error(`HTTP ${r.status}: ${path}`);
  return r.json();
}

const catalogo = await json("data/catalogo-publico.json");
const item = catalogo.periodos.find(p => p.periodo === periodo);
if (!item) throw Error("Período no publicado");
const partes = item.partes?.procesos;
if (!Array.isArray(partes) || partes.length === 0) throw Error("Sin fragmentos");
const conteos = { "Licitación": 0, "Compra Ágil": 0, "Otras/sin modalidad": 0 };
let total = 0;
for (const ruta of partes) {
  if (typeof ruta !== "string" ||
      !new RegExp(`^data/partes/procesos/${periodo}/[0-9]{4}\\.json$`).test(ruta)) {
    throw Error("Fragmento fuera del catálogo permitido");
  }
  const registros = await json(ruta);
  if (!Array.isArray(registros)) throw Error("Fragmento inválido");
  for (const registro of registros) {
    const modalidad = registro.modalidad;
    if (modalidad === "Licitación" || modalidad === "Compra Ágil") conteos[modalidad]++;
    else conteos["Otras/sin modalidad"]++;
    total++;
  }
}
if (total !== item.conteos?.procesos) {
  throw Error(`Inconsistencia: fragmentos=${total}, catálogo=${item.conteos?.procesos}`);
}
console.log(JSON.stringify({
  periodo, actualizado: catalogo.fecha_publicacion,
  total_procesos: total, modalidades: conteos,
  fuente: new URL("data/catalogo-publico.json", BASE).href,
  advertencia: "Conteos de registros publicados; cobertura potencialmente parcial."
}, null, 2));
