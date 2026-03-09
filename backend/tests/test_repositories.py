import pytest
from app.repositories import product_repository

# Marcamos todos os testes neste arquivo para serem executados com asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """
    Uma "fixture" do pytest. Este código roda UMA VEZ antes de todos os testes neste arquivo.
    Ele garante que a tabela de produtos exista.
    O 'yield' é onde os testes rodam. O código depois do 'yield' rodaria no final.
    """
    print("\n--- SETUP DE TESTE: Garantindo que a tabela 'produtos' existe. ---")
    product_repository.inicializar_tabela()
    yield
    print("\n--- TEARDOWN DE TESTE: Testes concluídos. ---")


async def test_adicionar_produto_com_sucesso():
    """
    Testa o caso de sucesso do método 'adicionar'.
    Ele verifica se o método pode ser chamado sem levantar uma exceção.
    """
    nome_teste = "Produto Pytest"
    tamanho_teste = "Médio"
    preco_teste = 123.45
    estoque_teste = 50

    try:
        product_repository.adicionar(
            nome=nome_teste,
            tamanho=tamanho_teste,
            preco=preco_teste,
            estoque=estoque_teste
        )
        sucesso = True
    except Exception as e:
        print(f"O teste falhou com uma exceção inesperada: {e}")
        sucesso = False

    # Verifica se o resultado foi o esperado
    assert sucesso is True, "O método adicionar() não deveria levantar uma exceção."

    # TODO: fazer um SELECT no banco
    # para confirmar que a linha foi realmente inserida com os dados corretos.
