"""Conexão inicial com MySQL."""
import getpass
import os
import pymysql


def conectar(senha):
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', '127.0.0.1'),
        port=int(os.getenv('MYSQL_PORT', '3306')),
        user=os.getenv('MYSQL_USER', 'root'),
        password=senha,
        database=os.getenv('MYSQL_DATABASE', 'colecao_relogios'),
        charset='utf8mb4',
        connect_timeout=5,
    )


def verificar(conexao):
    cursor = conexao.cursor()
    try:
        cursor.execute('SHOW TABLES')
        tabelas = [linha[0] for linha in cursor.fetchall()]
        esperadas = ['usuario', 'marca', 'relogio', 'foto', 'pasta', 'relogio_pasta']
        for tabela in esperadas:
            if tabela not in tabelas:
                raise ValueError('Tabela ausente: ' + tabela)
        cursor.execute('SELECT nome FROM marca ORDER BY nome')
        marcas = [linha[0] for linha in cursor.fetchall()]
        iniciais = ['Casio', 'Orient', 'Seiko', 'Citizen', 'Rolex', 'Omega',
                    'TAG Heuer', 'Cartier', 'Tissot', 'Longines']
        for marca in iniciais:
            if marca not in marcas:
                raise ValueError('Marca inicial ausente: ' + marca)
        return tabelas, marcas
    finally:
        cursor.close()


def main():
    conexao = None
    senha = os.getenv('MYSQL_PASSWORD')
    if senha is None:
        senha = getpass.getpass('Senha MySQL (oculta): ')
    try:
        conexao = conectar(senha)
        tabelas, marcas = verificar(conexao)
        print('Conexao OK. Seis tabelas e dez marcas iniciais verificadas.')
        return 0
    except (pymysql.MySQLError, ValueError):
        print('Falha: confira o servidor, as credenciais e a execucao de banco.sql.')
        return 1
    finally:
        if conexao is not None:
            conexao.close()


if __name__ == '__main__':
    raise SystemExit(main())
