# backend/app/handlers.py
from email.mime import message

import tornado.websocket
import tornado.web
import os 
import uuid 
from app.ai_connector import get_ai_response_stream, get_ai_response_as_json 
#from app.repositories import product_repository # comentado para a implementação do DI, mas mantido para referência futura



class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    connections = set()
    # Lista para armazenar o histórico da conversa (tuplas de 'remetente', 'mensagem')
    chat_history = []

    def initialize(self, repository):
        """
        Este método é chamado pelo Tornado quando o handler é criado.
        Ele "injeta" a dependência.
        """
        print("--- HANDLER: Injetando dependência do repositório ---")
        self.repository = repository

    def open(self):
        self.connections.add(self)
        print(f"Nova conexão. Total: {len(self.connections)}")
        ChatSocketHandler.broadcast(f"Um novo usuário entrou. Conectados: {len(self.connections)}")

    async def on_message(self, message):
        """
        Chamado quando o servidor recebe uma mensagem.
        Agora, vamos distribuir (broadcast) essa mensagem para todos.
        """
        print(f"--- HANDLER: MENSAGEM BRUTA RECEBIDA: '{message}' ---", flush=True)
        print(f"Mensagem recebida: {message}", flush=True)

        # ETAPA 1: VERIFICAR SE É UM COMANDO
        if message.strip() == "/criar_documento":
            # Se for o comando, chama a função para gerar o documento
            file_path = self.generate_markdown_document()
            # Avisa o usuário que o documento foi criado
            ChatSocketHandler.broadcast(f"IA: Documento gerado com sucesso em: {file_path}")
            return # Para a execução aqui, não envia o comando para a IA

       # Adiciona a pergunta ao histórico e a envia para o frontend
        self.chat_history.append(("Você", message))
        ChatSocketHandler.broadcast(f"Você: {message}")


        # --- LÓGICA DE ROTEAMENTO ---
        # Se a mensagem começar com um comando específico, use a lógica de JSON
        if message.lower().strip().startswith("cadastre"):
            print("--- HANDLER: Processando comando de cadastro ---", flush=True)
            ChatSocketHandler.broadcast("IA: Entendido. Processando cadastro de produto...")
    
            try:
                # PASSO 1: Chama a função que JÁ retorna um dicionário
                dados_dict = await get_ai_response_as_json(message)
                print(f"--- HANDLER: Resposta da IA (já como dict): {dados_dict} ---", flush=True)

                # PASSO 2: Verifica se a IA retornou um erro LÓGICO
                if "erro" in dados_dict or "produto" not in dados_dict:
                    erro_msg = dados_dict.get("erro", "Não foi possível extrair os dados do produto.")
                    ChatSocketHandler.broadcast(f"IA: Erro no cadastro. {erro_msg}")
                else:
                    # PASSO 3: Tenta salvar no banco de dados
                    nome_produto = dados_dict['produto'] 
                    tamanho = dados_dict.get('tamanho', 'único')
                    preco = float(dados_dict['preco'])
                    estoque = int(dados_dict.get('estoque', 1))

                    self.repository.adicionar(
                        nome=nome_produto,
                        tamanho=tamanho,
                        preco=preco,
                        estoque=estoque
                    )
                    
                    ChatSocketHandler.broadcast(f"IA: Sucesso! Produto '{nome_produto}' cadastrado no banco de dados.")
            except (ValueError, TypeError, KeyError) as e:
                # Captura erros de conversão de tipo ou chave faltando
                print(f"--- HANDLER: ERRO de dados ou tipo: {e} ---", flush=True)
                ChatSocketHandler.broadcast("IA: Erro! Os dados retornados pela IA estão incompletos ou em formato inesperado.")
            except Exception as e:
                # Captura TODOS os outros erros, incluindo falhas na chamada da IA
                print(f"--- HANDLER: ERRO genérico: {e} ---", flush=True)
                ChatSocketHandler.broadcast("IA: Erro! Não foi possível processar o seu pedido.")
            return
        # Se for qualquer outra mensagem, usa o chat normal com streaming
        else:
            message_id = str(uuid.uuid4())
            ChatSocketHandler.broadcast(f"IA_STREAM_START:{message_id}")

            full_response = ""
            # 2. Itera sobre os pedaços recebidos do gerador
            async for chunk in get_ai_response_stream(message):
                # Acumula a resposta completa para o histórico
                full_response += chunk
                # 3. Retransmite cada pedaço para o frontend com o ID
                ChatSocketHandler.broadcast(f"IA_STREAM_CHUNK:{message_id}:{chunk}")
            
            # 4. Envia uma mensagem de fim de stream
            ChatSocketHandler.broadcast(f"IA_STREAM_END:{message_id}")

            # 5. Salva a resposta completa no histórico
            self.chat_history.append(("IA", full_response))

    def on_close(self):
        self.connections.remove(self)
        print(f"Conexão fechada. Total: {len(self.connections)}")
        # Avisa a todos que um usuário saiu
        ChatSocketHandler.broadcast(f"Um usuário saiu. Conectados: {len(self.connections)}")

    def check_origin(self, origin):
        return True
    
    

    @classmethod
    def broadcast(cls, message):
        """
        Método de classe para enviar uma mensagem para todos os clientes conectados.
        """
        print(f"Distribuindo mensagem: '{message}' para {len(cls.connections)} clientes.")
        for conn in cls.connections:
            try:
                conn.write_message(message)
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")

    # ETAPA 3: MÉTODO PARA GERAR O DOCUMENTO MARKDOWN
    @classmethod
    def generate_markdown_document(cls):
        """
        Pega o histórico do chat e o salva como um arquivo Markdown.
        """
        print("Gerando documento Markdown a partir do histórico do chat...")
        
        # Define o nome do arquivo e o caminho (dentro da pasta 'backend')
        file_name = "procedimento.md"
        file_path = os.path.join(os.path.dirname(__file__), '..', file_name) # Salva na pasta 'backend'

        # Abre o arquivo para escrita
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("# Documento de Procedimento Gerado por IA - Meu modelo no Foundry 👌\n\n")
            f.write("---\n\n")

            for sender, msg in cls.chat_history:
                if sender == "Você":
                    # Formata a pergunta do usuário como uma citação
                    f.write(f"> **Você:** {msg}\n\n")
                elif sender == "IA":
                    # Formata a resposta da IA como texto normal
                    f.write(f"{msg}\n\n")
        
        print(f"Documento salvo em: {file_path}")
        # Limpa o histórico após gerar o documento para a próxima sessão
        cls.chat_history.clear()
        return file_path

# Handler da página principal, sem alterações
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Servidor de WebSocket está no ar. Conecte-se na rota /websocket")
