from src.objs import *
from src.functions.resultParser import result
from src.functions.funs import textToCategory
from src.commands.querySearch import querySearch
from src.functions.keyboard import mainReplyKeyboard, categoryReplyKeyboard

#: Handler for trending, popular, top and browse torrents
def browse(message,userLanguage, torrentType=None, customMessage=None):
    if message.chat.type == 'private':
        torrentType = torrentType or message.text.split()[0][1:]

        sent = bot.send_message(
            message.chat.id,
            text=customMessage or language['selectCategory'][userLanguage],
            reply_markup=categoryReplyKeyboard(
                userLanguage,
                allCategories=torrentType not in ['browse', 'popular'],
                restrictedMode=dbSql.getSetting(
                    message.chat.id, 'restrictedMode'
                ),
            ),
        )

        bot.register_next_step_handler(sent, browse2, userLanguage, torrentType)

    else:
        querySearch(message, userLanguage)

#: Next step handler for trending, popular, top and browse torrents
def browse2(message, userLanguage, torrentType, category=None, customMessage=None):
    #! Main menu
    if message.text == language['mainMenuBtn'][userLanguage]:
        bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))

    elif category := category or textToCategory(message.text, userLanguage):
        #! Send time keyboard if trending and popular torrents
        if torrentType in ['trending', 'popular']:
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)

            button1 = telebot.types.KeyboardButton(text=language['trendingToday' if torrentType == 'trending' else 'popularToday'][userLanguage])
            button2 = telebot.types.KeyboardButton(text=language['trendingThisWeek' if torrentType == 'trending' else 'popularThisWeek'][userLanguage])
            button3 = telebot.types.KeyboardButton(text=language['backBtn'][userLanguage])
            button4 = telebot.types.KeyboardButton(text=language['mainMenuBtn'][userLanguage])

            keyboard.row(button1)
            keyboard.row(button2)
            keyboard.row(button3, button4)

            sent = bot.send_message(message.chat.id, text=customMessage or language['selectTimePeriod'][userLanguage], reply_markup=keyboard)
            bot.register_next_step_handler(sent, browse3, userLanguage, torrentType, category)

        else:
            browse4(message, userLanguage, torrentType, category)
    else:
        browse(message, userLanguage, torrentType, customMessage=language['unknownCategory'][userLanguage])

#: Next step handler for trending and popular torrents
def browse3(message, userLanguage, torrentType, category):
    #! Main menu
    if message.text == language['mainMenuBtn'][userLanguage]:
        bot.send_message(message.chat.id, text=language['backToMenu'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))

    elif message.text == language['backBtn'][userLanguage]:
        browse(message,userLanguage, torrentType)

    else:
        week = (
            True
            if message.text == language[f'{torrentType}ThisWeek'][userLanguage]
            else False
            if message.text == language[f'{torrentType}Today'][userLanguage]
            else None
        )


        #! If week is None, return to browse2
        if week is None:
            browse2(message, userLanguage, torrentType, category, customMessage=language['unknownTimePeriod'][userLanguage])

        else:
            resultType = dbSql.getSetting(message.chat.id, 'defaultMode')
            bot.send_message(message.chat.id, text=language['fetchingTorrents'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))

            response =  getattr(torrent, torrentType)(category=None if category == 'all' else category, week=week)
            msg, markup = result(response, userLanguage, resultType, torrentType, 1, category, week)

            bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)

#: Next step handler for top and browse torrents
def browse4(message, userLanguage, torrentType, category):
    bot.send_message(message.chat.id, text=language['fetchingTorrents'][userLanguage], reply_markup=mainReplyKeyboard(userLanguage))
    resultType = dbSql.getSetting(message.chat.id, 'defaultMode')
    
    response =  getattr(torrent, torrentType)(category=None if category == 'all' else category)
    msg, markup = result(response, userLanguage, resultType, torrentType, 1, category)

    bot.send_message(chat_id=message.chat.id, text=msg or language['emptyPage'][userLanguage], reply_markup=markup)