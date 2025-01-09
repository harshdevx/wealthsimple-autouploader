import os
import json
import requests
import time
import jwt
import datetime
from telegram import Telegram

class WealthSimple():

    def __init__(self, ws_user_account):

        self.__tokens: dict = {
            'access_token': "",
            'refresh_token': ""
        }

        self.__ws_user_account = ws_user_account

        self.__data_file_name = 'data.json'
        self.__data_file_path = f"{os.getcwd()}/{self.__data_file_name}"

        self.__processed_data_file_name = 'processed-data.json'
        self.__processed_data_file_path = f"{os.getcwd()}/{self.__processed_data_file_name}"

        self.__bot = Telegram()
        
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
            'x-wealthsimple-otp-claim': self.__ws_user_account.get('ws_otp_claim'),
            'x-ws-device-id': self.__ws_user_account.get('ws_device_id'),
            'x-ws-profile': 'undefined',
            'x-ws-session-id': self.__ws_user_account.get('ws_user_session_id')
        }

        self.__payload = {
            "grant_type": "password",
            "username": self.__ws_user_account.get('username'),
            "password": self.__ws_user_account.get('password'),
            "skip_provision": True,
            "scope": "invest.read invest.write trade.read trade.write tax.read tax.write",
            "client_id": self.__ws_user_account.get('client_id')
        }

        response = requests.post(url=os.getenv(
            'WS_TOKEN_URL'), headers=self.__headers, data=self.__payload)

        if response.status_code == 200:
            self.__tokens['access_token'] = response.json().get('access_token')
            self.__tokens['refresh_token'] = response.json().get(
                'refresh_token')
            
        else:
            today = str(datetime.datetime.today().date())
            self.__bot.send_message(f"{today} - wealthsimple getting access token failed for user: {self.__ws_user_account.get('username')}")
            exit()

        self.__modified_headers: dict = {
            "Authorization": f"Bearer {self.__tokens.get('access_token')}",
            "Content-Type": "application/json"
        }

    def get_ws_accounts_list(self):
        ws_accounts_list = []

        decoded_jwt = jwt.decode(jwt=self.__tokens.get('access_token'), key=None, options={"verify_signature": False})
        query_payload = json.dumps({
            "operationName": "FetchAllAccountFinancials",
            "variables": {
                "pageSize": 25,
                "identityId": decoded_jwt.get('sub')
            },
            "query": "query FetchAllAccountFinancials($identityId: ID!, $startDate: Date, $pageSize: Int = 25, $cursor: String) {\n  identity(id: $identityId) {\n    id\n    ...AllAccountFinancials\n    __typename\n  }\n}\n\nfragment AllAccountFinancials on Identity {\n  accounts(filter: {}, first: $pageSize, after: $cursor) {\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    edges {\n      cursor\n      node {\n        ...AccountWithFinancials\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment AccountWithFinancials on Account {\n  ...AccountWithLink\n  ...AccountFinancials\n  __typename\n}\n\nfragment AccountWithLink on Account {\n  ...Account\n  linkedAccount {\n    ...Account\n    __typename\n  }\n  __typename\n}\n\nfragment Account on Account {\n  ...AccountCore\n  custodianAccounts {\n    ...CustodianAccount\n    __typename\n  }\n  __typename\n}\n\nfragment AccountCore on Account {\n  id\n  archivedAt\n  branch\n  closedAt\n  createdAt\n  cacheExpiredAt\n  currency\n  requiredIdentityVerification\n  unifiedAccountType\n  supportedCurrencies\n  nickname\n  status\n  accountOwnerConfiguration\n  accountFeatures {\n    ...AccountFeature\n    __typename\n  }\n  accountOwners {\n    ...AccountOwner\n    __typename\n  }\n  type\n  __typename\n}\n\nfragment AccountFeature on AccountFeature {\n  name\n  enabled\n  __typename\n}\n\nfragment AccountOwner on AccountOwner {\n  accountId\n  identityId\n  accountNickname\n  clientCanonicalId\n  accountOpeningAgreementsSigned\n  name\n  email\n  ownershipType\n  activeInvitation {\n    ...AccountOwnerInvitation\n    __typename\n  }\n  sentInvitations {\n    ...AccountOwnerInvitation\n    __typename\n  }\n  __typename\n}\n\nfragment AccountOwnerInvitation on AccountOwnerInvitation {\n  id\n  createdAt\n  inviteeName\n  inviteeEmail\n  inviterName\n  inviterEmail\n  updatedAt\n  sentAt\n  status\n  __typename\n}\n\nfragment CustodianAccount on CustodianAccount {\n  id\n  branch\n  custodian\n  status\n  updatedAt\n  __typename\n}\n\nfragment AccountFinancials on Account {\n  id\n  custodianAccounts {\n    id\n    branch\n    financials {\n      current {\n        ...CustodianAccountCurrentFinancialValues\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  financials {\n    currentCombined {\n      id\n      ...AccountCurrentFinancials\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment CustodianAccountCurrentFinancialValues on CustodianAccountCurrentFinancialValues {\n  deposits {\n    ...Money\n    __typename\n  }\n  earnings {\n    ...Money\n    __typename\n  }\n  netDeposits {\n    ...Money\n    __typename\n  }\n  netLiquidationValue {\n    ...Money\n    __typename\n  }\n  withdrawals {\n    ...Money\n    __typename\n  }\n  __typename\n}\n\nfragment Money on Money {\n  amount\n  cents\n  currency\n  __typename\n}\n\nfragment AccountCurrentFinancials on AccountCurrentFinancials {\n  id\n  netLiquidationValue {\n    ...Money\n    __typename\n  }\n  netDeposits {\n    ...Money\n    __typename\n  }\n  simpleReturns(referenceDate: $startDate) {\n    ...SimpleReturns\n    __typename\n  }\n  totalDeposits {\n    ...Money\n    __typename\n  }\n  totalWithdrawals {\n    ...Money\n    __typename\n  }\n  __typename\n}\n\nfragment SimpleReturns on SimpleReturns {\n  amount {\n    ...Money\n    __typename\n  }\n  asOf\n  rate\n  referenceDate\n  __typename\n}"
        })

        accounts_response = requests.post(
            url=os.getenv('WS_GRAPH_URL'), headers=self.__modified_headers, data=query_payload)
        
        for item in accounts_response.json().get('data').get('identity').get('accounts').get('edges'):

            if item.get('node').get('status') == 'open':
                ws_accounts_list.append({"accountId": item.get('node').get('id'), "supportedCurrency": item.get('node').get('supportedCurrencies')[0]})
        return ws_accounts_list


    def get_ws_data(self, start_date: str, end_date: str, ws_account_list):

        ws_accounts = []

        try:
            if (os.path.exists(self.__data_file_path)):
                os.remove(self.__data_file_path)
        except FileExistsError as e:
            print(e)

        for item in ws_account_list:
            ws_accounts.append(item.get('accountId'))

        query_payload = json.dumps({
            "operationName": "FetchActivityFeedItems",
            "variables": {
                "orderBy": "OCCURRED_AT_ASC",
                "condition": {
                    "accountIds": ws_accounts,
                    "startDate": f"{start_date}T00:00:00.999Z",
                    "endDate": f"{end_date}T23:59:59.999Z"
                },
                "first": 100
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

        orders = []
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
                orders.append(order)
                print(f"processed security symbol: {order.get('assetSymbol')}")
                time.sleep(int(os.getenv('SLEEP_SECONDS')))
            else:
                print(graph_response.status_code)

        final_data = {
            "cash_transactions": raw_data.get('cash_transactions'),
            "orders": orders
        }

        with open(self.__processed_data_file_path, 'w+') as file:
            json.dump(final_data, file)

        file.close()
    
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
            elif item.get('node').get('status') is None and item.get('node').get('type') == 'DIVIDEND':
                transaction_type = 'Dividend'
                post_item = {
                    "accountId": item.get('node').get('accountId'),
                    "amount": item.get('node').get('amount'),
                    "assetQuantity": None,
                    "assetSymbol": item.get('node').get('assetSymbol'),
                    "transactionType": transaction_type,
                    "fxRate": item.get('node').get('fxRate'),
                    "date": item.get('node').get('occurredAt'),
                    "currency": item.get('node').get('currency')
                }
            else:
                transaction_type = None

            if (transaction_type is not None):
                post_item = {
                    "accountId": item.get('node').get('accountId'),
                    "amount": item.get('node').get('amount'),
                    "assetQuantity": item.get('node').get('assetQuantity') if item.get('node').get('assetQuantity') is not None else 0.00,
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
