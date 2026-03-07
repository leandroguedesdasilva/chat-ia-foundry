# backend/app/handlers.py
import tornado.websocket
import tornado.web
import os 
import uuid 
from app.ai_connector import get_ai_response_stream, get_ai_response_as_json 
from app.database import adicionar_produto

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    connections = set()
    # Lista para armazenar o histórico da conversa (tuplas de 'remetente', 'mensagem')
    chat_history = []

    def open(self):
        self.connections.add(self)
        print(f"Nova conexão. Total: {len(self.connections)}")
        ChatSocketHandler.broadcast(f"Um novo usuário entrou. Conectados: {len(self.connections)}")

    async def on_message(self, message):
        """
        Chamado quando o servidor recebe uma mensagem.
        Agora, vamos distribuir (broadcast) essa mensagem para todos.
        """
        print(f"Mensagem recebida: {message}")

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
            
            # Mostra uma mensagem de "processando" para o usuário
            ChatSocketHandler.broadcast("IA: Entendido. Processando cadastro de produto...")

            # Chama a função que espera um JSON
            dados_produto = await get_ai_response_as_json(message)

            # Verifica se a IA retornou um erro
            if "erro" in dados_produto or "produto" not in dados_produto:
                erro_msg = dados_produto.get("erro", "Não foi possível extrair os dados do produto.")
                ChatSocketHandler.broadcast(f"IA: Erro no cadastro. {erro_msg}")
            else:
                # Tenta adicionar ao banco de dados
                if adicionar_produto(dados_produto):
                    nome_produto = dados_produto.get('produto')
                    ChatSocketHandler.broadcast(f"IA: Sucesso! Produto '{nome_produto}' cadastrado no banco de dados.")
                else:
                    ChatSocketHandler.broadcast("IA: Erro! Não foi possível salvar o produto no banco de dados.")
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
