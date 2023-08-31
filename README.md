
## CLASS: MajesticAPI
 ```
 Simple wrapper for Majestic Bank API. 
Most of it's endpoints are covered. 
All requests goes via tor proxy. 
``` 



#### FUNC: __init__
 ```
 Constructor method. 
``` 


#### FUNC: basic_info
 ```
 Get basic information about rates and limits.

:return: Available pairs with price and limit for each currency as min/max dict.
:rtype: dict 
``` 


#### FUNC: calculate_fee
 ```
 Calculate fee for given transaction's parameter.

:param pairs: Sequence of: [to_crypto: str, from_amount: numeric, to_currency: str, to_amount: numeric]. 
:type pairs: list
:return: Basic information about fee.
:rtype: dict 
``` 


#### FUNC: check
 ```
 Check user's input validity.

:param pairs: Sequence of: [to_crypto: str, from_amount: numeric, to_currency: str, to_amount: numeric].
:type pairs: list
:raise: If paris are not availavle or limit has been exceeded. 
``` 


#### FUNC: create_order
 ```
 Place an order (swap coins).

:param order_data: Sequence of: [to_crypto: str, from_amount: numeric, to_currency: str, wallet: str]. 
:type order_data: list
:return: Confirmation with order data (including TRX needed to track order).
:rtype: dict 
``` 


#### FUNC: track_order
 ```
 Track order by ID (TRX).

:param order_id: Transaction ID called TRX.
:type order_id: str
:return: Information about transaction.
:rtype: dict 
``` 

### CLI
```
  -h, --help            show this help message and exit
  --basic BASIC         Get basic data about rates, limits and available pairs.
  --limit LIMIT [LIMIT ...]
                        Narrow basic infomation. Params: both sequence of
                        currency symbol and pairs are valid
  --calc CALC [CALC ...]
                        Calculate fee. Params: from_symbol from_amount
                        to_symbol to_amount. Set one amount to zero to make it optional.
  --order ORDER [ORDER ...]
                        Place an orer. Params: form_sybmol from_amount to_symbol wallet
  --status STATUS       Get data about order. Params: order_id

TRX = transction ID.
```
