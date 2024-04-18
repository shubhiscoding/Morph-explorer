import requests
from dotenv import load_dotenv
import os
# Define your token
load_dotenv()
TOKEN = os.getenv('TOKEN')

# Function to get updates using long polling
def get_updates(offset=None, limit=100, timeout=0):
    url = f'https://api.telegram.org/bot{TOKEN}/getUpdates'
    params = {'offset': offset, 'limit': limit, 'timeout': timeout}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get('result', [])
    else:
        print(f"Failed to fetch updates. Status code: {response.status_code}")
        return []

# Function to send a message
def send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Failed to send message. Status code: {response.status_code}")

# Process updates
def process_updates(updates):
    for update in updates:
        # Extract chat_id and text from the update
        chat_id = update.get('message', {}).get('chat', {}).get('id')
        text = update.get('message', {}).get('text')

        # Handle each update based on your bot's logic
        if text == '/start':
            send_message(chat_id, "Welcome to Morph explorer run /help to get all commands")
        elif text.startswith('/TokenByAddress'):
            if text.startswith('/TokenByAddress '):
                send_message(chat_id, "Please wait, fetching data...")
                address = text.split('/TokenByAddress ')[1].strip()
                find_coin(address, chat_id)
        elif text.startswith('/TokenByName'):
            # Extract the coin name and type from the text
            if text.startswith('/TokenByName '):
                command_parts = text.split('/TokenByName ')[1].strip().split()
                # Check if both name and type are provided
                if len(command_parts) >= 2:
                    name = command_parts[0]
                    type = command_parts[1]
                    send_message(chat_id, "Please wait, fetching data...")
                    find_coin_By_Name(name, type, chat_id)
                else:
                    send_message(chat_id, "Please provide both the coin name and type. use /help for help")
            else:
                send_message(chat_id, "Please provide both the coin name and type. use /help for help")

        elif text.startswith('/WalletTransaction'):
            # Extract the coin address from the text
            if text.startswith('/WalletTransaction '):
                send_message(chat_id, "Please wait, fetching data...")
                address = text.split('/WalletTransaction ')[1].strip()
                get_transaction(address, chat_id)
            else:
                send_message(chat_id, "Please provide the address. use /help for help")

        # Handle each update based on your bot's logic
        elif text == '/help':
            help_command(chat_id)
        
        elif text == '/GasTracker':
            Gas_tracker(chat_id)
        
        elif text.startswith('/GetAllToken'):
            # Extract the coin address from the text
            if text.startswith('/GetAllToken '):  
                send_message(chat_id, "Please wait, fetching data...")  
                address = text.split('/GetAllToken ')[1].strip()
                all_token(address, chat_id)
            else:
                send_message(chat_id, "Please provide the address. use /help for help")

        elif text.startswith('/TokenTransaction'):
            if text.startswith('/TokenTransaction '):
                send_message(chat_id, "Please wait, fetching data...")
                address = text.split('/TokenTransaction ')[1].strip()
                tokenTransaction(address, chat_id)
            else:
                send_message(chat_id, "Please provide the address. use /help for help")
        
        elif text.startswith('/EthBalance'):
            if text.startswith('/EthBalance '):
                address = text.split('/EthBalance ')[1].strip()
                EthBalance(address, chat_id);
            else:
                send_message(chat_id, "Please provide the address. use /help for help")
        else:
            send_message(chat_id, "Invalid command. Please use /help to see all commands")
 
# Main function to continuously fetch and process updates
def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates:
            process_updates(updates)
            # Set the new offset to fetch only new updates next time
            offset = updates[-1]['update_id'] + 1

# Function to make API call to Morph API
def find_coin(address, chat_id):
    url = f'https://explorer-api-testnet.morphl2.io/api/v2/tokens/{address}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Extract relevant information from the response
        coin_info = (
            f"Coin info:\n"
            f"Name: {data.get('name')}\n"
            f"Symbol: {data.get('symbol')}\n"
            f"Token Type: {data.get('type')}\n"
            f"Exchange Rate: {data.get('exchange_rate')}\n"
            f"Decimals: {data.get('decimals')}\n"
            f"Total Supply: {data.get('total_supply')}\n"
            f"No.of Holders: {data.get('holders')}"
        )
        send_message(chat_id, coin_info)
    else:
        send_message(chat_id, "Failed to fetch coin information")


def find_coin_By_Name(name, type, chat_id):
    url = f'https://explorer-api-testnet.morphl2.io/api/v2/tokens/?q={name}&type={type}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            coins_info = "********-----List Of Tokens-----********\n\n"
            i = 0;
            for item in data['items']:
                i += 1
                if i >4:
                    break
                coin_info = (
                    f"Name: {item['name']}\n"
                    f"Symbol: {item['symbol']}\n"
                    f"Address: {item['address']}\n"
                    f"Decimals: {item['decimals']}\n"
                    f"Total Supply: {item['total_supply']}\n"
                    f"Exchange Rate: {item['exchange_rate']}\n"
                    f"No. of Holders: {item['holders']}\n\n"
                )
                coins_info += coin_info
            send_message(chat_id, coins_info)
        else:
            send_message(chat_id, "No tokens found for the provided criteria.")
    else:
        send_message(chat_id, "Failed to fetch token information. Please try again later.")


def Gas_tracker(chat_id):
    url = f'https://explorer-api-testnet.morphl2.io/api/v2/stats'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # Extract relevant information from the response
        gas_info = (
            f"Gas info:\n"
            f"Average Speed: {data.get('gas_prices').get('average')}Gwei\n"
            f"Fast Speed: {data.get('gas_prices').get('fast')}Gwei\n"
            f"Slow Speed: {data.get('gas_prices').get('slow')}Gwei"
        )
        send_message(chat_id, gas_info)
    else:
        send_message(chat_id, "Failed to fetch gas prices, check your connection and try again later")

def get_transaction(address, chat_id):
    url = f'https://explorer-api-testnet.morphl2.io/api/v2/addresses/{address}/transactions?filter=to%20%7C%20from'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            transaction_info, list = txns(data['items'], 4)
            send_message(chat_id, transaction_info)
        else:
            send_message(chat_id, "No transactions found for the provided address.")
    else:
        send_message(chat_id, "Failed to fetch transaction information. Please try again later.")

def EthBalance(address, chat_id):
    url = f'https://explorer-api-testnet.morphl2.io/api/v2/addresses/{address}/coin-balance-history-by-day'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            balance = data[len(data) - 1]['value']
            balance = int(balance)/10**18
            send_message(chat_id, f"Balance: {balance} Eth")

def txns(data, n):
    transaction_info = "********-----List Of Transactions-----********\n\n"
    i=0;
    list = [];
    for item in data:
        i += 1
        if i > n:
            break
        timestamp = item['timestamp']
        from_address = item['from']['hash']
        to_address = item['to']['hash']
        value = item['value']
        value = int(value)/ 10 ** 18
        transaction_details = (
            f"Timestamp: {timestamp}\n"
            f"From Address: {from_address}\n"
            f"To Address: {to_address}\n"
            f"Value: {value}\n\n"
        )
        list.append(item['hash'])
        transaction_info += transaction_details 
    return transaction_info, list

def all_token(address, chat_id):
    url = f'https://explorer-api-testnet.morphl2.io/api/v2/addresses/{address}/token-balances'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data:
            coins_info = "********-----List Of Tokens-----********\n\n"
            for item in data:
                value = (int(item['value']))/10**18
                if(value < 1):
                    value = round(value, 4)
                coin_info = (
                    f"Name: {item['token']['name']}\n"
                    f"Symbol: {item['token']['symbol']}\n"
                    f"Holding: {value} {item['token']['symbol']}\n\n"
                )
                coins_info += coin_info
            send_message(chat_id, coins_info)
        else:
            send_message(chat_id, "No tokens found for the provided criteria.")
    else:
        send_message(chat_id, "Failed to fetch token information. Please try again later.")


def tokenTransaction(address, chat_id):
    url = f'https://explorer-api-testnet.morphl2.io/api/v2/addresses/{address}/transactions?filter=to%20%7C%20from'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['items']:
            transaction_info, list = txns(data['items'], 20)
            transaction_details = "********-----Token Transfer Transaction (recent 5 only)-----********\n\n"
            i=0;
            if len(list) < 0:
                send_message(chat_id, "No recent token transfer transactions found for the provided address.")
            for item in list:
                url = f'https://explorer-api-testnet.morphl2.io/api/v2/transactions/{item}/token-transfers?type=ERC-20%2CERC-721%2CERC-1155'
                response = requests.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        if i >4:
                            break
                        if not data['items']:
                            continue
                        # print(data['items'][0])
                        smbl = data['items'][0]['token']['symbol']
                        from_address = data['items'][0]['from']['hash']
                        to_address = data['items'][0]['to']['hash']
                        type = data['items'][0]['type']
                        halfs = type.split('_')
                        half1 = ''
                        half2 = halfs[0]
                        transfertype = ''
                        if len(halfs) > 1:
                            half1 = halfs[1]
                            transfertype = half2 + ' ' + half1
                        else:
                            transfertype = half2
                        if(to_address != address):
                            from_address = address
                        value = data['items'][0]['total']['value']
                        value = int(value)/ 10 ** 18
                        if(value < 1):
                            value = round(value, 4)
                        transactions = (
                            f"From Address: {from_address}\n"
                            f"To Address: {to_address}\n"
                            f"Value: {value} {smbl}\n"
                            f"Type: {transfertype}\n\n"
                            f"Transaction Hash: {item}\n\n"
                        )
                        if(value > 0):
                            i += 1
                            transaction_details += transactions
                else:
                    send_message(chat_id, "Failed to fetch transaction information. Please try again later.")
            send_message(chat_id, transaction_details)
        else:
            send_message(chat_id, "No transactions found for the provided address.")
    else:
        send_message(chat_id, "Failed to fetch transaction information. Please try again later.")



# Function to handle the /help command
def help_command(chat_id):
    help_text = (
        "Welcome to Morph explorer\n"
        "Commands:\n"
        "/start: Start the bot\n"
        "/help: Get help\n"
        "/EthBalance <address>: Get Eth balance by address\n"
        "/GetAllToken <address>: Get all tokens by address\n"
        "/TokenTransaction <address>: Get token transactions by address\n"
        "/WalletTransaction <address>: Get transactions by address\n"
        "/TokenByAddress <address>: Get coin information by address\n"
        "/TokenByName <Name> <Type>: Get coin information by name and type (eg: /TokenByName USDT ERC-20)\n"
        "/GasTracker: Get gas prices\n"
    )
    send_message(chat_id, help_text)

if __name__ == '__main__':
    main()
