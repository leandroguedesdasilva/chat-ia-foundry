import tornado.ioloop
import tornado.web
from app.handlers import MainHandler, ChatSocketHandler
# from app.database import inicializar_db

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
    app = make_app()
    app.listen(8888)
    print("Servidor Tornado iniciado na porta 8888")
    print("HTTP em http://localhost:8888" )
    print("WebSocket em ws://localhost:8888/websocket")
    tornado.ioloop.IOLoop.current().start()
