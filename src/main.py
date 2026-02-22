import argparse
import datetime
# from ws import WealthSimple
from ws import WealthSimple
from gf import Ghostfolio


def get_date_range(start_date, end_date):
    date_range = []
    current = start_date
    while current <= end_date:
        print("processing data for month: ",
              current.month, " and year: ", current.year)
        month_start = current
        # last day of current month
        if current.month == 12:
            month_end = datetime.date(
                current.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            month_end = datetime.date(
                current.year, current.month + 1, 1) - datetime.timedelta(days=1)
        # cap at end_date
        month_end = min(month_end, end_date)
        date_range.append((month_start, month_end))
        # advance to first day of next month
        if current.month == 12:
            current = datetime.date(current.year + 1, 1, 1)
        else:
            current = datetime.date(current.year, current.month + 1, 1)
    return date_range


def main():
    parser = argparse.ArgumentParser(description='Wealthsimple auto uploader')
    parser.add_argument('--start-date', type=lambda s: datetime.date.fromisoformat(s),
                        default=None, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--end-date', type=lambda s: datetime.date.fromisoformat(s),
                        default=None, help='End date in YYYY-MM-DD format')
    args = parser.parse_args()

    today = datetime.date.today()

    update_master_data = True
    count = 0

    from config import ws_user_accounts
    for ws_account in ws_user_accounts:
        count += 1
        print(
            f"processing request for id: {ws_account.get('username')} and iteration is {count}")
        wealth_simple = WealthSimple(ws_account)
        ws_accounts_list = wealth_simple.get_ws_accounts_list()

        if args.start_date is not None and args.end_date is not None:
            date_range = get_date_range(args.start_date, args.end_date)
            for month_start, month_end in date_range:
                wealth_simple.get_ws_data(
                    month_start.isoformat(), month_end.isoformat(), ws_accounts_list)
                print(
                    f"Completed processing data from {month_start} to {month_end}")
        else:
            today = datetime.datetime.today().date()
            wealth_simple.get_ws_data(today, today, ws_accounts_list)
            print(f"Completed processing data for today: {today}")

        raw_data = wealth_simple.get_raw_ws_data()

        wealth_simple.get_ws_security_exchange_data(
            raw_data=raw_data)

        ghostfolio = Ghostfolio()
        ghostfolio.schema_check()

        gf_accounts_list = ghostfolio.get_gf_accounts()

        if (gf_accounts_list is None) and update_master_data:
            ghostfolio.create_master_data(ws_accounts_list)
        elif (gf_accounts_list is not None) and update_master_data:
            ghostfolio.update_account_list(gf_accounts_list=gf_accounts_list,
                                           ws_accounts_list=ws_accounts_list)
        gf_accounts_list = ghostfolio.get_gf_accounts()

        ghostfolio.parse_ws_data(
            gf_accounts_list=gf_accounts_list, count=count, user_name=ws_account.get('username'))


main()
