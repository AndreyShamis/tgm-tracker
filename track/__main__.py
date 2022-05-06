# telegram-tracker
# Copyright (c) 2018 Maxim Mikityanskiy
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from cmath import log
import logging
from datetime import datetime
from sys import argv, exit
from time import mktime, sleep

import telethon.sync
from settings import API_HASH, API_ID
from telethon import TelegramClient
from telethon.tl.types import UserStatusOffline, UserStatusOnline

DATETIME_FORMAT = '%Y-%m-%d @ %H:%M:%S'


logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')


def utc2localtime(utc):
    pivot = mktime(utc.timetuple())
    offset = datetime.fromtimestamp(pivot) - datetime.utcfromtimestamp(pivot)
    return utc + offset


if len(argv) < 2:
    print(f'usage: {argv[0]} <contact id>')
    exit(1)


contact_id = argv[1]

client = TelegramClient('tracker', API_ID, API_HASH)
client.start()

online = None
last_offline = None
last_known_online = None

#bot_entity = client.get_input_entity(peer="ashamis_bot")

# logging.info(f'bot_entity:{bot_entity}')
while True:
    if contact_id in ['me', 'self']:
        # Workaround for the regression in Telethon that breaks get_entity('me'):
        # https://github.com/LonamiWebs/Telethon/issues/1024
        contact = client.get_me()
        print(f"here me")
    else:
        contact = client.get_entity(contact_id)
        # results = client.send_message(entity=bot_entity, message='aaaa')

    if isinstance(contact.status, UserStatusOffline):
        if online != False:
            online = False
            if last_known_online:
                logging.info(f'~{datetime.now().strftime(DATETIME_FORMAT)}: DISCONNECT. {datetime.now().timestamp()-last_known_online} sec')
                sleep(2)
            else:
                logging.info(f'={utc2localtime(contact.status.was_online).strftime(DATETIME_FORMAT)}: DISCONNECT.')
                sleep(5)
            last_known_online = None

        elif last_offline != contact.status.was_online:
            if last_offline is not None:
                print(f'={utc2localtime(contact.status.was_online).strftime(DATETIME_FORMAT)}: User went offline after being online for short time.')
            else:
                print(f'={utc2localtime(contact.status.was_online).strftime(DATETIME_FORMAT)}: User went offline.')
        else:
            sleep(5)
        last_offline = contact.status.was_online
    elif isinstance(contact.status, UserStatusOnline):
        if online != True:
            online = True
            logging.warning(f'~{datetime.now().strftime(DATETIME_FORMAT)}: CONNECT.')
            sleep(5)
            last_known_online = datetime.now().timestamp()
        else:
            sleep(5)
    else:
        if online != False:
            online = False
            if last_known_online:
                print(f'~{datetime.now().strftime(DATETIME_FORMAT)}: User went offline. {datetime.now().timestamp()-last_known_online}  sec')
            else:
                print(f'~{datetime.now().strftime(DATETIME_FORMAT)}: User went offline {last_known_online}')
            last_known_online = None
        else:
            sleep(2)

        last_offline = None
    sleep(5)
