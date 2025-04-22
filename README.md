## Descrição  
DJ Maluco Bastos é um bot de música para Discord que conecta em canais de voz e reproduz áudio diretamente de URLs do YouTube ou de playlists inteiras usando yt_dlp e FFmpeg citeturn0search1. Ele gerencia filas de reprodução e responde com embeds que indicam o que está tocando citeturn0search0.

---

## Funcionalidades  
- **Reprodução de YouTube**: Toca vídeos completos do YouTube sem interrupções citeturn0search1.  
- **Gerenciamento de fila**: Comandos para adicionar (`!play`), exibir (`!queue`), pular (`!skip`) e limpar (`!wipe`) a fila.   
- **Embeds personalizadas**: Respostas visuais com título, autor do pedido e miniaturas das faixas.  
- **Leve e eficiente**: Baixa apenas o áudio e o transmite via FFmpeg para minimizar consumo de banda.

---

## Pré-requisitos  
- **Python 3.8+** citeturn0search6  
- **FFmpeg** instalado e disponível no PATH do sistema.  
- **Uma aplicação/bot no Discord** com token válido.

---

## Instalação  

1. **Clone o repositório**  
   ```bash
   git clone https://github.com/SEU_USUARIO/discord-music-bot.git
   cd discord-music-bot
   ```  

2. **Crie e ative um ambiente virtual**  
   ```bash
   python3 -m venv venv
   source venv/bin/activate     # Linux/macOS
   venv\Scripts\activate        # Windows
   ```  

3. **Instale as dependências**  
   ```bash
   pip install -r requirements.txt
   ```  

4. **Crie uma aplicação de bot de discord e gere o token**  
  Como criar uma aplicação de bot de discord e pegar o token:
  `https://www.youtube.com/watch?v=0M06NLY1DjA`

---

## Uso  

1. **Inicie o bot**  
   ```bash
   python dj_maluco.py
   ```  
2. **Convide o bot**  
   Use a URL de autorização com os escopos `bot` e `applications.commands`.  
3. **Execute comandos** no Discord:

| Comando              | Descrição                                  |
|----------------------|--------------------------------------------|
| `!connect_to_voice`  | Faz o bot entrar no canal de voz atual     |
| `!play <URL>`        | Enfileira vídeo ou playlist do YouTube     |
| `!queue` / `!q`      | Exibe as músicas na fila                   |
| `!now` / `!n`        | Mostra a música em reprodução              |
| `!pause`             | Pausa a reprodução                         |
| `!resume` / `!r`     | Retoma a reprodução                        |
| `!skip` / `!s`       | Pula para a próxima faixa                  |
| `!wipe` / `!w`       | Limpa toda a fila                          |
| `!stop`              | Para a reprodução (permanece no canal)     |
| `!quit`              | Para e desconecta o bot do canal de voz    |

---

## Contribuição  
1. Fork este repositório.  
2. Crie uma branch de feature:  
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```  
3. Faça seus commits e `push` na sua fork.  
4. Abra um Pull Request.

---
