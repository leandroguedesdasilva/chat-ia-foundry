from pydantic import BaseModel, Field

class ProdutoCreateDTO(BaseModel):
    """
    Data Transfer Object (DTO) para a criação de um produto.
    Ele valida e converte os dados recebidos da IA.
    """
    # O Field(..., alias='...') nos permite mapear o nome do campo no JSON da IA
    # para um nome de atributo mais idiomático em Python.
    nome: str = Field(..., alias='produto')
    tamanho: str = 'único' # Define um valor padrão se não for fornecido
    preco: float
    estoque: int = 1 # Define um valor padrão se não for fornecido

    class Config:
        # Permite que o Pydantic leia os dados mesmo que o campo no dicionário
        # não seja exatamente igual ao nome do atributo na classe.
        populate_by_name = True
        # Garante que o Pydantic não reclame de campos extras que a IA possa mandar
        extra = 'ignore'
        
