# backend/app/ai_connector.py
import os
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletion # Importa o tipo correto para Chat
from openai import AsyncAzureOpenAI
import json

# --- CONFIGURAÇÃO EXPLÍCITA - A PROVA DE ERROS ---
# Copiado diretamente do seu Azure Playground
AZURE_ENDPOINT = "https://leand-mlqwcnzd-eastus2.cognitiveservices.azure.com"
API_VERSION = "2024-02-15-preview" # Usando uma versão preview estável, como sugerido pelo Azure
AZURE_DEPLOYMENT_NAME = "gpt-5.3-chat"

# Pega a chave da variável de ambiente, que é a única coisa que deve ficar secreta
API_KEY = os.getenv("AZURE_OPENAI_API_KEY" )

# Inicializa o cliente com os valores explícitos
client = AsyncAzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION,
    api_key=API_KEY
)

async def get_ai_response_stream(user_message: str):
    """
    Envia uma mensagem para o Azure AI e retorna um stream de respostas.
    Esta função agora usa 'yield' para retornar os pedaços da resposta.
    """
    try:
        print(f"Iniciando STREAM para a pergunta: '{user_message}'")
        
        # A chamada agora inclui 'stream=True'
        response_stream = await client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": "Você é um assistente de IA prestativo."},
                {"role": "user", "content": user_message}
            ],
            max_completion_tokens=300, # Aumentei um pouco para respostas mais longas
            stream=True  # <--- A MUDANÇA MAIS IMPORTANTE!
        )
        
        # Itera sobre o stream de respostas
        async for chunk in response_stream:
            # Verifica se o chunk tem conteúdo de texto
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                # 'yield' envia o pedaço de volta para quem chamou a função
                yield content

    except Exception as e:
        print(f"[ERRO] Falha no stream com o Azure AI: {e}")
        yield "Desculpe, ocorreu um erro no stream com a IA."

def criar_prompt_json(user_message: str) -> str:
    """
    Cria um prompt que instrui a IA a extrair dados e retornar JSON.
    """
    # O contrato JSON que esperamos
    json_structure_example = """
    {
      "produto": "nome do produto",
      "tamanho": "P, M, G, ou único",
      "preco": 0.00,
      "estoque": 1
    }
    """

    # A instrução para a IA
    system_prompt = f"""
    Você é um assistente de processamento de dados. Sua tarefa é extrair informações de uma mensagem do usuário e retorná-las estritamente em formato JSON.
    A estrutura JSON que você deve usar como modelo é a seguinte:
    {json_structure_example}
    
    Se a mensagem do usuário não parecer um cadastro de produto, retorne um JSON com um campo "erro". Ex: {{"erro": "Não entendi a solicitação."}}
    Analise a seguinte mensagem do usuário e extraia os dados para o formato JSON:
    """
    
    # Retorna o prompt completo
    return f"{system_prompt}\n\nMensagem do usuário: '{user_message}'"


async def get_ai_response_as_json(user_message: str) -> dict:
    """
    Envia um prompt para a IA esperando uma resposta JSON e a retorna como um dicionário Python.
    """
    prompt = criar_prompt_json(user_message)
    
    try:
        print(f"Enviando prompt JSON para a IA...")
        
        response = await client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=500,
        )
        
        # Log do motivo de parada: 'stop'. 'length' significa que foi cortado.
        motivo_parada = response.choices[0].finish_reason
        print(f"IA finalizou com motivo: '{motivo_parada}'")

        conteudo = response.choices[0].message.content

        # Proteção contra resposta vazia ou None
        if not conteudo or not conteudo.strip():
            print("[ERRO] A IA retornou uma resposta vazia.")
            return {"erro": "A IA retornou uma resposta vazia."}

        json_string = conteudo.strip()
        print(f"IA retornou a string JSON: {json_string}")
        
        dados = json.loads(json_string)
        return dados

    except json.JSONDecodeError:
        print("[ERRO] A IA não retornou um JSON válido.")
        return {"erro": "A IA não retornou um JSON válido."}
    except Exception as e:
        print(f"[ERRO] Falha na comunicação com o Azure AI: {e}")
        return {"erro": "Falha ao comunicar com a IA."}
