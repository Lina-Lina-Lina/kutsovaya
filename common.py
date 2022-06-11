import logging
import urllib

import requests

import conf


def get_user(update):
    if update.message:
        message = update.message
    else:
        message = update.callback_query.message

    try:
        username = message['chat']['username'].lower().strip()
        chat_id = message['chat']['id']
    except Exception as e:
        logging.error(f'Ошибка в строке 24 echobot.py: {e}.')
        return
    return {'username': username, 'chat_id': chat_id}


def _exit(m, r):
    r = f'Сервис похоже забанил переводчика. Переводимая строка "{m}", результат "{r}"'
    logging.warning(r)


def translate(en):
    en = en.replace('\n', '')
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/5341 (KHTML, like Gecko) Chrome/36.0.855.0 Mobile Safari/5341'}
    url = "https://translate.googleapis.com/translate_a/single"

    a1 = 'en'
    a2 = 'ru'
    a3 = 'ru'
    a4 = urllib.parse.quote(en)

    query = f"client=gtx&ie=UTF-8&oe=UTF-8&dt=bd&dt=ex&dt=ld&dt=md&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=qc&sl={a1}&tl={a2}&hl={a3}&q={a4}"

    try:
        r = requests.get(url + '?' + query, headers=headers)
        if r.status_code == 200:
            output = r.json()
            tmp = ''
            for item in output[0]:
                if item[0]:
                    tmp = tmp + item[0]

            return tmp
        else:
            # Логгируем исключение.
            _exit(mes, r.status_code)

    except Exception:
        # Логгируем исключение.
        _exit(mes, r.status_code)


if __name__ == '__main__':
    en = 'Appartment'
    ru = translate(en)
    print('ru=', ru)
