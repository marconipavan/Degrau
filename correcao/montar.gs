/**
 * Degrau — montagem do formulário, das abas e do gatilho (rodar uma vez, na planilha do CASD).
 *
 * Extensões > Apps Script > cole este arquivo e o aoEnviar.gs > escolha montar > Executar.
 * Cria: abas Alunos e Painel (se faltarem); o formulário ligado a esta planilha;
 * o gatilho que chama aoEnviar a cada envio. O campo de foto precisa ser criado à mão
 * (o Apps Script não cria envio de arquivo): ver correcao/README.md.
 */
const PAGINAS = ['1ª folha (a)', '1ª folha (b)', '2ª folha (a)', '2ª folha (b)', '3ª folha (a)', '3ª folha (b)'];
const CAMPOS_POR_PAGINA = 12;   // igual a MAX_ITENS_PAGINA em motor/gabarito.py

function montar() {
  const ss = SpreadsheetApp.getActive();
  const cabecalhos = {
    Alunos: ['Aluno', 'E-mail', 'Nível atual', 'Próximo bloco', 'Entrada (nivelamento)'],
    Painel: ['Data', 'Aluno', 'Nível', 'Bloco', 'Nota (%)', 'Tempo (min)', 'Limite (min)', 'Status', 'Itens errados', 'Fotos'],
  };
  for (const [nome, cab] of Object.entries(cabecalhos)) {
    if (!ss.getSheetByName(nome)) ss.insertSheet(nome).appendRow(cab);
  }

  const alunos = ss.getSheetByName('Alunos').getDataRange().getValues().slice(1)
    .map(l => String(l[0]).trim()).filter(a => a);
  if (alunos.length === 0) throw new Error('Preencha a aba Alunos (coluna A) antes de montar o formulário.');

  const form = FormApp.create('Degrau — entrega do bloco diário');
  form.setDescription('Uma resposta por campo, com o número do item da folha. Deixe em branco os campos que a folha não tem.');
  form.addListItem().setTitle('Aluno').setChoiceValues(alunos).setRequired(true);
  form.addTextItem().setTitle('Código do bloco').setHelpText('Copie da folha. Exemplo: G1 10-12 (ou G1 10-12 v2)').setRequired(true)
    .setValidation(FormApp.createTextValidation().requireTextMatchesPattern('^ *[Gg]\\d+ +\\d+(-\\d+)?( +[Vv]\\d+)? *$')
      .setHelpText('Use o formato da folha: G1 10-12 ou G1 10-12 v2').build());
  form.addTimeItem().setTitle('Início').setRequired(true);
  form.addTimeItem().setTitle('Fim').setRequired(true);
  for (const pagina of PAGINAS) {
    form.addPageBreakItem().setTitle(pagina);
    for (let n = 1; n <= CAMPOS_POR_PAGINA; n++) form.addTextItem().setTitle(`${pagina} · ${n}`);
  }
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  ScriptApp.newTrigger('aoEnviar').forSpreadsheet(ss).onFormSubmit().create();
  return form.getPublishedUrl();
}
