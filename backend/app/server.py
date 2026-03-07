# backend/app/server.py
import tornado.ioloop
import tornado.web
# Importe ambos os handlers agora
from app.handlers import MainHandler, ChatSocketHandler

def make_app():
    """
    Cria e retorna a aplicação Tornado, associando rotas aos handlers.
    """
    return tornado.web.Application([
        (r"/", MainHandler),  # A rota raiz ainda mostra a página de status
        (r"/websocket", ChatSocketHandler), # Nova rota para a conexão WebSocket
    ])

if __name__ == "__main__":
    app = make_app()
    port = 8888
    app.listen(port)
    print(f"Servidor Tornado iniciado na porta {port}")
    print(f"HTTP em http://localhost:{port}" )
    print(f"WebSocket em ws://localhost:{port}/websocket")
    
    tornado.ioloop.IOLoop.current().start()
