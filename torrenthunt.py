import ssl
import telebot
from aiohttp import web

from src import *

#: Configuration for webhook
webhookBaseUrl = f"https://{config['webhookOptions']['webhookHost']}:{config['webhookOptions']['webhookPort']}"
webhookUrlPath = f"/{config['botToken']}/"

app = web.Application()

#: Process webhook calls
async def handle(request):
    if request.match_info.get('token') != bot.token:
        return web.Response(status=403)
    request_body_dict = await request.json()
    update = telebot.types.Update.de_json(request_body_dict)
    bot.process_new_updates([update])
    return web.Response()

app.router.add_post('/{token}/', handle)
    
#: Text handler
@bot.message_handler(content_types=['text'])
def text(message):
    userLanguage = dbSql.getSetting(message.chat.id, 'language')

    if message.chat.type != 'private' or floodControl(message, userLanguage):
        if 'via_bot' in message.json.keys():
            #! Don't search if the message is via the same bot
            if message.json['via_bot']['id'] == int(botId):
                if message.text.startswith('💫'):
                    message.text = message.text[1:]
                    querySearch(message, userLanguage)

            elif message.json['via_bot']['username'] == 'imdb':
                message.text = message.text.split(' •')[0]
                querySearch(message, userLanguage)

        elif message.text == language['mainMenuBtn'][userLanguage]:
            bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))

        elif message.text in ['/trending', language['trendingBtn'][userLanguage]]:
            browse(message, userLanguage, 'trending')

        elif message.text in ['/popular', language['popularBtn'][userLanguage]]:
            browse(message, userLanguage, 'popular')

        elif message.text in ['/top', language['topBtn'][userLanguage]]:
            browse(message, userLanguage, 'top')

        elif message.text in ['/browse', language['browseBtn'][userLanguage]]:
            browse(message, userLanguage, 'browse')

        elif message.text == language['settingsBtn'][userLanguage]:
            settings(message, userLanguage)

        elif message.text == language['helpBtn'][userLanguage]:
            help(message, userLanguage)

        elif message.text == language['supportBtn'][userLanguage]:
            support(message, userLanguage)

        else:
            querySearch(message, userLanguage)

#: Polling Bot
if config['connectionType'] == 'polling':
    #! Remove previous webhook if exists
    bot.remove_webhook()
    bot.polling(none_stop=True)

#: Webhook Bot
elif config['connectionType'] == 'webhook':
    #! Set webhook
    bot.set_webhook(url=webhookBaseUrl + webhookUrlPath,
                    certificate=open(config['webhookOptions']['sslCertificate'], 'r'))

    #! Build ssl context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(config['webhookOptions']['sslCertificate'], config['webhookOptions']['sslPrivatekey'])

    #! Start aiohttp server
    web.run_app(
        app,
        host=config['webhookOptions']['webhookListen'],
        port=config['webhookOptions']['webhookPort'],
        ssl_context=context,
    )
