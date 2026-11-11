# Etapa 2 — API Flask

Os modelos ficam em `backend/models.py`, as consultas e gravações em
`backend/dao.py` e as rotas em `backend/app.py`.

## Rodar localmente

Use um banco MySQL de teste inicializado com `database/banco.sql`. No cliente MySQL,
crie o usuário fictício abaixo uma vez e anote o ID retornado. `SEM_LOGIN` é um
marcador da demonstração.

```sql
USE colecao_relogios;
INSERT INTO usuario (nome, email, senha_hash)
VALUES ('Demonstração', 'demonstracao@example.invalid', 'SEM_LOGIN');
SELECT id_usuario FROM usuario WHERE email = 'demonstracao@example.invalid';
```

No PowerShell, a partir da raiz do projeto, substitua `1` pelo ID retornado.
Se o MySQL exigir senha, configure `MYSQL_PASSWORD` no ambiente antes de iniciar.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend/requirements.txt
$env:COLECAO_USUARIO_TESTE = '1'
.\.venv\Scripts\python.exe backend/app.py
```

A API roda em `http://127.0.0.1:5000` para testar o cadastro e as consultas
com o usuário fictício. Login e envio de imagens ficam pendentes.

## Rotas

| Método | Caminho | Operação |
| --- | --- | --- |
| GET / POST | `/marcas` | Listar ou cadastrar marcas |
| GET / POST | `/relogios` | Listar ou cadastrar relógios |
| GET / PUT / DELETE | `/relogios/<id>` | Consultar, editar ou excluir um relógio |
| GET / POST | `/pastas` | Listar ou criar pastas |
| GET | `/pastas/<id>` | Consultar uma pasta e seus relógios |
| POST / DELETE | `/pastas/<id>/relogios/<id>` | Adicionar ou retirar um relógio da pasta |

## Testar um cadastro

Use o ID de uma marca retornada por `GET /marcas`.

```powershell
$base = 'http://127.0.0.1:5000'
Invoke-RestMethod "$base/marcas"
$relogio = @{
    id_marca = 1
    modelo = 'F-91W'
    referencia = 'F-91W-1'
    mecanismo = 'quartzo'
    cor_mostrador = 'Preto'
} | ConvertTo-Json
Invoke-RestMethod "$base/relogios" -Method Post -ContentType 'application/json' -Body $relogio
Invoke-RestMethod "$base/relogios"
```
