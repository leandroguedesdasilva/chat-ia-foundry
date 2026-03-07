# Documento de Procedimento Gerado por IA

Este documento foi gerado a partir de uma conversa com um agente de IA.

---

> **Você:** Qual o primeiro passo para criar um servidor web em Python com Tornado?

O primeiro passo é **instalar o Tornado** no seu ambiente Python.

No terminal:

- pip install tornado

Depois disso você já pode começar criando um script Python que define um **RequestHandler** e inicia o servidor.

Exemplo mínimo:

```
import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Olá, mundo!")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```

Execute o arquivo e acesse:
http://localhost:8888

Isso já inicia um servidor web básico com Tornado.

> **Você:** E como eu defino uma rota para a página principal?

Depende do framework ou tecnologia que você está usando. Em geral, a **página principal (home)** usa a rota raiz: `/`.

Exemplos rápidos:

• **Express (Node.js)**
```js
app.get('/', (req, res) => {
  res.send('Página principal');
});
```

• **React Router**
```jsx
<Route path="/" element={<Home />} />
```

• **Laravel**
```php
Route::get('/', function () {
    return view('home');
});
```

• **Django**
```python
path('', views.home, name='home')
```

Se você quiser, me diga **qual framework ou linguagem** está usando (React, Next.js, Laravel, Django, Express, etc.), que eu mostro exatamente como fazer nele.

> **Você:** Ótimo, agora como eu inicio o servidor na porta 8080?

Depende de qual servidor/tecnologia você está usando. Alguns exemplos comuns:

- Node.js (Express):
  - No código: `app.listen(8080)`

- Python (HTTP simples):
  - `python -m http.server 8080`

- Flask:
  - `flask run --port 8080`

- Django:
  - `python manage.py runserver 0.0.0.0:8080`

- Java (Spring Boot):
  - em `application.properties`: `server.port=8080`

- Docker:
  - `docker run -p 8080:8080 imagem`

Se você me disser qual servidor ou framework está usando, te passo o comando exato.

