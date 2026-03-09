from app.repositories import ProductRepository
from backend.app.models import ProdutoCriarDTO

class ServicoProduto:
    """
    Camada de Serviço para a lógica de negócio de Produtos.
    Ela não sabe nada sobre a web (HTTP, WebSockets).
    Sua única responsabilidade é executar a lógica de negócio.
    """
    def __init__(self, repositorio: ProductRepository):
        """
        Injeta a dependência do repositório.
        O serviço precisa do repositório para acessar os dados.
        """
        print("--- SERVICO: Injetando dependência do repositório no serviço ---")
        self.repositorio = repositorio

    def criar_produto(self, produto_dto: ProdutoCriarDTO):
        """
        Recebe um DTO validado e o persiste no banco de dados.
        """
        print(f"--- SERVICO: Criando produto '{produto_dto.nome}' ---")
        
        # NOTA: Aqui é o lugar ideal para adicionar mais lógica de negócio no futuro, por exemplo:
        # - Verificar se um produto com o mesmo nome já existe antes de criar.
        # - Enviar um email de notificação para o administrador.
        # - Validar se o preço está dentro de uma faixa permitida.

        # A lógica atual é simples: apenas chama o repositório para salvar.
        self.repositorio.adicionar(
            nome=produto_dto.nome,
            tamanho=produto_dto.tamanho,
            preco=produto_dto.preco,
            estoque=produto_dto.estoque
        )
        
        # No futuro, este método poderia retornar o objeto completo que foi criado no banco.
        return produto_dto
