from datetime import date
from decimal import Decimal


class Usuario:
    def __init__(self, nome, email, id_usuario=None):
        self.id_usuario = id_usuario
        self.nome = nome
        self.email = email

    def to_dict(self):
        return vars(self).copy()

    @staticmethod
    def from_dict(dados):
        return Usuario(dados['nome'], dados['email'], dados.get('id_usuario'))


class Marca:
    def __init__(self, nome, id_marca=None):
        self.id_marca = id_marca
        self.nome = nome

    def to_dict(self):
        return vars(self).copy()

    @staticmethod
    def from_dict(dados):
        return Marca(dados['nome'], dados.get('id_marca'))


class Relogio:
    def __init__(self, id_usuario, id_marca, modelo, referencia, mecanismo,
                 cor_mostrador, data_aquisicao=None, preco_aquisicao=None,
                 observacoes=None, id_relogio=None):
        self.id_relogio = id_relogio
        self.id_usuario = id_usuario
        self.id_marca = id_marca
        self.modelo = modelo
        self.referencia = referencia
        self.mecanismo = mecanismo
        self.cor_mostrador = cor_mostrador
        self.data_aquisicao = data_aquisicao
        self.preco_aquisicao = preco_aquisicao
        self.observacoes = observacoes

    def to_dict(self):
        dados = vars(self).copy()
        if self.data_aquisicao is not None:
            dados['data_aquisicao'] = self.data_aquisicao.isoformat()
        if self.preco_aquisicao is not None:
            dados['preco_aquisicao'] = str(self.preco_aquisicao)
        return dados

    @staticmethod
    def from_dict(dados):
        data = dados.get('data_aquisicao')
        preco = dados.get('preco_aquisicao')
        return Relogio(
            dados['id_usuario'], dados['id_marca'], dados['modelo'], dados['referencia'],
            dados['mecanismo'], dados['cor_mostrador'],
            date.fromisoformat(data) if isinstance(data, str) else data,
            Decimal(preco) if isinstance(preco, str) else preco,
            dados.get('observacoes'), dados.get('id_relogio'),
        )


class Foto:
    def __init__(self, id_relogio, caminho_arquivo, legenda=None, id_foto=None):
        self.id_foto = id_foto
        self.id_relogio = id_relogio
        self.caminho_arquivo = caminho_arquivo
        self.legenda = legenda

    def to_dict(self):
        return vars(self).copy()

    @staticmethod
    def from_dict(dados):
        return Foto(dados['id_relogio'], dados['caminho_arquivo'],
                    dados.get('legenda'), dados.get('id_foto'))


class Pasta:
    def __init__(self, id_usuario, nome, id_pasta=None):
        self.id_pasta = id_pasta
        self.id_usuario = id_usuario
        self.nome = nome

    def to_dict(self):
        return vars(self).copy()

    @staticmethod
    def from_dict(dados):
        return Pasta(dados['id_usuario'], dados['nome'], dados.get('id_pasta'))
