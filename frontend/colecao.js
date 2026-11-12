const conteudo = document.querySelector('#conteudo');
const aviso = document.querySelector('#aviso');
const menu = document.querySelector('nav');
const mecanismos = { quartzo: 'Quartzo', automatico: 'Automático', manual: 'Manual' };
let mensagemSeguinte = '';
let versaoTela = 0;

async function api(caminho, metodo = 'GET', dados) {
  const opcoes = { method: metodo };
  if (dados !== undefined) {
    opcoes.headers = { 'Content-Type': 'application/json' };
    opcoes.body = JSON.stringify(dados);
  }
  const resposta = await fetch(caminho, opcoes);
  if (!resposta.ok) {
    const dadosErro = await resposta.json().catch(() => ({}));
    throw new Error(dadosErro.erro || 'Não foi possível concluir a operação.');
  }
  if (resposta.status !== 204) return resposta.json();
}

function mostrar(id) {
  conteudo.replaceChildren(document.querySelector('#' + id).content.cloneNode(true));
}

function navegar(destino, mensagem) {
  mensagemSeguinte = mensagem;
  if (location.hash === destino) abrirTela();
  else location.hash = destino;
}

function preencherRelogios(lista, relogios, marcas) {
  if (!relogios.length) {
    const vazio = document.createElement('li');
    vazio.textContent = 'Nenhum relógio cadastrado.';
    lista.append(vazio);
  }
  for (const relogio of relogios) {
    const item = document.createElement('li');
    const link = document.createElement('a');
    link.href = '#relogio/' + relogio.id_relogio;
    const foto = document.createElement('span');
    foto.className = 'foto';
    foto.textContent = 'Sem foto';
    const marca = document.createElement('small');
    marca.textContent = marcas.find(item => item.id_marca === relogio.id_marca)?.nome ?? '';
    const nome = document.createElement('strong');
    nome.textContent = relogio.modelo;
    link.append(foto, marca, nome);
    item.append(link);
    lista.append(item);
  }
}

function mostrarEntrada(cadastro) {
  mostrar('entrada');
  const titulo = cadastro ? 'Criar conta' : 'Entrar';
  conteudo.querySelector('h1').textContent = titulo;
  conteudo.querySelector('button').textContent = titulo;
  conteudo.querySelector('.nome-conta').hidden = !cadastro;
  const link = conteudo.querySelector('.trocar-conta');
  link.textContent = cadastro ? 'Já tem conta? Entrar' : 'Ainda não tem conta? Criar conta';
  link.href = cadastro ? '#entrar' : '#criar-conta';
}

function mostrarDetalhe(relogio, marcas) {
  mostrar('detalhe');
  const marca = marcas.find(item => item.id_marca === relogio.id_marca);
  conteudo.querySelector('h1').textContent = [marca?.nome, relogio.modelo].filter(Boolean).join(' ');
  const lista = conteudo.querySelector('dl');
  const preco = relogio.preco_aquisicao == null ? null :
    Number(relogio.preco_aquisicao).toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
  const data = relogio.data_aquisicao?.split('-').reverse().join('/');
  for (const [nome, valor] of [
    ['Referência', relogio.referencia], ['Mecanismo', mecanismos[relogio.mecanismo]],
    ['Mostrador', relogio.cor_mostrador], ['Aquisição', data],
    ['Preço', preco], ['Observações', relogio.observacoes],
  ]) {
    if (!valor) continue;
    const termo = document.createElement('dt');
    termo.textContent = nome;
    const descricao = document.createElement('dd');
    descricao.textContent = valor;
    lista.append(termo, descricao);
  }
  const id = relogio.id_relogio;
  conteudo.querySelector('.editar').href = '#editar/' + id;
  const excluir = conteudo.querySelector('.excluir');
  excluir.onclick = async () => {
    if (!window.confirm('Excluir este relógio da coleção?')) return;
    excluir.disabled = true;
    try {
      await api('/relogios/' + id, 'DELETE');
      navegar('#colecao', 'Relógio excluído.');
    } catch (erro) {
      aviso.textContent = erro.message;
      excluir.disabled = false;
    }
  };
}

function mostrarFormulario(relogio, marcas, pastas, vinculos) {
  mostrar('form-relogio');
  const id = relogio?.id_relogio;
  const destino = id ? '#relogio/' + id : '#colecao';
  conteudo.querySelector('h1').textContent = id ? 'Editar relógio' : 'Novo relógio';
  const voltar = conteudo.querySelector('.voltar');
  voltar.href = destino;
  if (id) voltar.textContent = '‹ Detalhes do relógio';
  conteudo.querySelector('.cancelar').href = destino;
  const form = conteudo.querySelector('form');
  const seletor = form.elements.id_marca;
  seletor.add(new Option('Selecionar marca', ''));
  for (const marca of marcas) seletor.add(new Option(marca.nome, marca.id_marca));
  seletor.add(new Option('Outra marca', 'nova'));
  const campoNovaMarca = form.querySelector('.nova-marca');
  seletor.onchange = () => {
    campoNovaMarca.hidden = seletor.value !== 'nova';
    form.elements.nova_marca.required = !campoNovaMarca.hidden;
  };

  for (const campo of ['id_marca', 'modelo', 'referencia', 'mecanismo', 'cor_mostrador',
    'data_aquisicao', 'preco_aquisicao', 'observacoes']) {
    form.elements[campo].value = relogio?.[campo] ?? '';
  }
  const opcoes = form.querySelector('.opcoes-pastas');
  if (!pastas.length) {
    const link = document.createElement('a');
    link.href = '#pastas';
    link.textContent = 'Criar uma pasta';
    opcoes.append(link);
  }
  for (const pasta of pastas) {
    const rotulo = document.createElement('label');
    const caixa = document.createElement('input');
    caixa.type = 'checkbox';
    caixa.name = 'pasta';
    caixa.value = pasta.id_pasta;
    caixa.checked = vinculos.includes(pasta.id_pasta);
    rotulo.append(caixa, ' ' + pasta.nome);
    opcoes.append(rotulo);
  }

  form.onsubmit = async evento => {
    evento.preventDefault();
    const botao = form.querySelector('button[type=submit], .acoes button');
    botao.disabled = true;
    aviso.textContent = 'Salvando…';
    const campos = new FormData(form);
    const escolhidas = campos.getAll('pasta').map(Number);
    let idSalvo;
    try {
      if (campos.get('id_marca') === 'nova') {
        const marca = await api('/marcas', 'POST', { nome: campos.get('nova_marca') });
        seletor.add(new Option(marca.nome, marca.id_marca), seletor.options.length - 1);
        seletor.value = marca.id_marca;
        seletor.onchange();
        campos.set('id_marca', marca.id_marca);
      }
      const dados = Object.fromEntries(campos);
      dados.id_marca = Number(dados.id_marca);
      delete dados.pasta;
      delete dados.nova_marca;
      const salvo = await api(id ? '/relogios/' + id : '/relogios', id ? 'PUT' : 'POST', dados);
      idSalvo = id ?? salvo.id_relogio;
      for (const pasta of pastas) {
        const anterior = vinculos.includes(pasta.id_pasta);
        const atual = escolhidas.includes(pasta.id_pasta);
        if (anterior !== atual) {
          await api('/pastas/' + pasta.id_pasta + '/relogios/' + idSalvo, atual ? 'POST' : 'DELETE');
        }
      }
      navegar('#relogio/' + idSalvo, 'Relógio salvo.');
    } catch (erro) {
      if (idSalvo) {
        navegar('#editar/' + idSalvo, 'Relógio salvo. Confira as pastas. ' + erro.message);
      } else {
        aviso.textContent = erro.message;
        botao.disabled = false;
      }
    }
  };
}

function mostrarPastas(pastas) {
  mostrar('lista-pastas');
  const lista = conteudo.querySelector('ul');
  if (!pastas.length) {
    const vazio = document.createElement('li');
    vazio.textContent = 'Nenhuma pasta criada.';
    lista.append(vazio);
  }
  for (const pasta of pastas) {
    const item = document.createElement('li');
    const nome = document.createElement('strong');
    nome.textContent = pasta.nome;
    const link = document.createElement('a');
    link.href = '#pasta/' + pasta.id_pasta;
    link.className = 'botao';
    link.textContent = 'Abrir';
    link.setAttribute('aria-label', 'Abrir ' + pasta.nome);
    item.append(nome, link);
    lista.append(item);
  }
  const form = conteudo.querySelector('form');
  form.onsubmit = async evento => {
    evento.preventDefault();
    const botao = form.querySelector('button');
    botao.disabled = true;
    try {
      await api('/pastas', 'POST', { nome: form.elements.nome.value });
      navegar('#pastas', 'Pasta criada.');
    } catch (erro) {
      aviso.textContent = erro.message;
      botao.disabled = false;
    }
  };
}

async function abrirTela() {
  const versao = ++versaoTela;
  const [pagina, id] = (location.hash.slice(1) || 'entrar').split('/');
  const entrada = pagina === 'entrar' || pagina === 'criar-conta';
  menu.hidden = entrada;
  const secao = pagina === 'pastas' || pagina === 'pasta' ? '#pastas' : '#colecao';
  for (const link of menu.querySelectorAll('a')) {
    if (link.hash === secao) link.setAttribute('aria-current', 'page');
    else link.removeAttribute('aria-current');
  }
  const mensagem = mensagemSeguinte;
  mensagemSeguinte = '';
  aviso.textContent = '';
  conteudo.replaceChildren();
  if (entrada) {
    mostrarEntrada(pagina === 'criar-conta');
    return;
  }
  aviso.textContent = 'Carregando…';
  try {
    if (pagina === 'colecao') {
      const [relogios, marcas] = await Promise.all([api('/relogios'), api('/marcas')]);
      if (versao !== versaoTela) return;
      mostrar('lista');
      preencherRelogios(conteudo.querySelector('ul'), relogios, marcas);
    } else if (pagina === 'relogio' && /^\d+$/.test(id)) {
      const [relogio, marcas] = await Promise.all([api('/relogios/' + id), api('/marcas')]);
      if (versao !== versaoTela) return;
      mostrarDetalhe(relogio, marcas);
    } else if (pagina === 'novo' || (pagina === 'editar' && /^\d+$/.test(id))) {
      const [marcas, pastas, relogio] = await Promise.all([
        api('/marcas'), api('/pastas'), id ? api('/relogios/' + id) : null,
      ]);
      const detalhes = relogio ? await Promise.all(pastas.map(pasta => api('/pastas/' + pasta.id_pasta))) : [];
      if (versao !== versaoTela) return;
      const vinculos = detalhes.filter(pasta => pasta.relogios.some(item => item.id_relogio === relogio.id_relogio))
        .map(pasta => pasta.id_pasta);
      mostrarFormulario(relogio, marcas, pastas, vinculos);
    } else if (pagina === 'pastas') {
      const pastas = await api('/pastas');
      if (versao !== versaoTela) return;
      mostrarPastas(pastas);
    } else if (pagina === 'pasta' && /^\d+$/.test(id)) {
      const [pasta, marcas] = await Promise.all([api('/pastas/' + id), api('/marcas')]);
      if (versao !== versaoTela) return;
      mostrar('detalhe-pasta');
      conteudo.querySelector('h1').textContent = pasta.nome;
      preencherRelogios(conteudo.querySelector('ul'), pasta.relogios, marcas);
    } else {
      throw new Error('Tela não encontrada.');
    }
    aviso.textContent = mensagem;
  } catch (erro) {
    if (versao === versaoTela) aviso.textContent = erro.message;
  }
}

window.addEventListener('hashchange', abrirTela);
abrirTela();
