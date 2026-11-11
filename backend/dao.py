from pymysql.cursors import DictCursor

from models import Foto, Marca, Pasta, Relogio, Usuario


def consultar(conexao, sql, parametros=()):
    with conexao.cursor(DictCursor) as cursor:
        cursor.execute(sql, parametros)
        return cursor.fetchall()


def gravar(conexao, sql, parametros):
    try:
        with conexao.cursor() as cursor:
            cursor.execute(sql, parametros)
            resultado = cursor.rowcount, cursor.lastrowid
        conexao.commit()
        return resultado
    except Exception:
        conexao.rollback()
        raise


class UsuarioDAO:
    def __init__(self, conexao):
        self.conexao = conexao

    def buscar(self, id_usuario):
        linhas = consultar(self.conexao,
                           'SELECT id_usuario, nome, email FROM usuario WHERE id_usuario = %s',
                           (id_usuario,))
        return Usuario.from_dict(linhas[0]) if linhas else None


class MarcaDAO:
    def __init__(self, conexao):
        self.conexao = conexao

    def listar(self):
        linhas = consultar(self.conexao, 'SELECT id_marca, nome FROM marca ORDER BY nome')
        return [Marca.from_dict(linha) for linha in linhas]

    def inserir(self, marca):
        _, marca.id_marca = gravar(self.conexao, 'INSERT INTO marca (nome) VALUES (%s)',
                                   (marca.nome,))


class RelogioDAO:
    def __init__(self, conexao):
        self.conexao = conexao

    def listar(self, id_usuario):
        linhas = consultar(self.conexao,
                           'SELECT * FROM relogio WHERE id_usuario = %s ORDER BY id_relogio',
                           (id_usuario,))
        return [Relogio.from_dict(linha) for linha in linhas]

    def buscar(self, id_usuario, id_relogio):
        linhas = consultar(self.conexao,
                           'SELECT * FROM relogio WHERE id_usuario = %s AND id_relogio = %s',
                           (id_usuario, id_relogio))
        return Relogio.from_dict(linhas[0]) if linhas else None

    def inserir(self, relogio):
        _, relogio.id_relogio = gravar(self.conexao, '''
            INSERT INTO relogio (id_usuario, id_marca, modelo, referencia, mecanismo,
                                 cor_mostrador, data_aquisicao, preco_aquisicao, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (relogio.id_usuario, relogio.id_marca, relogio.modelo, relogio.referencia,
              relogio.mecanismo, relogio.cor_mostrador, relogio.data_aquisicao,
              relogio.preco_aquisicao, relogio.observacoes))

    def atualizar(self, relogio):
        linhas, _ = gravar(self.conexao, '''
            UPDATE relogio
               SET id_marca = %s, modelo = %s, referencia = %s, mecanismo = %s,
                   cor_mostrador = %s, data_aquisicao = %s, preco_aquisicao = %s,
                   observacoes = %s
             WHERE id_usuario = %s AND id_relogio = %s
        ''', (relogio.id_marca, relogio.modelo, relogio.referencia, relogio.mecanismo,
              relogio.cor_mostrador, relogio.data_aquisicao, relogio.preco_aquisicao,
              relogio.observacoes, relogio.id_usuario, relogio.id_relogio))
        return linhas > 0 or self.buscar(relogio.id_usuario, relogio.id_relogio) is not None

    def excluir(self, id_usuario, id_relogio):
        linhas, _ = gravar(self.conexao,
                           'DELETE FROM relogio WHERE id_usuario = %s AND id_relogio = %s',
                           (id_usuario, id_relogio))
        return linhas > 0


class FotoDAO:
    def __init__(self, conexao):
        self.conexao = conexao

    def listar(self, id_usuario, id_relogio):
        linhas = consultar(self.conexao, '''
            SELECT f.* FROM foto f
            INNER JOIN relogio r ON r.id_relogio = f.id_relogio
            WHERE r.id_usuario = %s AND r.id_relogio = %s ORDER BY f.id_foto
        ''', (id_usuario, id_relogio))
        return [Foto.from_dict(linha) for linha in linhas]


class PastaDAO:
    def __init__(self, conexao):
        self.conexao = conexao

    def listar(self, id_usuario):
        linhas = consultar(self.conexao,
                           'SELECT * FROM pasta WHERE id_usuario = %s ORDER BY nome',
                           (id_usuario,))
        return [Pasta.from_dict(linha) for linha in linhas]

    def buscar(self, id_usuario, id_pasta):
        linhas = consultar(self.conexao,
                           'SELECT * FROM pasta WHERE id_usuario = %s AND id_pasta = %s',
                           (id_usuario, id_pasta))
        return Pasta.from_dict(linhas[0]) if linhas else None

    def inserir(self, pasta):
        if consultar(self.conexao, 'SELECT id_pasta FROM pasta WHERE id_usuario = %s AND nome = %s',
                     (pasta.id_usuario, pasta.nome)):
            raise ValueError('Já existe uma pasta com esse nome.')
        _, pasta.id_pasta = gravar(self.conexao,
                                   'INSERT INTO pasta (id_usuario, nome) VALUES (%s, %s)',
                                   (pasta.id_usuario, pasta.nome))

    def listar_relogios(self, id_usuario, id_pasta):
        linhas = consultar(self.conexao, '''
            SELECT r.* FROM relogio r
            INNER JOIN relogio_pasta rp ON rp.id_relogio = r.id_relogio
            INNER JOIN pasta p ON p.id_pasta = rp.id_pasta
            WHERE p.id_pasta = %s AND p.id_usuario = %s AND r.id_usuario = %s
            ORDER BY r.id_relogio
        ''', (id_pasta, id_usuario, id_usuario))
        return [Relogio.from_dict(linha) for linha in linhas]

    def vincular(self, id_usuario, id_pasta, id_relogio):
        linhas, _ = gravar(self.conexao, '''
            INSERT INTO relogio_pasta (id_relogio, id_pasta)
            SELECT r.id_relogio, p.id_pasta
            FROM relogio r INNER JOIN pasta p ON p.id_usuario = r.id_usuario
            WHERE r.id_relogio = %s AND p.id_pasta = %s AND r.id_usuario = %s
        ''', (id_relogio, id_pasta, id_usuario))
        return linhas > 0

    def desvincular(self, id_usuario, id_pasta, id_relogio):
        linhas, _ = gravar(self.conexao, '''
            DELETE FROM relogio_pasta
            WHERE id_relogio = %s AND id_pasta = %s
              AND EXISTS (SELECT 1 FROM relogio r
                          WHERE r.id_relogio = relogio_pasta.id_relogio AND r.id_usuario = %s)
              AND EXISTS (SELECT 1 FROM pasta p
                          WHERE p.id_pasta = relogio_pasta.id_pasta AND p.id_usuario = %s)
        ''', (id_relogio, id_pasta, id_usuario, id_usuario))
        return linhas > 0
