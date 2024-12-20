import os
import json
import requests
import uuid


class Ghostfolio():

    def __init__(self):

        self.__token: str = ""

        self.__processed_data_file_name = 'processed-data.json'
        self.__processed_data_file_path = f"{os.getcwd()}/{self.__processed_data_file_name}"

        self.__map_file_name = 'map.json'
        self.__map_file_path = f"{os.getcwd()}/{self.__map_file_name}"

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
            "Content-Type": "application/json"
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
                "currency": "CAD",
                "id": item_uuid,
                "isExcluded": False,
                "name": item,
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
            if item not in gf_accounts_list.keys():
                item_uuid = str(uuid.uuid4()).lower()
                payload: dict = {
                    "balance": 0,
                    "comment": None,
                    "currency": "CAD",
                    "id": item_uuid,
                    "isExcluded": False,
                    "name": item,
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

    def parse_ws_data(self, gf_accounts_list):
        try:
            if os.path.exists(self.__processed_data_file_path):
                with open(self.__processed_data_file_path, 'r') as file:
                    processed_data = json.load(file)

            if os.path.exists(self.__map_file_path):
                with open(self.__map_file_path, 'r') as file:
                    map_data = json.load(file)

                # process all cash transactions
                if len(processed_data.get('cash_transactions')) > 0:
                    gf_accounts_list = self.get_gf_accounts()
                    for transaction in processed_data.get('cash_transactions'):
                        account = gf_accounts_list.get(
                            transaction.get('account_name'))
                        response = requests.get(
                            f"{os.getenv('GF_URL')}/account/{account.get('id')}", headers=self.__modified_header)
                        account_balance = response.json().get('balance')

                        account_balance = account_balance + \
                            transaction.get("amount")
                        payload: dict = {
                            "balance": account_balance,
                            "comment": None,
                            "currency": "CAD",
                            "id": account.get('id'),
                            "isExcluded": False,
                            "name": transaction.get('account_name'),
                            "platformId": account.get('platformId')
                        }
                        url = f"{os.getenv('GF_URL')}/account/{account.get('id')}"

                        # put_response = requests.put(url=url,
                        #                             headers=self.__modified_header, data=json.dumps(payload))
                    # process all orders
                if len(processed_data.get('orders')) > 0:
                    for order in processed_data.get('orders'):
                        account = gf_accounts_list.get(order.get('accountId'))

                        if (order.get('primary_exchange') is not None) and ((order.get('primary_exchange') not in map_data.get('markets').get('exclude'))) and (order.get('assetSymbol') != 'CASH'):
                            assetSymbol = f"{order.get('assetSymbol')}.{map_data.get('markets').get('include').get(order.get('primary_exchange'))}"
                        elif (order.get('primary_exchange') is not None) and ((order.get('primary_exchange') in map_data.get('markets').get('exclude'))) and (order.get('assetSymbol') != 'CASH'):
                            assetSymbol = order.get('assetSymbol')
                        elif (order.get('primary_exchange') == None) and (order.get('assetSymbol') == 'CASH'):
                            assetSymbol = map_data.get('symbols').get('CASH')

                        post_data: dict = {
                            "accountId": account.get('id'),
                            "comment": "",
                            "fee": 0,
                            "quantity": float(order.get('assetQuantity')),
                            "type": str(order.get('transactionType')).upper(),
                            "unitPrice": round(float(order.get('amount'))/float(order.get('assetQuantity')), 2),
                            "currency": order.get('currency'),
                            "dataSource": "YAHOO",
                            "date": order.get('date'),
                            "symbol": assetSymbol
                        }
                        response = requests.post(
                            url=f"{os.getenv('GF_URL')}/order", headers=self.__modified_header, data=json.dumps(post_data))
                        if response.status_code == 201:
                            print("ordered entered successfully...")
                        else:
                            print(response.json())
        except FileExistsError as e:
            print(e)
            exit()
