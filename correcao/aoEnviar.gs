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
const PAGINAS_DO_FORMULARIO = 6;  // 3 folhas por bloco, frente e verso (igual ao montar.gs)

function normalizar(s) {
  return String(s || '')
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')  // remove acentos e circunflexos (AÔB -> AOB)
    .toUpperCase()
    .replace(/°|º/g, '')
    .replace(/[’‘′´`]/g, "'").replace(/[”“″]/g, '"').replace(/''/g, '"')   // minutos e segundos digitados no celular
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

// "G1 10-12", "G1 100" ou "G1 10-12 v2" -> {nivel, folhas: ['G1 10', 'G1 11', 'G1 12'], versao}
function lerBloco(codigo) {
  const m = String(codigo || '').trim().toUpperCase().replace(/\s+/g, ' ').match(/^(\w+) (\d+)(?:-(\d+))?(?: V(\d+))?$/);
  if (!m) return null;
  const de = Number(m[2]), ate = Number(m[3] || m[2]);
  if (ate < de || ate - de >= PAGINAS_DO_FORMULARIO / 2) return null;
  const folhas = [];
  for (let n = de; n <= ate; n++) folhas.push(m[1] + ' ' + n);
  const versao = Number(m[4] || 1);
  return { nivel: m[1], folhas, versao, texto: m[1] + ' ' + de + (ate > de ? '-' + ate : '') + (versao > 1 ? ' v' + versao : '') };
}

function aoEnviar(e) {
  const r = e.namedValues;
  const aluno = (r['Aluno'] || [''])[0];
  const digitado = String((r['Código do bloco'] || [''])[0]).trim();
  const tempo = minutos(r['Início'][0], r['Fim'][0]);
  const fotos = (r['Foto da resolução'] || [''])[0];
  const painel = SS.getSheetByName('Painel');
  const erro = msg => painel.appendRow([new Date(), aluno, '', digitado, '', tempo, '', 'ERRO: ' + msg, '', fotos]);

  const bloco = lerBloco(digitado);
  if (!bloco) return erro('código do bloco inválido');

  // Gabarito por folha e versão: [folha, versão, página, item, respostas aceitas, pontos, tempo-padrão da folha]
  const linhas = SS.getSheetByName('Gabarito').getDataRange().getValues().slice(1);
  let feitos = 0, total = 0, limite = 0;
  const errados = [], semGabarito = [];
  bloco.folhas.forEach((folha, i) => {
    const daFolha = linhas.filter(l => String(l[0]).trim().toUpperCase() === folha && Number(l[1]) === bloco.versao);
    if (daFolha.length === 0) { semGabarito.push(folha); return; }
    limite += Number(daFolha[0][6]) || 0;
    daFolha.forEach(([, , pagina, item, aceitas, pontos]) => {
      const campo = `${i + 1}ª folha (${String(pagina).trim().toLowerCase()}) · ${item}`;
      pontos = Number(pontos) || 0;
      total += pontos;
      if (confere((r[campo] || [''])[0], aceitas)) feitos += pontos; else errados.push(campo);
    });
  });
  if (semGabarito.length) return erro('sem gabarito: ' + semGabarito.join(', ') + (bloco.versao > 1 ? ' v' + bloco.versao : ''));

  const nota = total ? Math.round(100 * feitos / total) : 0;
  const dentroDoTempo = !TEMPO_CONTA || !limite || tempo <= limite;
  const status = (nota >= CORTE_NOTA && dentroDoTempo) ? 'Domínio' : 'Repetir';
  painel.appendRow([new Date(), aluno, bloco.nivel, bloco.texto, nota, tempo, limite,
                    status, errados.join(', '), fotos]);
}
