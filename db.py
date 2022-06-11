import random
import logging

import psycopg2

import conf


connection = psycopg2.connect(
    database='dfktgad9g6meiq', 
    user='irfqalupfywlyt', 
    password='fdf71cf2cd640e094d3eff18a7db3d741948f5a44e2f0fb83d056aad192b675c', 
    host='ec2-52-212-228-71.eu-west-1.compute.amazonaws.com', 
    port='5432'
)

logging.warning('Database opened successfully')
connection.autocommit = True
cursor = connection.cursor()


def add_word(user_id, username, ru, en):
    cursor.execute("""SELECT id FROM tguser WHERE chat_id LIKE '%s';""", (user_id, ))
    output = cursor.fetchall()
    if len(output) == 0:
        # создаем пользователя
        cursor.execute("INSERT INTO tguser (chat_id, name) VALUES(%s, %s)", (user_id, username, ))
        connection.commit()

    cursor.execute("""SELECT id FROM tguser WHERE chat_id = '%s';""", (user_id, ))
    user_id = cursor.fetchall()[0][0]
    
    cursor.execute("""SELECT tguser_id, en FROM card WHERE (tguser_id = '%s') AND (en ILIKE %s);""", (user_id, en))
    output = cursor.fetchall()
    
    if len(output) == 0:
        cursor.execute("""INSERT INTO card (tguser_id, ru, en) VALUES(%s, %s, %s)""", (user_id, ru, en, ))
        connection.commit()
        logging.warning('Слово и перевод успешно добавлено.')
    else:
        logging.warning('Слово и перевод уже есть в БД.')
    return True


def get_random_word(chat_id):
    cursor.execute("""SELECT id FROM tguser WHERE chat_id = '%s';""", (chat_id, ))
    user_id = cursor.fetchall()[0][0]
    cursor.execute("""SELECT tguser_id, ru, en FROM card WHERE tguser_id = '%s' ORDER BY id ASC;""", (user_id, ))
    output = cursor.fetchall()
    user_id, ru, en  = random.choice(output)
    return ru, en


def get_user_carts(chat_id):
    cursor.execute("""SELECT id FROM tguser WHERE chat_id = '%s';""", (chat_id, ))
    try:
        user_id = cursor.fetchall()[0][0]
    except:
        return []
    cursor.execute("""SELECT id, ru, en FROM card WHERE tguser_id = '%s' ORDER BY id ASC;""", (user_id, ))
    output = cursor.fetchall()
    return output


def change_card_translate(cid, en, ru):
    cursor.execute("""UPDATE card SET en=%s, ru=%s WHERE id=%s;""", (en, ru, cid, ))
    return True


def delete_card(cid):
    cursor.execute("""DELETE FROM card WHERE id=%s;""", (cid, ))
    return True



def _init_db():
    with open('createdb.sql', 'r') as f:
        sql = f.read()
    cursor.execute(sql)
    connection.commit()
    logging.warning('Tables created successfully')


if __name__ == '__main__':
    _init_db()
    #o = change_card_translate(5, 'xxx', 'yyy')
    #print('o=', o)
