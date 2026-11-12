import os
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from flask import Flask, abort, g, jsonify, request, send_from_directory
from pymysql import MySQLError
from pymysql.err import IntegrityError

from conexao import conectar
from dao import FotoDAO, MarcaDAO, PastaDAO, RelogioDAO, UsuarioDAO
from models import Marca, Pasta, Relogio

app = Flask(__name__, static_folder=Path(__file__).resolve().parent.parent / "frontend",
            static_url_path="")
EMAIL_DEMONSTRACAO = 'demonstracao@example.invalid'


@app.before_request
def verificar_demonstracao():
    if request.remote_addr not in ('127.0.0.1', '::1'):
        abort(403)
    if request.endpoint in ('inicio', 'static'):
        return
    identificador = os.getenv('COLECAO_USUARIO_TESTE', '')
    if not identificador.isascii() or not identificador.isdecimal() or len(identificador) > 10:
        abort(503, description='Configure COLECAO_USUARIO_TESTE para testar a API local.')
    g.conexao = conectar(os.getenv('MYSQL_PASSWORD', ''))
    usuario = UsuarioDAO(g.conexao).buscar(int(identificador))
    if usuario is None or usuario.email != EMAIL_DEMONSTRACAO:
        abort(503, description='Configure o usuário fictício da demonstração.')
    g.id_usuario = usuario.id_usuario


@app.teardown_request
def fechar_conexao(erro):
    conexao = g.pop('conexao', None)
    if conexao is not None:
        conexao.close()


@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(503)
def erro_http(erro):
    return jsonify(erro=erro.description), erro.code


@app.errorhandler(ValueError)
def erro_validacao(erro):
    return jsonify(erro=str(erro)), 400


@app.errorhandler(IntegrityError)
def erro_integridade(erro):
    if erro.args[0] == 1062:
        return jsonify(erro='Esse registro já existe.'), 409
    if erro.args[0] == 1452:
        return jsonify(erro='O registro relacionado não existe.'), 400
    return erro_banco(erro)


@app.errorhandler(MySQLError)
def erro_banco(erro):
    return jsonify(erro='Não foi possível acessar o banco de dados.'), 503


def dados_json():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise ValueError('Envie um objeto JSON.')
    return dados


def texto(dados, campo, limite, opcional=False):
    valor = dados.get(campo)
    if opcional and valor is None:
        return None
    if not isinstance(valor, str):
        raise ValueError(f'Informe {campo}.')
    valor = valor.strip()
    if opcional and not valor:
        return None
    tamanho = len(valor.encode('utf-8')) if campo == 'observacoes' else len(valor)
    if not valor or tamanho > limite:
        raise ValueError(f'Confira o tamanho do campo {campo}.')
    return valor


def ler_relogio(id_relogio=None):
    dados = dados_json()
    id_marca = dados.get('id_marca')
    if type(id_marca) is not int or not 0 < id_marca <= 2147483647:
        raise ValueError('Selecione uma marca válida.')
    mecanismo = texto(dados, 'mecanismo', 15)
    if mecanismo not in ('quartzo', 'automatico', 'manual'):
        raise ValueError('Selecione quartzo, automatico ou manual.')

    data = texto(dados, 'data_aquisicao', 10, opcional=True)
    if data:
        try:
            data_convertida = date.fromisoformat(data)
        except ValueError:
            raise ValueError('Use uma data válida no formato AAAA-MM-DD.') from None
        if data_convertida.isoformat() != data or data_convertida.year < 1000:
            raise ValueError('Use uma data válida no formato AAAA-MM-DD.')
        data = data_convertida

    preco = dados.get('preco_aquisicao')
    if preco not in (None, ''):
        try:
            preco = Decimal(str(preco))
            if (not preco.is_finite() or not 0 <= preco <= Decimal('9999999999.99')
                    or preco != preco.quantize(Decimal('0.01'))):
                raise InvalidOperation
            preco = preco.quantize(Decimal('0.01'))
        except InvalidOperation:
            raise ValueError('Informe um preço válido com até duas casas decimais.') from None
    else:
        preco = None

    return Relogio.from_dict({
        'id_relogio': id_relogio,
        'id_usuario': g.id_usuario,
        'id_marca': id_marca,
        'modelo': texto(dados, 'modelo', 120),
        'referencia': texto(dados, 'referencia', 100),
        'mecanismo': mecanismo,
        'cor_mostrador': texto(dados, 'cor_mostrador', 60),
        'data_aquisicao': data,
        'preco_aquisicao': preco,
        'observacoes': texto(dados, 'observacoes', 65535, opcional=True),
    })


@app.route('/')
def inicio():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/marcas', methods=['GET'])
def listar_marcas():
    return jsonify([marca.to_dict() for marca in MarcaDAO(g.conexao).listar()])


@app.route('/marcas', methods=['POST'])
def criar_marca():
    marca = Marca(texto(dados_json(), 'nome', 100))
    MarcaDAO(g.conexao).inserir(marca)
    return jsonify(marca.to_dict()), 201


@app.route('/relogios', methods=['GET'])
def listar_relogios():
    relogios = RelogioDAO(g.conexao).listar(g.id_usuario)
    return jsonify([relogio.to_dict() for relogio in relogios])


@app.route('/relogios', methods=['POST'])
def criar_relogio():
    relogio = ler_relogio()
    RelogioDAO(g.conexao).inserir(relogio)
    return jsonify(relogio.to_dict()), 201


@app.route('/relogios/<int:id_relogio>', methods=['GET'])
def consultar_relogio(id_relogio):
    relogio = RelogioDAO(g.conexao).buscar(g.id_usuario, id_relogio)
    if relogio is None:
        abort(404, description='Relógio não encontrado.')
    dados = relogio.to_dict()
    dados['fotos'] = [foto.to_dict() for foto in FotoDAO(g.conexao).listar(g.id_usuario, id_relogio)]
    return jsonify(dados)


@app.route('/relogios/<int:id_relogio>', methods=['PUT'])
def atualizar_relogio(id_relogio):
    if not RelogioDAO(g.conexao).atualizar(ler_relogio(id_relogio)):
        abort(404, description='Relógio não encontrado.')
    return '', 204


@app.route('/relogios/<int:id_relogio>', methods=['DELETE'])
def excluir_relogio(id_relogio):
    if not RelogioDAO(g.conexao).excluir(g.id_usuario, id_relogio):
        abort(404, description='Relógio não encontrado.')
    return '', 204


@app.route('/pastas', methods=['GET'])
def listar_pastas():
    pastas = PastaDAO(g.conexao).listar(g.id_usuario)
    return jsonify([pasta.to_dict() for pasta in pastas])


@app.route('/pastas', methods=['POST'])
def criar_pasta():
    pasta = Pasta(g.id_usuario, texto(dados_json(), 'nome', 100))
    PastaDAO(g.conexao).inserir(pasta)
    return jsonify(pasta.to_dict()), 201


@app.route('/pastas/<int:id_pasta>', methods=['GET'])
def consultar_pasta(id_pasta):
    dao = PastaDAO(g.conexao)
    pasta = dao.buscar(g.id_usuario, id_pasta)
    if pasta is None:
        abort(404, description='Pasta não encontrada.')
    dados = pasta.to_dict()
    dados['relogios'] = [relogio.to_dict() for relogio in dao.listar_relogios(g.id_usuario, id_pasta)]
    return jsonify(dados)


@app.route('/pastas/<int:id_pasta>/relogios/<int:id_relogio>', methods=['POST'])
def vincular_relogio(id_pasta, id_relogio):
    if not PastaDAO(g.conexao).vincular(g.id_usuario, id_pasta, id_relogio):
        abort(404, description='Pasta ou relógio não encontrado.')
    return jsonify(id_pasta=id_pasta, id_relogio=id_relogio), 201


@app.route('/pastas/<int:id_pasta>/relogios/<int:id_relogio>', methods=['DELETE'])
def desvincular_relogio(id_pasta, id_relogio):
    if not PastaDAO(g.conexao).desvincular(g.id_usuario, id_pasta, id_relogio):
        abort(404, description='Vínculo não encontrado.')
    return '', 204


if __name__ == '__main__':
    app.run(host='127.0.0.1', threaded=False)
