document.getElementById('send-btn').addEventListener('click', async () => {
  const input = document.getElementById('msg-input');
  const chatArea = document.getElementById('chat-area');
  const msg = input.value;
  if(!msg) return;

  chatArea.innerHTML += '<div class="msg-user">' + msg + '</div>';
  input.value = '';

  const [tab] = await chrome.tabs.query({active: true, currentWindow: true});

  const resp = await fetch('https://engenheiro-producao-ai.onrender.com/api/sales-agent/chat', {
    method: 'POST', headers: {'Content-Type':'application/json'},
    body: JSON.stringify({message: msg, page: tab.url, market: 'BR'})
  });
  const data = await resp.json();
  chatArea.innerHTML += '<div class="msg-bot">' + data.response + '</div>';
  chatArea.scrollTop = chatArea.scrollHeight;
});
