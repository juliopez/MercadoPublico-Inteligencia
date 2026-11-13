// Puente de solo lectura: lenguaje natural -> motor determinista -> contrato de interfaz.
import { crearMotor, ConsultaError } from './motor.js';
import { interpretarLocal } from './interpretar_local.js';

const entero = n => new Intl.NumberFormat('es-CL').format(n);
function presentar(intencion, r) {
  const d=r.datos;
  let explicacion;
  if (intencion.operacion === 'modalidades') {
    // Nunca afirmar que total_procesos equivale a procesos únicos.
    const pregunta=intencion.pregunta_original||'';
    const pideLicitaciones=/\blicitacion(?:es)?\b|\blicitaciones?\b/.test(pregunta);
    const pideComprasAgiles=/\bcompras?\s+agiles?\b/.test(pregunta);
    const busca=pideLicitaciones && !pideComprasAgiles ? 'licitaciones' :
      pideComprasAgiles && !pideLicitaciones ? 'compras_agiles' : null;
    explicacion=busca ? `En ${r.periodo} se registran ${entero(d[busca])} ${busca==='licitaciones'?'licitaciones':'compras ágiles'} según la clasificación de registros publicados.` :
      `En ${r.periodo}: ${entero(d.licitaciones)} registros de licitaciones y ${entero(d.compras_agiles)} de compras ágiles.`;
  } else if (intencion.operacion === 'resumen') {
    explicacion=`En ${r.periodo} hay ${entero(d.registros)} registros de ${r.entidad}. ${entero(d.registros_con_monto)} informan monto; su suma es $ ${entero(d.monto_total_clp)} CLP. Los montos informados no son pagos comprobados.`;
  } else if (intencion.operacion === 'ranking') {
    explicacion=`Principales actores de ${r.entidad} en ${r.periodo}, por ${d.criterio}: `+
      (d.filas.map(x=>`${x.posicion}. ${x.actor}: ${entero(x.valor)}`).join('; ') || 'sin registros');
  } else if (intencion.operacion === 'serie') {
    explicacion=`Comparación de ${r.entidad}: `+d.map(x=>`${x.periodo}: ${entero(x.registros)} registros`).join('; ');
  } else if (intencion.operacion === 'organismo') {
    explicacion=`${d.organismo}: ${entero(d.procesos_unicos)} procesos únicos en ${r.periodo}.`;
  } else throw new ConsultaError('Operación no presentable',400);
  return { estado:'respondida',resultado:{ explicacion, datos:d, fuentes:r.fuentes, cobertura:r.cobertura, metodo:r.metodo } };
}
export function crearFlujoLocal({leerJSON}) {
  let motorPendiente;
  return {
    async consultar(pregunta) {
      if (!motorPendiente) motorPendiente=crearMotor({leerJSON}).catch(e=>{motorPendiente=null;throw e;});
      const motor=await motorPendiente;
      const intencion=interpretarLocal(pregunta,motor.periodosDisponibles);
      if (intencion.necesita_aclaracion) return {estado:'aclaracion',pregunta_aclaracion:'Indica un mes y año publicados, el tipo de registro y la consulta que deseas realizar.'};
      const resultado=await motor.consultar(intencion);
      if (!Array.isArray(resultado.fuentes)||resultado.fuentes.length<2||!resultado.metodo) throw new ConsultaError('Fuentes insuficientes',503);
      return presentar({...intencion,pregunta_original:pregunta.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase()},resultado);
    }
  };
}
