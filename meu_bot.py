import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURAÇÕES ---
TOKEN = "8379371681:AAGKNTyHK2AdLZO2fkAi34yuwOqBtl0vQ9s" 

# Para descobrir o ID, bot @userinfobot
USER_ID_TO_NOTIFY = 1828582181  # MEU ID

# Lista de palavras-chave que o bot vai procurar (não diferencia maiúsculas de minúsculas)
KEYWORDS_TO_MONITOR = ["air force", "airforce"] 
# ---------------------

# Configura o logging para ver erros no terminal
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Envia uma mensagem quando o comando /start é emitido."""
    user = update.effective_user
    await update.message.reply_html(
        f"Olá, {user.mention_html()}!\n\nEu sou seu bot de alertas. "
        f"Me adicione a um grupo e eu te avisarei quando as palavras-chave "
        f"{KEYWORDS_TO_MONITOR} forem mencionadas.",
    )


async def monitor_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Lê as mensagens do grupo e procura por palavras-chave."""
    # Ignora mensagens que não têm texto
    if not update.message or not update.message.text:
        return

    message_text = update.message.text.lower() # Converte a mensagem para minúsculas
    chat = update.effective_chat
    
    # Verifica se alguma palavra-chave está na mensagem
    for keyword in KEYWORDS_TO_MONITOR:
        if keyword in message_text:
            logger.info(f"Palavra-chave '{keyword}' encontrada no grupo '{chat.title}'")
            
            # Monta a mensagem de alerta
            # O link da mensagem só funciona em grupos públicos ou supergrupos com username
            message_link = update.message.link if update.message.link else f"no grupo '{chat.title}'"
            alert_message = (
                f"🚨 **ALERTA DE PROMOÇÃO!** 🚨\n\n"
                f"Palavra-chave encontrada: **{keyword}**\n\n"
                f"🔗 **Ver mensagem original:** {message_link}\n\n"
                f"```{update.message.text}```"
            )
            
            # Envia a notificação para o seu usuário privado
            try:
                await context.bot.send_message(
                    chat_id=USER_ID_TO_NOTIFY, 
                    text=alert_message, 
                    parse_mode='Markdown'
                )
                # Sai do loop para não enviar múltiplos alertas pela mesma mensagem
                break 
            except Exception as e:
                logger.error(f"Erro ao enviar notificação: {e}")


def main() -> None:
    """Inicia o bot."""
    # Cria o objeto da aplicação e passa o token
    application = Application.builder().token(TOKEN).build()

    # Adiciona os "manipuladores" (handlers)
    # Um para o comando /start
    application.add_handler(CommandHandler("start", start))
    
    # Outro para todas as mensagens de texto que não são comandos
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, monitor_group))

    # Inicia o bot. Ele ficará "escutando" até pará-lo (com Ctrl+C no terminal)
    logger.info("Bot iniciado. Pressione Ctrl+C para parar.")
    application.run_polling()


if __name__ == "__main__":
    main()