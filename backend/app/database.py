import os
import psycopg2
from psycopg2 import pool
import time

# Lê as credenciais do banco de dados a partir das variáveis de ambiente
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

connection_pool = None
db_initialized = False # Adiciona uma flag de controle

def inicializar_db(pool_instance):
    """Cria a tabela de produtos se ela não existir."""
    global db_initialized
    if db_initialized:
        return

    conn = None
    try:
        conn = pool_instance.getconn()
        with conn.cursor() as cur:
            print("Verificando/Criando tabela 'produtos'...")
            cur.execute('''
                CREATE TABLE IF NOT EXISTS produtos (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    tamanho VARCHAR(50),
                    preco NUMERIC(10, 2) NOT NULL,
                    estoque INTEGER NOT NULL,
                    data_criacao TIMESTAMPTZ DEFAULT NOW()
                )
            ''')
            conn.commit()
            print("Tabela 'produtos' pronta.")
            db_initialized = True # Marca como inicializado com sucesso
    except Exception as e:
        print(f"Erro ao inicializar a tabela: {e}")
    finally:
        if conn:
            pool_instance.putconn(conn)

def get_connection_pool():
    """Cria e retorna o pool de conexões, tentando reconectar se necessário."""
    global connection_pool
    if connection_pool is None:
        print("Criando pool de conexões com o PostgreSQL...")
        for i in range(5): # Tenta conectar 5 vezes
            try:
                connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 5, # min e max de conexões
                    host=DB_HOST,
                    dbname=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD
                )
                print("Pool de conexões criado com sucesso.")
                # Garante que a tabela seja criada assim que o pool for estabelecido
                inicializar_db(connection_pool)
                break # Sai do loop se conectar
            except psycopg2.OperationalError as e:
                print(f"Tentativa {i+1}/5: Não foi possível conectar ao PostgreSQL. Tentando novamente em 2 segundos... Erro: {e}")
                time.sleep(2)
    return connection_pool

def adicionar_produto(dados_produto: dict):
    """Adiciona um novo produto ao banco de dados PostgreSQL."""
    pool = get_connection_pool()
    if not pool:
        print("Adição de produto falhou: não há pool de conexões.")
        return False

    conn = None
    try:
        conn = pool.getconn()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO produtos (nome, tamanho, preco, estoque) VALUES (%s, %s, %s, %s)",
                (
                    dados_produto.get("produto"),
                    dados_produto.get("tamanho"),
                    dados_produto.get("preco"),
                    dados_produto.get("estoque", 1)
                )
            )
            conn.commit()
            print(f"Produto '{dados_produto.get('produto')}' adicionado ao PostgreSQL.")
            return True
    except Exception as e:
        print(f"Erro ao adicionar produto no PostgreSQL: {e}")
        return False
    finally:
        if conn:
            pool.putconn(conn)
