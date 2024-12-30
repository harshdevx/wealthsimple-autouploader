import os
import json
import requests
import uuid
import datetime
import hashlib
import time


class Ghostfolio():

    def __init__(self):

        self.__token: str = ""

        self.__processed_data_file_name = 'processed-data.json'
        self.__processed_data_file_path = f"{os.getcwd()}/{self.__processed_data_file_name}"

        self.__map_file_name = 'map.json'
        self.__map_file_path = f"{os.getcwd()}/{self.__map_file_name}"

        self.__order_hash_list = []
        self.__dividends_hash_list = []
        self.__order_hash_file_name = 'order_hash.json'
        self.__order_hash_file_path = f"{os.getcwd()}/{self.__order_hash_file_name}"

        gf_token_payload = json.dumps(
            {"accessToken": os.getenv('GF_USER_TOKEN')})
        gf_token_header: dict = {
            'Content-Type': 'application/json'
        }

        gf_token_response = requests.post(
            url=f"{os.getenv('GF_URL')}/auth/anonymous", headers=gf_token_header, data=gf_token_payload)
        self.__token = gf_token_response.json().get('authToken')

        self.__modified_header: dict = {
            "Authorization": f"Bearer {self.__token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"
        }

    def get_gf_accounts(self):

        gf_accounts_list = {}
        response = requests.get(
            url=f"{os.getenv('GF_URL')}/account", headers=self.__modified_header)

        if response.status_code == 200:
            for item in response.json().get('accounts'):
                gf_accounts_list.update({
                    item.get('name'): {
                        "id": item.get('id'),
                        "platformId": item.get('platformId')
                    }
                })

        if len(gf_accounts_list) > 0:
            return gf_accounts_list
        else:
            return None

    def create_master_data(self, ws_accounts_list):
        print("creating accounts in ghostfolio....")

        for item in ws_accounts_list:
            item_uuid = str(uuid.uuid4()).lower()
            payload: dict = {
                "balance": 0,
                "comment": None,
                "currency": item.get('supportedCurrency'),
                "id": item_uuid,
                "isExcluded": False,
                "name": item.get('accountId'),
                "platformId": "34fec028-e9ae-4d73-b6c6-09d018418754"
            }

            response = requests.post(
                url=f"{os.getenv('GF_URL')}/account", headers=self.__modified_header, data=json.dumps(payload))

            if response.status_code == 201:
                print(f"account {payload.get('name')} created successfully...")
            else:
                print(response.json())

        print("finished creating accounts in ghostfolio....")

    def update_account_list(self, gf_accounts_list, ws_accounts_list):

        print("updating accounts in ghostfolio....")
        for item in ws_accounts_list:
            if item.get('accountId') not in gf_accounts_list.keys():
                item_uuid = str(uuid.uuid4()).lower()
                payload: dict = {
                    "balance": 0,
                    "comment": None,
                    "currency": item.get('supportedCurrency'),
                    "id": item_uuid,
                    "isExcluded": False,
                    "name": item.get('accountId'),
                    "platformId": "34fec028-e9ae-4d73-b6c6-09d018418754"
                }

                response = requests.post(
                    url=f"{os.getenv('GF_URL')}/account", headers=self.__modified_header, data=json.dumps(payload))

                if response.status_code == 201:
                    print(
                        f"account {payload.get('name')} created successfully...")
                else:
                    print(response.json())
            else:
                print(
                    f"checked item and found: {item} therefore not making changes...")
        print("finished updating accounts in ghostfolio....")

    def parse_ws_data(self, gf_accounts_list, count):
        try:
            if os.path.exists(self.__processed_data_file_path):
                with open(self.__processed_data_file_path, 'r') as file:
                    processed_data = json.load(file)
                file.close()

            if os.path.exists(self.__map_file_path):
                with open(self.__map_file_path, 'r') as file:
                    map_data = json.load(file)
                file.close()

            processed_records = 1
            total_records = len(processed_data.get('orders'))

            # process all orders
            if len(processed_data.get('orders')) > 0:
                for order in processed_data.get('orders'):
                    account = gf_accounts_list.get(
                        order.get('accountId'))
                    data_source = "YAHOO"
                    if (order.get('primary_exchange') is not None) and ((order.get('primary_exchange') not in map_data.get('markets').get('exclude'))) and (order.get('assetSymbol') != 'CASH'):
                        assetSymbol = f"{order.get('assetSymbol')}.{map_data.get('markets').get('include').get(order.get('primary_exchange'))}"
                    elif (order.get('primary_exchange') is not None) and ((order.get('primary_exchange') in map_data.get('markets').get('exclude'))) and (order.get('assetSymbol') != 'CASH'):
                        assetSymbol = order.get('assetSymbol')
                    elif (order.get('primary_exchange') == None) and (order.get('assetSymbol') == 'CASH'):
                        assetSymbol = map_data.get(
                            'symbols').get('CASH')
                    elif (order.get('primary_exchange') == None) and (order.get('assetSymbol') == 'DOGE'):
                        assetSymbol = map_data.get(
                            'symbols').get('DOGE')
                        data_source = "COINGECKO"

                    lookup_response = requests.get(
                        url=f"{os.getenv('GF_URL')}/symbol/lookup?query={assetSymbol}", headers=self.__modified_header)

                    # symbol lookup to get right currency for processing dividends
                    if lookup_response.status_code == 200:
                        symbols_list = lookup_response.json().get('items')
                    for item in symbols_list:
                        if item.get('symbol') == assetSymbol:
                            currency = item.get('currency')
                            assetSymbol = item.get('symbol')

                    # check if its dividend or regular order
                    if str(order.get('transactionType')).upper() != 'DIVIDEND':
                        post_data: dict = {
                            "accountId": account.get('id'),
                            "comment": "",
                            "fee": 0,
                            "quantity": float(order.get('assetQuantity')),
                            "type": str(order.get('transactionType')).upper(),
                            "unitPrice": round(float(order.get('amount'))/float(order.get('assetQuantity')), 2),
                            "currency": currency,
                            "dataSource": data_source,
                            "date": order.get('date'),
                            "symbol": assetSymbol
                        }

                        order_hash = hashlib.sha1(json.dumps(
                            post_data).encode('utf-8')).hexdigest()

                        if (count == 1):
                            if (order_hash not in self.__order_hash_list):
                                response = requests.post(
                                    url=f"{os.getenv('GF_URL')}/order", headers=self.__modified_header, data=json.dumps(post_data))
                                if response.status_code == 201:
                                    print(
                                        f"order/dividend {processed_records} of {total_records} entered successfully...")
                                    self.__order_hash_list.append(order_hash)
                                else:
                                    print(response.json())
                        else:
                            try:
                                if os.path.exists(self.__order_hash_file_path):
                                    with open(self.__order_hash_file_path, 'r+') as file:
                                        final_hashes_list = json.load(
                                            file)
                                    file.close()

                                    self.__order_hash_list = final_hashes_list.get(
                                        'order_hashes')
                                    if (order_hash not in self.__order_hash_list):
                                        response = requests.post(
                                            url=f"{os.getenv('GF_URL')}/order", headers=self.__modified_header, data=json.dumps(post_data))
                                        if response.status_code == 201:
                                            print(
                                                f"order/dividend {processed_records} of {total_records} entered successfully...")
                                            self.__order_hash_list.append(
                                                order_hash)
                                        else:
                                            print(response.json())
                                    else:
                                        print(
                                            "data matched for this record therefore not processing...")
                            except FileExistsError as e:
                                print(e)

                    # process dividend
                    else:

                        url = f"{os.getenv('GF_URL')}/import/dividends/{data_source}/{assetSymbol}"
                        dividend_response = requests.get(
                            url=url, headers=self.__modified_header)

                        if (dividend_response.status_code == 200):
                            post_data: dict = {
                                "accounts": [],
                                "activities": [{
                                    "accountId": account.get('id'),
                                    "comment": "",
                                    "fee": 0,
                                    "quantity": dividend_response.json().get('activities')[
                                        0].get('quantity'),
                                    "type": "DIVIDEND",
                                    "unitPrice": dividend_response.json().get('activities')[
                                        0].get('unitPrice'),
                                    "currency": currency,
                                    "dataSource": data_source,
                                    "date": order.get('date'),
                                    "symbol": assetSymbol
                                }]
                            }

                        order_hash = hashlib.sha1(json.dumps(
                            post_data).encode('utf-8')).hexdigest()

                        if (count == 1):
                            if (order_hash not in self.__dividends_hash_list):
                                response = requests.post(
                                    url=f"{os.getenv('GF_URL')}/import?dryRun=false", headers=self.__modified_header, data=json.dumps(post_data))
                                if response.status_code == 201:
                                    print(
                                        f"order/dividend {processed_records} of {total_records} entered successfully...")
                                    self.__dividends_hash_list.append(
                                        order_hash)
                                else:
                                    print(response.json())
                        else:
                            try:
                                if os.path.exists(self.__order_hash_file_path):
                                    with open(self.__order_hash_file_path, 'r+') as file:
                                        final_hashes_list = json.load(
                                            file)
                                    file.close()

                                    self.__dividends_hash_list = final_hashes_list.get(
                                        'dividend_hashes')
                                    if (order_hash not in self.__dividends_hash_list):
                                        response = requests.post(
                                            url=f"{os.getenv('GF_URL')}/order", headers=self.__modified_header, data=json.dumps(post_data))
                                        if response.status_code == 201:
                                            print(
                                                f"order/dividend {processed_records} of {total_records} entered successfully...")
                                            self.__dividends_hash_list.append(
                                                order_hash)
                                        else:
                                            print(response.json())
                                    else:
                                        print(
                                            "data matched for this record therefore not processing...")
                            except FileExistsError as e:
                                print(e)
                    processed_records += 1
                    time.sleep(int(os.getenv('SLEEP_SECONDS')))

                final_hashes_list = {
                    "order_hashes": self.__order_hash_list,
                    "dividend_hashes": self.__dividends_hash_list
                }
                with open(self.__order_hash_file_path, 'a+') as file:
                    json.dump(final_hashes_list, file)
                file.close()

            today = str(datetime.datetime.today().date())
            message: str = f"ghostfolio updated for date: {today}"
            url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage?chat_id={os.getenv('TELEGRAM_CHAT_ID')}&text={message}"
            requests.get(url).json()
        except ZeroDivisionError as e:
            print(e)

        except FileExistsError as e:
            print(e)
            today = str(datetime.datetime.today().date())
            message: str = f"could not run ghostfolio update: {today}"
            url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}/sendMessage?chat_id={os.getenv('TELEGRAM_CHAT_ID')}&text={message}"
            requests.get(url).json()

            exit()

    def delete_order_hashes(self):
        print("deleting order hashes...")

        try:
            if os.path.exists(self.__order_hash_file_path):
                os.remove(self.__order_hash_file_path)

        except FileExistsError as e:
            print(e)
        print("deleted order hashes....")
