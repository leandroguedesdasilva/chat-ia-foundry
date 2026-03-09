import os
import psycopg2
import psycopg2.pool

# Pool de conexões.
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10, # min e max de conexões
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

class ProductRepository:
    """
    Esta classe é a única responsável por interagir com a tabela 'produtos' no banco de dados.
    Ela esconde todos os detalhes de SQL do resto da aplicação.
    """
    def inicializar_tabela(self):
        """Garante que a tabela 'produtos' exista."""
        print("--- REPOSITORY: Inicializando tabela 'produtos'... ---")
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                print("--- REPOSITORY: Verificando/Criando tabela 'produtos'... ---")
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS produtos (
                        id SERIAL PRIMARY KEY,
                        nome VARCHAR(255) NOT NULL,
                        tamanho VARCHAR(100),
                        preco NUMERIC(10, 2) NOT NULL,
                        estoque INTEGER NOT NULL
                    );
                """)
                conn.commit()
                print("--- REPOSITORY: Tabela 'produtos' pronta. ---")
        finally:
            db_pool.putconn(conn)

    def adicionar(self, nome: str, tamanho: str, preco: float, estoque: int):
        """
        Adiciona um novo produto ao banco de dados.
        Recebe dados simples e monta o SQL internamente.
        """
        conn = db_pool.getconn()
        try:
            with conn.cursor() as cur:
                print(f"--- REPOSITORY: Adicionando produto '{nome}' ao banco de dados. ---")
                cur.execute(
                    "INSERT INTO produtos (nome, tamanho, preco, estoque) VALUES (%s, %s, %s, %s)",
                    (nome, tamanho, preco, estoque)
                )
                conn.commit()
                print(f"--- REPOSITORY: Produto '{nome}' adicionado com sucesso. ---")
        finally:
            db_pool.putconn(conn)

# Criamos uma instância única do repositório que será usada em toda a aplicação (Padrão Singleton)
product_repository = ProductRepository()
