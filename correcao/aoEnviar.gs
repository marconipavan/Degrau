/**
 * Degrau — correção automática dos blocos diários (Google Apps Script)
 *
 * ESTADO: testado com planilha e formulário simulados (correcao/teste/simular.js);
 * falta o teste com envios falsos no Google (passo 7 da montagem).
 *
 * Montagem: correcao/README.md (o montar.gs cria formulário, abas e gatilho).
 */
const SS = SpreadsheetApp.getActive();
const CORTE_NOTA = 90;            // % mínimo para domínio
const TEMPO_CONTA = true;         // false nas duas primeiras semanas do piloto (só registra)

function normalizar(s) {
  return String(s || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')  // remove acentos e circunflexos (AÔB -> AOB)
    .toUpperCase()
    .replace(/°|º/g, '')
    .replace(/\s+/g, '')
    .replace(/,/g, '.');
}

// "19:02", "19:02:00" ou "7:02:00 PM" -> minutos desde a meia-noite
function emMinutos(t) {
  const m = String(t).match(/(\d{1,2}):(\d{2})(?::\d{2})?\s*([AP]M)?/i);
  if (!m) return NaN;
  let h = Number(m[1]);
  if (m[3]) h = h % 12 + (m[3].toUpperCase() === 'PM' ? 12 : 0);
  return h * 60 + Number(m[2]);
}

function minutos(ini, fim) {
  const d = emMinutos(fim) - emMinutos(ini);
  return d < 0 ? d + 24 * 60 : d;
}

// Resposta do tipo conjunto ("conjunto:PÔQ,QÔR,..."): itens em qualquer ordem, separados por
// vírgula, ponto e vírgula ou espaço; nome de ângulo de 3 letras vale nos dois sentidos (QÔP = PÔQ).
function itensConjunto(s) {
  return String(s || '').split(/[,;\s]+/).map(normalizar).filter(x => x)
    .map(x => /^[A-Z]{3}$/.test(x) ? [x, x.split('').reverse().join('')].sort()[0] : x)
    .sort().join(',');
}

function confere(resposta, aceitas) {
  return String(aceitas).split('|').some(a => a.startsWith('conjunto:')
    ? itensConjunto(resposta) === itensConjunto(a.slice('conjunto:'.length))
    : normalizar(resposta) === normalizar(a));
}

function aoEnviar(e) {
  const r = e.namedValues;
  const aluno = (r['Aluno'] || [''])[0];
  const bloco = String((r['Código do bloco'] || [''])[0]).trim().toUpperCase().replace(/\s+/g, ' ');
  const tempo = minutos(r['Início'][0], r['Fim'][0]);
  const fotos = (r['Foto da resolução'] || [''])[0];

  const gab = SS.getSheetByName('Gabarito').getDataRange().getValues().slice(1)
    .filter(l => String(l[0]).trim().toUpperCase().replace(/\s+/g, ' ') === bloco);

  const painel = SS.getSheetByName('Painel');
  if (gab.length === 0) {
    painel.appendRow([new Date(), aluno, '', bloco, '', tempo, '', 'ERRO: bloco sem gabarito', '', fotos]);
    return;
  }

  let feitos = 0, total = 0;
  const errados = [];
  // cada linha do gabarito: [bloco, campo, respostas aceitas, pontos, tempo]; campo = título da pergunta
  gab.forEach(([, campo, aceitas, pontos]) => {
    pontos = Number(pontos) || 0;
    total += pontos;
    const ok = confere((r[campo] || [''])[0], aceitas);
    if (ok) feitos += pontos; else errados.push(campo);
  });

  const nota = total ? Math.round(100 * feitos / total) : 0;
  const limite = Number(gab[0][4]) || 0;
  const dentroDoTempo = !TEMPO_CONTA || !limite || tempo <= limite;
  const status = (nota >= CORTE_NOTA && dentroDoTempo) ? 'Domínio' : 'Repetir';

  painel.appendRow([new Date(), aluno, bloco.split(' ')[0], bloco, nota, tempo, limite,
                    status, errados.join(', '), fotos]);
}
