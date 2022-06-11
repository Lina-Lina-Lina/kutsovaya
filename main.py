import random
import logging

from telegram import Update, ForceReply, ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from db import add_word, get_random_word, get_user_carts, change_card_translate, delete_card
from conf import TOKEN
from common import get_user, translate


def get_info(update: Update, context: CallbackContext, text: str = 'Выберите действие:') -> None:
    if update.message:
        message = update.message
    else:
        message = update.callback_query.message

    keyboard = [
        [
            InlineKeyboardButton('Добавить карточку', callback_data='1'),
        ], [
            InlineKeyboardButton('Сгенерировать карточку', callback_data='2'),
        ], [
            InlineKeyboardButton('Редактировать карточку', callback_data='3'),
        ], [
            InlineKeyboardButton('Удалить карточку', callback_data='4'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    message.reply_text(text, reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    """Parses the CallbackQuery and updates the message text."""
    user_obj = get_user(update)
    query = update.callback_query

    query.answer()
    btn_data = query.data

    if btn_data.startswith('a'):
        action, answer = btn_data.split('_')
        if answer == '1':
            text = 'Вы выбрали правильный ответ.'
        if answer == '0':
            text = 'Вы ошиблись.'
        
        get_info(update, context, text)
        return

    if btn_data == '1':
        context.user_data['action'] = {'action': 'a'}
        text = 'Наберите слово на английском языке'
        update.callback_query.message.reply_text(text)
        return

    if btn_data == '2':
        try:
            ru, en = get_random_word(user_obj['chat_id'])
        except:
            text = 'Перечень вариантов ответов пуст.'
            update.callback_query.message.reply_text(text)
            return

        text = f'Выберите правильный перевод слова "{en}"'
        
        with open('russian.txt', 'r', encoding='utf-8') as fp:
            all_lines = fp.readlines()

        word1 = random.choice(all_lines)
        word2 = random.choice(all_lines)
        word3 = random.choice(all_lines)

        keyboard = [
            [
                InlineKeyboardButton(f'{ru}', callback_data='a_1'),
            ], [
                InlineKeyboardButton(word1, callback_data='a_0'),
            ], [
                InlineKeyboardButton(word2, callback_data='a_0'),
            ], [
                InlineKeyboardButton(word3, callback_data='a_0'),
            ]
        ]
        random.shuffle(keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        #get_info(update, context)
        return

    if btn_data == '3':
        text = 'Выберите карточку для редактирования:'
        all_cards = get_user_carts(user_obj['chat_id'])
        keyboard = []
        for card in all_cards:
            cid = card[0]
            ru = card[1]
            en = card[2]
            keyboard.append([
                InlineKeyboardButton(f'{en} - {ru}', callback_data=f'e_{cid}'),
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        return

    if btn_data == '4':
        text = 'Выберите карточку для удаления:'
        all_cards = get_user_carts(user_obj['chat_id'])
        keyboard = []
        for card in all_cards:
            cid = card[0]
            ru = card[1]
            en = card[2]
            keyboard.append([
                InlineKeyboardButton(f'{en} - {ru}', callback_data=f'd_{cid}'),
            ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.reply_text(text, reply_markup=reply_markup)
        return

    if btn_data.startswith('e'):
        action, cid = btn_data.split('_')
        context.user_data['action'] = {'action': action, 'cid': cid}
        text = 'Введите вариант перевода. Формат english; русский :'
        update.callback_query.message.reply_text(text)
        return

    if btn_data.startswith('d'):
        action, cid = btn_data.split('_')
        delete_card(cid)
        text = 'Карточка успешно удалена.'
        get_info(update, context, text)
        return

    keyboard = [
        [
            InlineKeyboardButton('Добавить карточку', callback_data='1'),
        ], [
            InlineKeyboardButton('Сгенерировать карточку', callback_data='2'),
        ], [
            InlineKeyboardButton('Редактировать карточку', callback_data='3'),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.callback_query.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN
    )


def receive_eng_word(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    en = update.message.text
    en = str(en)
    en = en.strip()

    if not context.user_data.get('action'):
        return

    con = context.user_data.get('action')
    if con['action'] == 'e':
        try:
            en, ru = en.split(';')
            en = en.strip()
            ru = ru.strip()
        except:
            return
        cid = con['cid']
        change_card_translate(cid, en, ru)
        context.user_data['action'] = None
        text = f'Слово "{en}" и перевод "{ru}" изменено в БД.'
        get_info(update, context, text)    
        return

    if con['action'] == 'a':
        user_obj = get_user(update)
        ru = translate(en)
        add_word(user_obj['chat_id'], user_obj['username'], ru, en)
        text = f'Слово "{en}" и перевод "{ru}" добавлено в БД.'
        get_info(update, context, text)
        context.user_data['action'] = None


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN, workers=4)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler('start', get_info))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, receive_eng_word))
    
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
