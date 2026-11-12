# Etapa 3 — Interface web

A interface segue o wireframe e usa HTML, CSS e JavaScript. O navegador envia as
requisições com Fetch para o Flask, que lê e grava no MySQL.

## Rodar localmente

1. Prepare o MySQL, o usuário fictício e as dependências conforme o
   [guia da Etapa 2](ETAPA2.md).
2. Execute `backend/app.py` com a configuração de demonstração.
3. Abra <http://127.0.0.1:5000> e selecione **Abrir coleção de demonstração**.

Na tela **Pastas**, crie uma pasta. Em **Minha coleção**, escolha **Novo relógio**,
selecione uma marca ou cadastre outra e marque a pasta. Salve e abra o relógio
pela coleção ou pela pasta. Use **Editar** para alterar os dados ou os vínculos
e **Excluir** para remover o relógio.

As telas **Entrar** e **Criar conta** fazem parte do wireframe. O acesso de teste
usa o usuário fictício configurado no Flask. A autenticação e o envio de fotos
estão pendentes.
