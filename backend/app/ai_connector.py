# backend/app/ai_connector.py
import os
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletion # Importa o tipo correto para Chat
from openai import AsyncAzureOpenAI

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