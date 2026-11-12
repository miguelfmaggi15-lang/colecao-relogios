import os
from pathlib import Path

from conexao import conectar

EMAIL_DEMONSTRACAO = 'demonstracao@example.invalid'


def preparar():
    arquivo = Path(__file__).resolve().parent.parent / 'database' / 'banco.sql'
    _, separador, tabelas_e_dados = arquivo.read_text(encoding='utf-8').partition(
        'USE colecao_relogios;'
    )
    tabelas, comentario, dados = tabelas_e_dados.partition('-- Dados iniciais:')
    if not separador or not comentario:
        raise RuntimeError('O formato de banco.sql mudou.')

    with conectar(os.environ['MYSQL_PASSWORD']) as conexao:
        with conexao.cursor() as cursor:
            for comando in tabelas.split(';'):
                if comando.strip():
                    cursor.execute(comando)
            cursor.execute('SELECT COUNT(*) FROM marca')
            if cursor.fetchone()[0] == 0:
                cursor.execute(dados.split('\n', 1)[1])
            cursor.execute('SELECT id_usuario FROM usuario WHERE email = %s',
                           (EMAIL_DEMONSTRACAO,))
            usuario = cursor.fetchone()
            if usuario is None:
                cursor.execute(
                    'INSERT INTO usuario (id_usuario, nome, email, senha_hash) VALUES (1, %s, %s, %s)',
                    ('Demonstração', EMAIL_DEMONSTRACAO, 'SEM_LOGIN'),
                )
            elif usuario[0] != 1:
                raise RuntimeError('O usuário fictício precisa ter o ID 1.')
        conexao.commit()


if __name__ == '__main__':
    preparar()
