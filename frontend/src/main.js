// frontend/main.js
import './style.css';

// Seleciona os elementos do HTML
const messagesList = document.querySelector('#messages');
const messageForm = document.querySelector('#message-form');
const messageInput = document.querySelector('#message-input');

// Cria uma nova conexão WebSocket com o nosso backend
// Lembre-se que o backend está em ws://localhost:8888/websocket
const socket = new WebSocket('ws://localhost:8888/websocket');

// Função para adicionar uma mensagem de usuário ou de status (não-stream)
function addUserMessage(message) {
    const li = document.createElement('li');
    li.classList.add('user-message');
    li.textContent = message.substring('Você:'.length).trim();
    messagesList.appendChild(li);
    scrollToBottom();
}
function addStatusMessage(message) {
    const li = document.createElement('li');
    li.textContent = message;
    li.style.textAlign = 'center';
    li.style.color = '#888';
    li.style.fontSize = '0.9em';
    messagesList.appendChild(li);
    scrollToBottom();
}

function scrollToBottom() {
    messagesList.scrollTop = messagesList.scrollHeight;
}

// Função para adicionar uma mensagem à lista na tela
function addMessage(message) {
  const li = document.createElement('li');
  
  // Verifica se a mensagem começa com "Você:" ou "IA:"
  if (message.startsWith('Você:')) {
    li.classList.add('user-message');
    // Remove o prefixo para não exibi-lo duas vezes
    li.textContent = message.substring('Você:'.length).trim();
  } else if (message.startsWith('IA:')) {
    li.classList.add('ia-message');
    // Adiciona um pequeno avatar de robô para a IA
    li.textContent = '🤖 ' + message.substring('IA:'.length).trim();
  } else {
    // Para mensagens de status (como "Conectado ao servidor")
    li.textContent = message;
    li.style.textAlign = 'center'; // Centraliza mensagens de status
    li.style.color = '#888';
    li.style.fontSize = '0.9em';
  }
  
  messagesList.appendChild(li);
  // Rola para a mensagem mais recente
  messagesList.scrollTop = messagesList.scrollHeight;
}
// O que fazer quando a conexão for aberta com sucesso
socket.addEventListener('open', (event) => {
  console.log('Conectado ao servidor WebSocket!');
  addMessage('Conectado ao servidor!');
});

// Listener de mensagens do WebSocket (com lógica de streaming)
socket.addEventListener('message', (event) => {
    const message = event.data;

    if (message.startsWith('Você:')) {
        addUserMessage(message);
    } else if (message.startsWith('IA_STREAM_START:')) {
        // 1. Recebe o sinal de início de stream
        const messageId = message.split(':')[1];
        // Cria um novo elemento 'li' para a resposta da IA, com um ID único
        const li = document.createElement('li');
        li.classList.add('ia-message');
        li.id = `ia-message-${messageId}`; // Associa o ID do backend ao elemento
        li.innerHTML = '🤖 <span></span>'; // Usa um span para o texto que será atualizado
        messagesList.appendChild(li);
        scrollToBottom();
    } else if (message.startsWith('IA_STREAM_CHUNK:')) {
        // 2. Recebe um pedaço do stream
        const parts = message.split(':');
        const messageId = parts[1];
        const chunk = parts.slice(2).join(':'); // Reconstrói o chunk caso ele contenha ':'
        
        // Encontra o elemento 'li' correspondente pelo ID
        const li = document.getElementById(`ia-message-${messageId}`);
        if (li) {
            // Adiciona o novo pedaço de texto ao conteúdo do span
            const span = li.querySelector('span');
            span.textContent += chunk;
            scrollToBottom();
        }
    } else if (message.startsWith('IA_STREAM_END:')) {
        // 3. Recebe o sinal de fim de stream (opcional, pode ser usado para algo no futuro)
        const messageId = message.split(':')[1];
        console.log(`Stream finalizado para a mensagem ${messageId}`);
    } else {
        // Para mensagens normais (status, etc.)
        addStatusMessage(message);
    }
});

// O que fazer quando o formulário de mensagem for enviado
messageForm.addEventListener('submit', (event) => {
  console.log('Formulário enviado!');
  event.preventDefault(); // Impede o recarregamento da página
  const message = messageInput.value;
  console.log(`Mensagem a ser enviada: "${message}"`);

  if (message) {
    console.log('Enviando para o WebSocket...');
    // Envia a mensagem para o servidor WebSocket
    socket.send(message);
    // Limpa o campo de input
    messageInput.value = '';
  }
});
