// Testa o aoEnviar.gs com envios falsos, sem Google: planilha e formulário simulados.
// uso: node correcao/teste/simular.js        (sai com código 1 se algum caso falhar)
// O gabarito vem de correcao/gabarito.gs (a biblioteca de geometria inteira, por folha e versão), gerado do YAML
// por ./degrau atualizar-gabarito.
const fs = require('fs'), path = require('path'), vm = require('vm'), assert = require('assert');

const DIR = path.join(__dirname, '..');

function lerCsv(texto) {           // CSV simples com aspas
  const linhas = []; let campo = '', linha = [], aspas = false;
  for (let i = 0; i < texto.length; i++) {
    const c = texto[i];
    if (aspas) {
      if (c === '"' && texto[i + 1] === '"') { campo += '"'; i++; }
      else if (c === '"') aspas = false;
      else campo += c;
    } else if (c === '"') aspas = true;
    else if (c === ',') { linha.push(campo); campo = ''; }
    else if (c === '\n') { linha.push(campo); linhas.push(linha); linha = []; campo = ''; }
    else if (c !== '\r') campo += c;
  }
  if (campo || linha.length) { linha.push(campo); linhas.push(linha); }
  // como o Sheets: células numéricas viram número
  return linhas.map(l => l.map(v => (v !== '' && !isNaN(v) ? Number(v) : v)));
}

function novaPlanilha() {
  const abas = {
    Painel: [lerCsv(fs.readFileSync(path.join(DIR, 'modelos', 'painel.csv'), 'utf8'))[0]],
  };
  const aba = nome => ({
    getDataRange: () => ({ getValues: () => abas[nome].map(l => l.slice()) }),
    appendRow: l => abas[nome].push(l),
  });
  return { abas, SpreadsheetApp: { getActive: () => ({ getSheetByName: aba }) } };
}

function carregar() {
  const p = novaPlanilha();
  const ctx = { SpreadsheetApp: p.SpreadsheetApp, Date, String, Number, Math };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(DIR, 'gabarito.gs'), 'utf8') + '\nthis.GABARITO = GABARITO;', ctx);
  vm.runInContext(fs.readFileSync(path.join(DIR, 'aoEnviar.gs'), 'utf8') + '\nthis.aoEnviar = aoEnviar;', ctx);
  return { aoEnviar: ctx.aoEnviar, painel: p.abas.Painel, gabarito: ctx.GABARITO };
}

// envio do formulário: e.namedValues = {título da pergunta: [resposta]}
function envio(bloco, ini, fim, respostas) {
  const nv = { 'Aluno': ['Aluno Teste'], 'Código do bloco': [bloco], 'Início': [ini], 'Fim': [fim],
               'Foto da resolução': ['https://exemplo/foto'] };
  for (const [campo, v] of Object.entries(respostas)) nv[campo] = [v];
  return { namedValues: nv };
}

// primeira resposta aceita de cada campo do bloco (folhas na ordem do bloco, versão 1)
function corretas(gab, folhas = ['G1 1', 'G1 2', 'G1 3']) {
  const r = {};
  folhas.forEach((folha, k) => {
    for (const [f, v, pagina, item, aceitas] of gab)
      if (f === folha && v === 1) r[`${k + 1}ª folha (${pagina}) · ${item}`] = String(aceitas).split('|')[0].replace(/^conjunto:/, '');
  });
  return r;
}

const casos = [];
function caso(nome, f) { casos.push([nome, f]); }

caso('tudo certo, no tempo: nota 100, Domínio', () => {
  const s = carregar();
  s.aoEnviar(envio('G1 1-3', '19:02:00', '19:13:00', corretas(s.gabarito)));
  const l = s.painel[1];
  assert.deepStrictEqual([l[1], l[2], l[3], l[4], l[5], l[6], l[7], l[8]],
                         ['Aluno Teste', 'G1', 'G1 1-3', 100, 11, 12, 'Domínio', '']);
});

caso('variações de escrita aceitas (minúsculas, sem acento, ordem inversa, ° e espaços)', () => {
  const s = carregar(); const r = corretas(s.gabarito);
  r['1ª folha (a) · 1'] = 'rqp';
  r['1ª folha (b) · 4'] = ' ra ';
  r['3ª folha (b) · 2'] = 'lkj obtuso';
  r['2ª folha (b) · 1'] = 'PÔS, QÔS, POR, rôs, qôr, PÔQ';   // conjunto em outra ordem
  r['2ª folha (b) · 2'] = '10';
  s.aoEnviar(envio(' g1   1-3 ', '19:02', '19:10', r));
  assert.strictEqual(s.painel[1][4], 100, 'itens errados: ' + s.painel[1][8]);
});

caso('minutos e segundos com aspas do celular (’ ′ ” e duas aspas simples)', () => {
  const ctx = { String }; vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(DIR, 'aoEnviar.gs'), 'utf8').replace(/^const SS = .*$/m, '') + '\nthis.confere = confere;', ctx);
  for (const r of ['35°20’15”', "35°20′15″", "35°20'15''", ' 35° 20\' 15" '])
    assert.ok(ctx.confere(r, '35°20\'15"'), r);
  assert.ok(!ctx.confere("35°15'20\"", '35°20\'15"'));
});

caso('conjunto com ângulo escrito ao contrário (QÔP = PÔQ)', () => {
  const s = carregar(); const r = corretas(s.gabarito);
  r['2ª folha (b) · 1'] = 'QÔP; RÔQ; SÔR; RÔP; SÔQ; SÔP';
  s.aoEnviar(envio('G1 1-3', '19:02', '19:10', r));
  assert.strictEqual(s.painel[1][4], 100, 'itens errados: ' + s.painel[1][8]);
});

caso('conjunto incompleto conta como erro', () => {
  const s = carregar(); const r = corretas(s.gabarito);
  r['2ª folha (b) · 1'] = 'PÔQ, QÔR, RÔS';
  s.aoEnviar(envio('G1 1-3', '19:02', '19:10', r));
  assert.strictEqual(s.painel[1][8], '2ª folha (b) · 1');
});

caso('erros: nota pelos pontos e lista dos campos errados; 90% ainda é Domínio', () => {
  const s = carregar(); const r = corretas(s.gabarito);
  r['1ª folha (a) · 2'] = 'MNT';      // 20 pontos
  r['3ª folha (a) · 7'] = 'O';        // 10 pontos
  delete r['3ª folha (b) · 5'];       // 20 pontos, em branco
  s.aoEnviar(envio('G1 1-3', '19:02', '19:10', r));
  const total = s.gabarito.filter(l => ['G1 1', 'G1 2', 'G1 3'].includes(l[0])).reduce((a, l) => a + l[5], 0);   // 490
  const l = s.painel[1];
  assert.strictEqual(l[4], Math.round(100 * (total - 50) / total));   // 90
  assert.strictEqual(l[7], 'Domínio');
  assert.strictEqual(l[8], '1ª folha (a) · 2, 3ª folha (a) · 7, 3ª folha (b) · 5');
});

caso('abaixo de 90%: Repetir', () => {
  const s = carregar(); const r = corretas(s.gabarito);
  r['1ª folha (a) · 2'] = 'MNT'; r['1ª folha (a) · 3'] = 'CDE'; r['3ª folha (b) · 5'] = 'N';   // 60 pontos
  s.aoEnviar(envio('G1 1-3', '19:02', '19:10', r));
  assert.deepStrictEqual([s.painel[1][4], s.painel[1][7]], [88, 'Repetir']);
});

caso('tudo certo mas acima do tempo: Repetir', () => {
  const s = carregar();
  s.aoEnviar(envio('G1 1-3', '19:02', '19:20', corretas(s.gabarito)));
  assert.deepStrictEqual([s.painel[1][4], s.painel[1][5], s.painel[1][7]], [100, 18, 'Repetir']);
});

caso('horário em formato de 12 horas e passando da meia-noite', () => {
  const s = carregar();
  s.aoEnviar(envio('G1 1-3', '12:50:00 AM', '1:10:00 AM', corretas(s.gabarito)));   // 00:50 a 01:10
  assert.strictEqual(s.painel[1][5], 20);
  const s2 = carregar();
  s2.aoEnviar(envio('G1 1-3', '11:55 PM', '12:05 AM', corretas(s2.gabarito)));
  assert.strictEqual(s2.painel[1][5], 10);
});

caso('bloco sem gabarito: linha de erro no Painel', () => {
  const s = carregar();
  s.aoEnviar(envio('G1 101-103', '19:02', '19:10', {}));     // folhas que não existem
  assert.strictEqual(s.painel[1][7], 'ERRO: sem gabarito: G1 101, G1 102, G1 103');
  s.aoEnviar(envio('G1 1-3 v2', '19:02', '19:10', {}));            // repetição sem a versão 2 carregada
  assert.strictEqual(s.painel[2][7], 'ERRO: sem gabarito: G1 1, G1 2, G1 3 v2');
  s.aoEnviar(envio('G1 1-9', '19:02', '19:10', {}));               // mais folhas do que o formulário comporta
  assert.strictEqual(s.painel[3][7], 'ERRO: código do bloco inválido');
});

caso('bloco de uma folha só e folha fora do início da biblioteca (G1 89)', () => {
  const s = carregar();
  s.aoEnviar(envio('G1 89', '19:02', '19:05', corretas(s.gabarito, ['G1 89'])));
  assert.deepStrictEqual([s.painel[1][3], s.painel[1][4], s.painel[1][6], s.painel[1][7]], ['G1 89', 100, 4, 'Domínio']);
});

caso('montar.gs cria um campo para cada linha do gabarito, com o mesmo título', () => {
  const titulos = [], abas = {};
  const item = () => { const o = { setTitle: x => (titulos.push(x), o), setChoiceValues: () => o, setRequired: () => o,
                                   setHelpText: () => o, setValidation: () => o }; return o; };
  const validacao = { requireTextMatchesPattern: () => validacao, setHelpText: () => validacao, build: () => ({}) };
  const form = { setDescription() {}, addListItem: item, addTextItem: item, addTimeItem: item, addPageBreakItem: item,
                 setDestination() {}, getPublishedUrl: () => 'url' };
  const ss = { getId: () => 'id', getSheetByName: n => abas[n],
               insertSheet: n => (abas[n] = { rows: [], appendRow(l) { this.rows.push(l); },
                                              getDataRange() { return { getValues: () => this.rows }; } }) };
  const ctx = { SpreadsheetApp: { getActive: () => ss }, FormApp: { create: () => form, createTextValidation: () => validacao,
                DestinationType: { SPREADSHEET: 1 } },
                ScriptApp: { newTrigger: () => ({ forSpreadsheet: () => ({ onFormSubmit: () => ({ create() {} }) }) }) },
                Error, Object, String };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(DIR, 'montar.gs'), 'utf8') + '\nthis.montar = montar;', ctx);
  assert.throws(() => ctx.montar(), /Preencha a aba Alunos/);
  abas.Alunos.appendRow(['Aluno Teste']);
  titulos.length = 0;
  ctx.montar();
  const campos = [1, 2, 3].flatMap(k => carregar().gabarito.map(l => `${k}ª folha (${l[2]}) · ${l[3]}`));
  const faltam = campos.filter(c => !titulos.includes(c));
  assert.deepStrictEqual(faltam, []);
  // o regex do formulário aceita o que o script normaliza
  const re = /^ *[Gg]\d+ +\d+(-\d+)?( +[Vv]\d+)? *$/;
  for (const c of [' g1  10-12 ', 'G1 100', 'G1 10-12 v2']) assert.ok(re.test(c), c);
});

let falhas = 0;
for (const [nome, f] of casos) {
  try { f(); console.log('ok     ' + nome); }
  catch (e) { falhas++; console.log('FALHOU ' + nome + '\n       ' + e.message.split('\n').join('\n       ')); }
}
console.log(`${casos.length - falhas}/${casos.length} casos passaram`);
process.exit(falhas ? 1 : 0);
