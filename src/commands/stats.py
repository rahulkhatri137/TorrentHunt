from src.objs import *
from datetime import datetime
from src.functions.floodControl import floodControl

languageSet = [
        "english", 
        "nepali", 
        "bengali", 
        "belarusian", 
        "catalan", 
        "dutch",  
        "french",  
        "german",
        "hindi", 
        "italian", 
        "korean", 
        "malay", 
        "polish", 
        "portuguese", 
        "russian", 
        "spanish", 
        "turkish", 
        "ukrainian"
    ]

#: Get the Statistics of users
@bot.message_handler(commands=['stats'])
def stats(message):
    userLanguage = dbSql.getSetting(message.from_user.id, 'language')

    if message.chat.type != 'private' or floodControl(message, userLanguage):
        currentDate = datetime.now().strftime('%Y-%m-%d')

        msg = f'<b>📊 Statistics</b>\n\n'

        languageStats = {
            i.capitalize(): dbSql.getUsers(i, countOnly=True)
            for i in languageSet
        }

        languageStats = dict(
            sorted(
                languageStats.items(), key=lambda item: item[1], reverse=True
            )
        )


        for i, value in languageStats.items():
            msg += f'{i}: {value}\n'

        totalUsers = dbSql.getAllUsers(countOnly=True)
        totalGroups = dbSql.getAllUsers(type="groups", countOnly=True)

        msg += f'\n<b>Users: {totalUsers} <code>({dbSql.getAllUsers(date=currentDate, countOnly=True)} today)</code></b>'
        msg += f'\n<b>Groups: {totalGroups} <code>({dbSql.getAllUsers(type="groups", date=currentDate, countOnly=True)} today)</code></b>'

        bot.send_message(chat_id=message.chat.id, text=msg)