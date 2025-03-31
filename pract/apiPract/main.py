import requests
from flask import Flask, request, jsonify
from web3 import Web3

app = Flask(__name__)

# API ключ
POLYGONSCAN_API_KEY = 'ТОКЕН'

# Подключаемся к сети Polygon
polygon_url = "https://polygon-rpc.com"
web3 = Web3(Web3.HTTPProvider(polygon_url))

# Адрес токена и его ABI
token_address = web3.to_checksum_address('')
# Стандартный ABI нашел на гитхабе
token_abi = [
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]

token_contract = web3.eth.contract(address=token_address, abi=token_abi)



@app.route('/get_balanceOf', methods=['GET'])
def get_balance():
    # получаем адреса из JSON-запроса
    address = request.args.get('address')
    if address is None:
        return jsonify({'error': 'Address parameter is required'}), 400

    try:
        # Преобразуем адрес в формат с контрольной суммой
        checksum_address = web3.to_checksum_address(address)

        balance = token_contract.functions.balanceOf(checksum_address).call()
        return jsonify({'balance': Web3.from_wei(balance, 'ether')})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/get_balance_batch', methods=['POST'])
def get_balance_batch():
    try:
        # получаем адреса из JSON-запроса
        addresses = request.json.get('addresses')

        # Проверка на наличие адресов и их тип
        if not addresses or not isinstance(addresses, list):
            return jsonify({'error': 'Invalid input'}), 400

        balances = []

        for addr in addresses:
            try:
                # Преобразуем адрес в формат с контрольной суммой
                checksum_address = web3.to_checksum_address(addr)

                # Получаем баланс для адреса
                balance = token_contract.functions.balanceOf(checksum_address).call()
                balances.append(web3.from_wei(balance, 'ether'))
            except Exception as e:
                # Если произошла ошибка для конкретного адреса, добавляем сообщение об ошибке
                balances.append({'address': addr, 'error': str(e)})

        return jsonify({"balances": balances})

    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500


@app.route('/get_token_info', methods=['GET'])
def get_token_info():
    try:
        name = token_contract.functions.name().call()
        symbol = token_contract.functions.symbol().call()
        total_supply = token_contract.functions.totalSupply().call()
        return jsonify({
            "symbol": symbol,
            "name": name,
            "totalSupply": web3.from_wei(total_supply, 'ether')
        })
    except Exception as e:
        return jsonify({'error': 'an error occured:' + str(e)}), 500


@app.route('/get_top', methods=['GET'])
def get_top():
    n = int(request.args.get('n', 10))  # Получаем количество адресов, по умолчанию 10
    try:
        # Получаем топовые адреса по балансам токена
        url = f'https://api.polygonscan.com/api?module=account&action=tokenbalance&contractaddress={token_address}&apikey={POLYGONSCAN_API_KEY}'
        response = requests.get(url)
        data = response.json()

        # Проверям ответ
        if data['status'] == '0':
            return jsonify({'error': data['message']}), 400

        balances = data['result']
        top_addresses = sorted(balances, key=lambda x: x[1], reverse=True)[:n]
        return jsonify(top_addresses)
    except Exception as e:
        return jsonify({'error': "an error occured" + str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
