import datetime
from dotenv import load_dotenv, find_dotenv
from ws import WealthSimple
from gf import Ghostfolio


def main():
    load_dotenv(find_dotenv())

    update_master_data = True

    wealth_simple = WealthSimple()
    ghostfolio = Ghostfolio()
    today = str(datetime.datetime.today().date())
    wealth_simple.get_ws_data(today, today)

    ws_accounts_list = wealth_simple.get_ws_accounts()
    raw_data = wealth_simple.get_raw_ws_data()

    wealth_simple.get_ws_security_exchange_data(
        raw_data=raw_data)

    gf_accounts_list = ghostfolio.get_gf_accounts()

    if (gf_accounts_list is None) and update_master_data:
        ghostfolio.create_master_data(ws_accounts_list)
        gf_accounts_list = ghostfolio.get_gf_accounts()
    elif (gf_accounts_list is not None) and update_master_data:
        ghostfolio.update_account_list(gf_accounts_list=gf_accounts_list,
                                       ws_accounts_list=ws_accounts_list)
        gf_accounts_list = ghostfolio.get_gf_accounts()
    ghostfolio.parse_ws_data(gf_accounts_list=gf_accounts_list)


main()
