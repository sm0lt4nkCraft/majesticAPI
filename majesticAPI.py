"""MajesticAPI - CLI helper for Majestic Bank API 
by sm0lt4ntCraft
"""
import argparse
import json
import re
import requests
import tabulate

    
class MajesticAPI:
    """
    Simple wrapper for Majestic Bank API. 
    Most of it's endpoints are covered. 
    All requests goes via tor proxy.
    """
    def __init__(self):
        """Constructor method."""
        self.API_LINK = "https://www.majesticbank.de/api/v1/"
        self.tor_proxies = {
            "http": "socks5://127.0.0.1:9150",
            "https": "socks5://127.0.0.1:9150"
        } 
        self.basic = self.basic_info()


    def basic_info(self) -> dict:
        """Get basic information about rates and limits.
    
        :return: Available pairs with price and limit for each currency as min/max dict.
        :rtype: dict
        """
        # Make request.
        try:
            response = requests.get("{}{}".format(self.API_LINK, "rates"), proxies=self.tor_proxies)
            if response.status_code == 200:
                return json.loads(response.text)
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)


    def check(self, pairs: list) -> None:
        """Check user's input validity.
        
        :param pairs: Sequence of: [to_crypto: str, from_amount: numeric, to_currency: str, to_amount: numeric].
        :type pairs: list
        :raise: If paris are not availavle or limit has been exceeded.
        """ 
        # Gather basic information.
        data = {}

        f = pairs[0].upper()
        t = pairs[2].upper()
        pair = f"{f}-{t}"
        
        # Check if pairs availavle.
        if pair in self.basic.keys():
            data.update({"price": (self.basic[pair], t)})
            data.update({"lim": {
                f: self.basic["limits"][f], 
                t: self.basic["limits"][t]
                }})
        else:
            raise SystemExit("Invalid transaction pair.")
        
        # Check limits.
        for x in [pairs[:2], pairs[2:]]:
            if x[1] > 0:
                lim_dict = data["lim"][x[0].upper()]
                if not lim_dict["min"] < x[1] < lim_dict["max"]:
                    print(f"Limits for {x[0]} (min/max): ", lim_dict["min"], lim_dict["max"])
                    raise SystemExit("Transaction limit error.")
        

    def calculate_fee(self, pairs: list) -> dict:
        """Calculate fee for given transaction's parameter.
       
        :param pairs: Sequence of: [to_crypto: str, from_amount: numeric, to_currency: str, to_amount: numeric]. 
        :type pairs: list
        :return: Basic information about fee.
        :rtype: dict
        """ 
        self.check(pairs)

        # Gather basic information.
        params = {}
        params.update({"from_currency": pairs[0], "receive_currency": pairs[2]})

        if pairs[1] > 0 and pairs[3] > 0:
            params.update({"from_amount": pairs[1], "receive_amount": pairs[3]})
        else:
            vector = "from_amount" if pairs[1] > 0 else "receive_amount"
            amount = pairs[1] if vector == "from_amount" else pairs[3]
            params.update({vector: amount})
      
        # Make request.
        try:
            response = requests.post("{}{}".format(self.API_LINK, "calculate"), params=params, proxies=self.tor_proxies)
            if response.ok:
                return json.loads(response.text)
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

        
    def create_order(self, order_data: list) -> dict:
        """Place an order (swap coins).

        :param order_data: Sequence of: [to_crypto: str, from_amount: numeric, to_currency: str, wallet: str]. 
        :type order_data: list
        :return: Confirmation with order data (including TRX needed to track order).
        :rtype: dict
        """
        pairs = order_data.copy()
        pairs[3] = 0
        self.check(pairs) 

        # Gather basic information.
        params = {
            "from_amount": order_data[1],
            "from_currency": order_data[0],
            "receive_currency": order_data[2],
            "receive_address": order_data[3],
            "referral_code": "86iGfJ"
        }
        
        # Make request.
        try:
            response = requests.get("{}{}".format(self.API_LINK, "exchange"), params=params, proxies=self.tor_proxies)
            if response.ok:
                print(response.status_code, response.text)
                return json.loads(response.text)
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)


    def track_order(self, order_id: str) -> dict:
        """Track order by ID (TRX).

        :param order_id: Transaction ID called TRX.
        :type order_id: str
        :return: Information about transaction.
        :rtype: dict
        """
        # Make request.
        try:
            response = requests.get("{}{}".format(self.API_LINK, "track"), params={"trx": order_id}, proxies=self.tor_proxies)
            if response.ok:
                return json.loads(response.text)
            else:
                response.raise_for_status() 
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)


if __name__ == "__main__":
    # CLI help
    prog = "MajesticAPI - CLI helper for Majestic Bank API by sm0lt4ntCraft"
    description = "Simple wrapper for Majestic Bank API. Most of it's endpoints are covered. All requests goes via tor proxy." 
    epilog = "TRX = transction ID."
    basic_help = "Get basic data about rates, limits and available pairs."
    limit_help = "Narrow basic infomation. Params: both sequence of currency symbol and pairs are valid"
    calc_help = "Calculate fee. Params: from_symbol from_amount to_symbol to_amount. Set one amount to zero to make it optional."
    order_help = "Place an orer. Params: form_sybmol from_amount to_symbol wallet"
    status_help = "Get data about order. Params: order_id"
    
    # Parser.
    parser = argparse.ArgumentParser(prog=prog, description=description, epilog=epilog)
    parser.add_argument("--basic", help=basic_help)
    parser.add_argument("--limit", nargs="+", help=limit_help)
    parser.add_argument("--calc", nargs="+", help=calc_help)
    parser.add_argument("--order", nargs="+", help=order_help)
    parser.add_argument("--status", help=status_help)
    args = parser.parse_args()

    # Init class.
    mapi = MajesticAPI()

    # Schow basic information.
    if args.basic:
        basic = mapi.basic   
        rates = [[b, basic[b]] for b in basic if b != "limits"] 
        limits = [[l, basic["limits"][l]["min"], basic["limits"][l]["max"]] for l in basic["limits"]]
       
        # Narrow results.
        if args.limit:
            rates = [r for r in rates if r[0] in args.limit]
            limits = [l for l in limits if l[0] in [r[0] for r in rates]]

        print("\n", "RATES", "\n", tabulate.tabulate(rates, tablefmt="github")) 
        print("\n", "LIMITS", "\n", tabulate.tabulate(limits, tablefmt="github"))

    # Calcucate fees.
    if args.calc:
        if len(args.calc) == 4:
            to_calc = [c if re.search("[A-Z]+", c) else float(c) for c in args.calc]
            calc = mapi.calculate_fee(to_calc)
            print(tabulate.tabulate([[c, calc[c]] for c in calc], tablefmt="github"))
        else:
            raise SystemExit(f"Wrong arguments number. {calc_help}")
        
    # Place an order
    if args.order:
        if len(args.order) == 4:
            to_order =[c if re.search("[A-Z]+|[a-z]+", c) else float(c) for c in args.order]
            order = mapi.create_order(to_order)
            print_table([[o, order[o]] for o in order])
        else:
            raise SystemExit(f"Worng arguments number. {order_help}")

    # Check order status.
    if args.status:
        if len(args.status) == 1:
            status = mapi.track_order(args.status)
            print_table([[s, status[s]] for s in status])
        else:
            raise SystemExit(f"Wrong arguments number. {status_help}")
    
