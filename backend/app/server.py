import tornado.ioloop
import tornado.web
from app.handlers import MainHandler, ChatSocketHandler
from app.repositories import ProductRepository

def make_app():
    """
    Cria e configura a aplicação Tornado.
    """
    print("--- SERVER: Criando instância do ProductRepository. ---")
    repo = ProductRepository()
    repo.inicializar_tabela()

    # Passe o repositório para o handler usando um dicionário no terceiro argumento
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/websocket", ChatSocketHandler, {"repository": repo}),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Servidor Tornado iniciado na porta 8888")
    print("HTTP em http://localhost:8888"  )
    print("WebSocket em ws://localhost:8888/websocket")
    tornado.ioloop.IOLoop.current().start()

