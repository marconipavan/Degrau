/**
 * Degrau — correção automática dos blocos diários (Google Apps Script)
 *
 * ESTADO: esboço, ainda NÃO testado com um formulário real.
 *
 * Instalação:
 *  1. Crie o formulário (campos em correcao/README.md) e vincule a uma planilha.
 *  2. Na planilha, crie as abas Alunos, Gabarito e Painel (modelos em correcao/modelos/).
 *  3. Extensões > Apps Script > cole este arquivo.
 *  4. Acionadores > Adicionar acionador > função aoEnviar > "Da planilha" > "Ao enviar o formulário".
 *  5. Teste com envios falsos antes de usar com alunos.
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

function minutos(ini, fim) {
  const p = t => String(t).split(':').map(Number);
  const [h1, m1] = p(ini), [h2, m2] = p(fim);
  let d = (h2 * 60 + m2) - (h1 * 60 + m1);
  return d < 0 ? d + 24 * 60 : d;
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
    const resp = normalizar((r[campo] || [''])[0]);
    const ok = String(aceitas).split('|').map(normalizar).includes(resp);
    if (ok) feitos += pontos; else errados.push(campo);
  });

  const nota = total ? Math.round(100 * feitos / total) : 0;
  const limite = Number(gab[0][4]) || 0;
  const dentroDoTempo = !TEMPO_CONTA || !limite || tempo <= limite;
  const status = (nota >= CORTE_NOTA && dentroDoTempo) ? 'Domínio' : 'Repetir';

  painel.appendRow([new Date(), aluno, bloco.split(' ')[0], bloco, nota, tempo, limite,
                    status, errados.join(', '), fotos]);
}
