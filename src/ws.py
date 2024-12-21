import os
import json
import requests
import time


class WealthSimple():

    def __init__(self):

        self.__tokens: dict = {
            'access_token': "",
            'refresh_token': ""
        }

        self.__data_file_name = 'data.json'
        self.__data_file_path = f"{os.getcwd()}/{self.__data_file_name}"

        self.__processed_data_file_name = 'processed-data.json'
        self.__processed_data_file_path = f"{os.getcwd()}/{self.__processed_data_file_name}"

        self.__headers: dict = {
            'accept': 'application/json',
            'accept-language': 'en-US,en;q=0.9',
            'origin': os.getenv('WS_WEB_URL'),
            'priority': 'u=1, i',
            'referer': os.getenv('WS_WEB_URL'),
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15',
            'x-wealthsimple-client': '@wealthsimple/wealthsimple',
            'x-wealthsimple-otp-claim': os.getenv('WS_OTP_CLAIM'),
            'x-ws-device-id': os.getenv('WS_DEVICE_ID'),
            'x-ws-profile': 'undefined',
            'x-ws-session-id': os.getenv('WS_USER_SESSION_ID')
        }

        self.__get_ws_token()

        payload = {
            "grant_type": "password",
            "username": os.getenv('USERNAME'),
            "password": os.getenv('PASSWORD'),
            "skip_provision": True,
            "scope": "invest.read invest.write trade.read trade.write tax.read tax.write",
            "client_id": os.getenv('CLIENT_ID')
        }

        response = requests.post(url=os.getenv(
            'WS_TOKEN_URL'), headers=self.__headers, data=payload)

        if response.status_code == 200:
            self.__tokens['access_token'] = response.json().get('access_token')
            self.__tokens['refresh_token'] = response.json().get(
                'refresh_token')

        else:
            print("error fetching tokens")
            exit()

        self.__modified_headers: dict = {
            "Authorization": f"Bearer {self.__tokens.get('access_token')}",
            "Content-Type": "application/json"
        }

    def get_ws_data(self, start_date: str, end_date: str):

        try:
            if (os.path.exists(self.__data_file_path)):
                os.remove(self.__data_file_path)
        except FileExistsError as e:
            print(e)

        query_payload = json.dumps({
            "operationName": "FetchActivityFeedItems",
            "variables": {
                "orderBy": "OCCURRED_AT_DESC",
                "condition": {
                    "accountIds": ["rrsp-XDoi7dq_ZA", "rrsp-Zc5TJ11raQ", "lira-HaPyL0c3Xg", "lira-eQrV4U3prw", "spousal-rrsp-RI6dAocqgQ", "tfsa-GYO7GFBttA", "tfsa-VNm_UCnRhQ", "resp-6uwrhI7DaQ", "non-registered-crypto-2Ctopceh8Q"],
                    "startDate": f"{start_date}T00:00:00.999Z",
                    "endDate": f"{end_date}T23:59:59.999Z"
                },
                "first": 50
            },
            "query": "query FetchActivityFeedItems($first: Int, $cursor: Cursor, $condition: ActivityCondition, $orderBy: [ActivitiesOrderBy!] = OCCURRED_AT_DESC) {\n  activityFeedItems(\n    first: $first\n    after: $cursor\n    condition: $condition\n    orderBy: $orderBy\n  ) {\n    edges {\n      node {\n        ...Activity\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment Activity on ActivityFeedItem {\n  accountId\n  aftOriginatorName\n  aftTransactionCategory\n  aftTransactionType\n  amount\n  amountSign\n  assetQuantity\n  assetSymbol\n  canonicalId\n  currency\n  eTransferEmail\n  eTransferName\n  externalCanonicalId\n  identityId\n  institutionName\n  occurredAt\n  p2pHandle\n  p2pMessage\n  spendMerchant\n  securityId\n  billPayCompanyName\n  billPayPayeeNickname\n  redactedExternalAccountNumber\n  opposingAccountId\n  status\n  subType\n  type\n  strikePrice\n  contractType\n  expiryDate\n  chequeNumber\n  provisionalCreditAmount\n  primaryBlocker\n  interestRate\n  frequency\n  counterAssetSymbol\n  rewardProgram\n  counterPartyCurrency\n  counterPartyCurrencyAmount\n  counterPartyName\n  fxRate\n  fees\n  reference\n  __typename\n}"
        })

        graph_response = requests.post(
            url=os.getenv('WS_GRAPH_URL'), headers=self.__modified_headers, data=query_payload)

        if graph_response.status_code == 200:
            list_of_transactions = graph_response.json().get('data').get(
                'activityFeedItems').get('edges')

            with open('data.json', 'w+') as file:
                json.dump(list_of_transactions, file)
                file.close()
        else:
            print(graph_response.status_code)

    # get wealthsimple security exchange data

    def get_ws_security_exchange_data(self, raw_data):
        try:
            if os.path.exists(self.__processed_data_file_path):
                os.remove(self.__processed_data_file_path)
        except FileExistsError as e:
            print(e)

        processed_data = []
        for order in raw_data.get('orders'):
            query_payload = json.dumps({
                "operationName": "FetchSecuritySearchResult",
                "variables": {
                    "query": f"{order.get('assetSymbol')}"
                },
                "query": "query FetchSecuritySearchResult($query: String!) {\n  securitySearch(input: {query: $query}) {\n    results {\n      ...SecuritySearchResult\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment SecuritySearchResult on Security {\n  id\n  buyable\n  status\n  stock {\n    symbol\n    name\n    primaryExchange\n    __typename\n  }\n  securityGroups {\n    id\n    name\n    __typename\n  }\n  quoteV2 {\n    ... on EquityQuote {\n      marketStatus\n      __typename\n    }\n    __typename\n  }\n  __typename\n}"
            })
            graph_response = requests.post(
                url=os.getenv('WS_GRAPH_URL'), headers=self.__modified_headers, data=query_payload)

            if graph_response.status_code == 200:
                stock_exchange = graph_response.json().get('data').get(
                    'securitySearch').get('results')[0].get('stock').get('primaryExchange')

                order['primary_exchange'] = stock_exchange
                processed_data.append(order)
                print(f"processed security symbol: {order.get('assetSymbol')}")
                time.sleep(2)
            else:
                print(graph_response.status_code)

        final_data = {
            "cash_transactions": raw_data.get('cash_transactions'),
            "orders": processed_data
        }

        with open(self.__processed_data_file_path, 'w+') as file:
            json.dump(final_data, file)

        file.close()
    # get wealthsimple accounts

    def get_ws_accounts(self):
        try:
            if os.path.exists(self.__data_file_path):
                with open(self.__data_file_path, 'r') as file:
                    parsed_json = json.load(file)
        except FileExistsError as e:
            print(e)
            exit()
        ws_accounts_list = []
        for item in parsed_json:
            ws_accounts_list.append(item.get('node').get('accountId'))

        ws_accounts_list = set(ws_accounts_list)

        return ws_accounts_list

    # process ws raw data
    def get_raw_ws_data(self):

        ghostfolio_datalist = []
        cash_updates = []

        if os.path.exists(self.__data_file_path):
            with open(self.__data_file_path, 'r') as file:
                parsed_json = json.load(file)

        for item in parsed_json:
            post_item: dict = {}
            if item.get('node').get('status') == 'FILLED' and item.get('node').get('type') == 'DIY_BUY':
                transaction_type = 'Buy'
            elif item.get('node').get('status') == None and item.get('node').get('type') == 'MANAGED_BUY':
                transaction_type = 'Buy'
            elif item.get('node').get('status') == 'FILLED' and item.get('node').get('type') == 'DIY_SELL':
                transaction_type = 'Sell'
            elif item.get('node').get('status') == None and item.get('node').get('type') == 'MANAGED_SELL':
                transaction_type = 'Sell'
            elif item.get('node').get('status') == 'posted' and item.get('node').get('type') == 'CRYPTO_BUY':
                transaction_type = 'Buy'
            elif item.get('node').get('status') == 'posted' and item.get('node').get('type') == 'CRYPTO_SELL':
                transaction_type = 'Sell'
            elif item.get('node').get('status') == None and item.get('node').get('type') == 'REFUND':
                cash_updates.append({
                    "account_name": item.get("node").get("accountId"),
                    "amount": float(item.get("node").get("amount"))
                })
                transaction_type = None
            elif item.get('node').get('status') == "completed" and item.get('node').get('type') == 'DEPOSIT':
                cash_updates.append({
                    "account_name": item.get("node").get("accountId"),
                    "amount": float(item.get("node").get("amount"))
                })
                transaction_type = None
            elif item.get('node').get('status') == "completed" and item.get('node').get('type') == 'INSTITUTIONAL_TRANSFER_INTENT':
                cash_updates.append({
                    "account_name": item.get("node").get("accountId"),
                    "amount": float(item.get("node").get("amount"))
                })
                transaction_type = None
            else:
                transaction_type = None

            if (transaction_type is not None):
                post_item = {
                    "accountId": item.get('node').get('accountId'),
                    "amount": item.get('node').get('amount'),
                    "assetQuantity": item.get('node').get('assetQuantity'),
                    "assetSymbol": item.get('node').get('assetSymbol'),
                    "transactionType": transaction_type,
                    "fxRate": item.get('node').get('fxRate'),
                    "date": item.get('node').get('occurredAt'),
                    "currency": item.get('node').get('currency')
                }

                ghostfolio_datalist.append(post_item)

        raw_data: dict = {
            "cash_transactions": cash_updates,
            "orders": ghostfolio_datalist
        }

        return raw_data
