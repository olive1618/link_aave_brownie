from brownie import accounts, config, network, interface


def main():
    """
    Runs the get_weth function to get WETH
    """
    get_weth()


def get_weth(account=None):
    """Mints WETH by depositing ETH."""
    print(f'Active network: {network.show_active()}')

    my_wallet_address = (account if account else accounts.add(config["wallets"]["from_key"]))
    my_balance = my_wallet_address.balance()
    print(f'My wallet address: {my_wallet_address}')
    print(f'Account balance: {my_balance} in Wei')
    print(f'Gas paid: {my_wallet_address.gas_used}')

    weth_wallet_addr = config["networks"][network.show_active()]["weth_token"]
    print(f'wETH Kovan wallet address: {weth_wallet_addr}')

    contract_interface = interface.WethInterface(weth_wallet_addr)
    trade_amt = (my_balance / 2.) * .9
    print(f'Trade {trade_amt} Wei')
    tx = contract_interface.deposit({"from": my_wallet_address, "value": trade_amt})

    return tx
