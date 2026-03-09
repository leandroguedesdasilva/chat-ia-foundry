import tornado.ioloop
import tornado.web
from app.handlers import MainHandler, ChatSocketHandler
from app.repositories import product_repository

def make_app():
    """
    Cria e configura a aplicação Tornado.
    """
    # inicializar_db()
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/websocket", ChatSocketHandler),
    ])

if __name__ == "__main__":

    product_repository.inicializar_tabela()  # Garante que a tabela 'produtos' exista antes de iniciar o servidor

    app = make_app()
    app.listen(8888)
    print("Servidor Tornado iniciado na porta 8888")
    print("HTTP em http://localhost:8888" )
    print("WebSocket em ws://localhost:8888/websocket")
    tornado.ioloop.IOLoop.current().start()
