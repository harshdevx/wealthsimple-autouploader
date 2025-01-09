import os
import requests
import json

class Telegram():

    def __init__(self):
        self.__telegram_bot_token: str = os.getenv('TELEGRAM_TOKEN')
        self.__telegram_chat_id: str = os.getenv('TELEGRAM_CHAT_ID')
        self.__telegram_api_url: str = os.getenv('TELEGRAM_API_URL')

    
    def send_message(self, message: str):
        
        url = f"{self.__telegram_api_url}/bot{self.__telegram_bot_token}/sendMessage?chat_id={self.__telegram_chat_id}&text={message}"
        response = requests.get(url=url)

        if response.status_code != 200:
            print('telegram api error...')
