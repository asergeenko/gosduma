import logging
from typing import Dict

import orm


ITEMS_PER_PAGE = 5
from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardMarkup,InlineKeyboardButton,ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
# States
CHOOSING, TYPING_REPLY, TYPING_CHOICE,TYPING_DEPUTY_NAME,TYPING_LAW,TYPING_FACTION,CHOOSING_LAW = range(7)

# Routes
BY_DEPUTY, BY_FACTION = range(2)

DONE_BTN = ['Завершить']

reply_keyboard = [
    ['Поиск по депутату', 'Поиск по фракции'],
    DONE_BTN,
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True,one_time_keyboard=True)

done_markup = ReplyKeyboardMarkup([DONE_BTN], resize_keyboard=True,one_time_keyboard=True)

POPULAR_LAWS = {
    'Поправки в Конституцию-2020':'31837',
    'Повышение пенсионного возраста':'30043',
    'Закон Димы Яковлева':'19260',
    'Декриминализации домашнего насилия':'27757'
}
#POPULAR_LAWS_LAYOUT = [[key for key in list(POPULAR_LAWS.keys())[i:i+2]] for i in range(0,3,2)]
POPULAR_LAWS_LAYOUT = [[key for key in POPULAR_LAWS.keys()]]

def create_law_answer_for_deputy(law,vote_id):
    if law[7] == 'for':
        vote = 'за'
    elif law[7] == 'against':
        vote = 'против'
    elif law[7] == 'abstain':
        vote = 'воздержался'
    elif law[7] == 'absent':
        vote = 'не голосовал'

    return '\n'.join([
        f'<strong>{law[0]}</strong>',
        f'{law[1]}',
        f'<a href="http://vote.duma.gov.ru/vote/{vote_id}">стенограмма</a>',
        f'<strong>Голос:</strong> {vote}',
        f'<strong>Всего голосов "ЗА":</strong> {law[3]}',
        f'<strong>Всего голосов "ПРОТИВ":</strong> {law[4]}',
        f'<strong>Всего воздержались:</strong> {law[5]}',
        f'<strong>Всего не голосовали:</strong> {law[6]}',
        f'<strong>Дата:</strong> {law[2].strftime("%d.%m.%Y")}\n'
    ])

def create_law_answer_for_faction(law,vote_id):
    return '\n'.join([
        f'<strong>{law[0]}</strong>',
        f'{law[1]}',
        f'<a href="http://vote.duma.gov.ru/vote/{vote_id}">стенограмма</a>',
        f'<strong>Депутатов во фракции:</strong> {law[7]}',
        f'<strong>Голосов "ЗА" во фракции:</strong> {law[8]}',
        f'<strong>Голосов "ПРОТИВ" во фракции:</strong> {law[9]}',
        f'<strong>Воздержались во фракции:</strong> {law[10]}',
        f'<strong>Не голосовали во фракции:</strong> {law[11]}',
        f'<strong>Всего голосов "ЗА":</strong> {law[3]}',
        f'<strong>Всего голосов "ПРОТИВ":</strong> {law[4]}',
        f'<strong>Всего воздержались:</strong> {law[5]}',
        f'<strong>Всего не голосовали:</strong> {law[6]}',
        f'<strong>Дата:</strong> {law[2].strftime("%d.%m.%Y")}\n'
    ])

def start(update: Update, context: CallbackContext) -> int:
    """Start the conversation and ask user for input."""
    update.message.reply_text(
        "Бот для работы с открытыми данными Государственной Думы РФ. Вот, что он умеет:",
        reply_markup=markup,
    )

    return CHOOSING


def regular_choice(update: Update, context: CallbackContext) -> int:
    """Ask the user for info about the selected predefined choice."""
    text = update.message.text
    user_data = context.user_data
    user_data['choice'] = text

    if text == 'Поиск по депутату':
        user_data['route'] = BY_DEPUTY
        update.message.reply_text('Введите фамилию или регулярное выражение:',reply_markup=done_markup)
        return TYPING_DEPUTY_NAME

    else:
        user_data['route'] = BY_FACTION
        user_data['factions'] = {row.name:row.id for row in orm.get_factions()}
        if not user_data['factions']:
            update.message.reply_text(
                "Ничего не найдено. Попробуйте другой запрос?",
                reply_markup=markup,
            )
            return CHOOSING
        fkeyboard = [[name] for name in user_data['factions'].keys()]
        fkeyboard.append(DONE_BTN)
        fmarkup = ReplyKeyboardMarkup(fkeyboard, resize_keyboard=True,one_time_keyboard=True)
        update.message.reply_text("Выберите фракцию:",reply_markup=fmarkup)
        return TYPING_LAW


def choose_from_query(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    route = context.user_data['route']

    if route == BY_DEPUTY:
        deputies = dict(list(orm.get_deputies_by_name_regex(text)))
        if not deputies:
            update.message.reply_text(
                "Ничего не найдено. Попробуйте другой запрос?",
                reply_markup=markup,
            )
            return CHOOSING

        fkeyboard = [[name] for name in deputies.keys()]
        fkeyboard.append(DONE_BTN)
        context.user_data['deputies'] = deputies
        fmarkup = ReplyKeyboardMarkup(fkeyboard, resize_keyboard=True, one_time_keyboard=True)
        update.message.reply_text("Выберите депутата:", reply_markup=fmarkup)
        return TYPING_LAW


def type_law(update: Update, context: CallbackContext) -> int:
    text = update.message.text
    user_data = context.user_data
    route = user_data['route']
    answer = ''
    if route == BY_DEPUTY:
        deputies = user_data['deputies']
        dep_id = deputies[text]
        user_data['dep_id'] = dep_id
        user_data['dep_name'] = text

    elif route == BY_FACTION:
        factions = user_data['factions']
        fac_id = factions[text]
        user_data['fac_name'] = text
        user_data['fac_id'] = fac_id

    fkeyboard = POPULAR_LAWS_LAYOUT[:]
    fkeyboard.append(DONE_BTN)
    fmarkup = ReplyKeyboardMarkup(fkeyboard, resize_keyboard=True, one_time_keyboard=True)

    update.message.reply_text(answer + "\nВведите фразу или регулярное выражение для поиска законопроекта или выберите законопроект из списка ниже:",
                              parse_mode='html',reply_markup=fmarkup)
    return CHOOSING_LAW

def choice_law(update: Update, context: CallbackContext) -> int:
    user_data = context.user_data
    answer = ''
    route = user_data['route']
    first_request = False


    if 'laws' not in user_data:
        first_request = True
        text = update.message.text
        user_data['page']=0

        if route == BY_DEPUTY:
            if text in POPULAR_LAWS.keys():
                laws = {str(law[0]):law[1:] for law in orm.get_law_by_id_for_deputy(user_data['dep_id'], POPULAR_LAWS[text])}
            else:
                laws = {str(law[0]): law[1:] for law in orm.get_laws_by_deputy(user_data['dep_id'], text)}
        elif route == BY_FACTION:
            if text in POPULAR_LAWS.keys():
                laws = {str(law[0]):law[1:] for law in orm.get_law_by_id_for_faction(user_data['fac_id'], POPULAR_LAWS[text])}
            else:
                laws = {str(law[0]): law[1:] for law in orm.get_laws_by_faction(user_data['fac_id'], text)}

        if not laws:
            update.message.reply_text(f"Законопроекты по запросу <i>'{text}'</i> для {'данного депутата' if  route == BY_DEPUTY else 'данной фракции'} не найдены. Попробуйте друой запрос:",
                                      parse_mode='html',reply_markup=done_markup)
            return CHOOSING_LAW

        user_data['laws'] = laws
        user_data['num_pages'] = len(laws) // ITEMS_PER_PAGE
        if len(laws) % ITEMS_PER_PAGE:
            user_data['num_pages'] += 1



    else:
        query = update.callback_query
        try:
            query.answer()
        except Exception as e:
            logger.exception(str(e))
        data = query.data

        if data == 'prev':
            user_data['page'] -= 1

        elif data == 'next':
            user_data['page'] += 1

        else:
            law = user_data['laws'][data]

            if route == BY_DEPUTY:
                answer += user_data['dep_name'] + '\n' + create_law_answer_for_deputy(law,data)

            elif route == BY_FACTION:
                answer += user_data['fac_name']+'\n' + create_law_answer_for_faction(law,data)




    footer = []
    start = user_data['page']*ITEMS_PER_PAGE
    fkeyboard = [[InlineKeyboardButton(value[0] + '\n' + value[1], callback_data=key)]
                 for key, value in
                 list(user_data['laws'].items())[start:start + ITEMS_PER_PAGE]]
    if user_data['page'] > 0:
        footer.append(InlineKeyboardButton('Пред.',callback_data='prev'))
    if user_data['page'] < user_data['num_pages'] - 1:
        footer.append(InlineKeyboardButton('След.', callback_data='next'))

    fkeyboard.append(footer)
    fkeyboard.append([InlineKeyboardButton('Завершить',callback_data='done')])

    fmarkup = InlineKeyboardMarkup(fkeyboard)
    if user_data['page']==user_data['num_pages']-1:
        # Last page
        to = len(user_data['laws'])
    else:
        to = (user_data['page'] + 1) * ITEMS_PER_PAGE
    answer += f"\nГолосования {user_data['page']*ITEMS_PER_PAGE+1}-{to} из {len(user_data['laws'])}:"

    if update.callback_query:
        #if first_request:
        #    update.callback_query.edit_message_text(' ', reply_markup=ReplyKeyboardRemove())
        update.callback_query.edit_message_text(answer, reply_markup=fmarkup,parse_mode='html')
    else:
        update.message.reply_text(answer, reply_markup=fmarkup,parse_mode='html')
    return CHOOSING_LAW



# Удалить 'laws', 'page','num_pages'

def done(update: Update, context: CallbackContext) -> int:
    """Display the gathered info and end the conversation."""
    user_data = context.user_data

    answer = "Всего доброго!\nНажмите /start для следующего запроса."

    if update.callback_query:
        update.callback_query.answer(answer)#, reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(answer)#, reply_markup=ReplyKeyboardRemove())


    user_data.clear()
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex('^(Поиск по депутату|Поиск по фракции)$'), regular_choice
                ),
                MessageHandler(Filters.text & ~Filters.command, done),
            ],
            TYPING_DEPUTY_NAME: [
                MessageHandler(Filters.regex('^Завершить$'), done),
                MessageHandler(Filters.text & ~Filters.command,choose_from_query),
            ],
            TYPING_LAW: [MessageHandler(Filters.regex('^Завершить$'), done),
                MessageHandler(Filters.text & ~Filters.command, type_law)],
            CHOOSING_LAW: [MessageHandler(Filters.regex('^Завершить$'), done),
                MessageHandler(Filters.text & ~Filters.command, choice_law),
                           CallbackQueryHandler(choice_law,pattern='^(prev|next|[0-9]+)$')],
            
            TYPING_CHOICE: [MessageHandler(Filters.regex('^Завершить$'), done),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^Завершить$'), done),
                   CallbackQueryHandler(done,pattern='^done$')],
        allow_reentry=True
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
