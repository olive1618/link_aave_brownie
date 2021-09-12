from brownie import accounts, config, interface, network
from web3 import Web3


def main():
    my_wallet_address = accounts.add(config["wallets"]["from_key"])
    my_balance = my_wallet_address.balance()
    print(f'My wallet address: {my_wallet_address}')
    print(f'Account balance: {my_balance} in Wei')

    weth_wallet_addr = config["networks"][network.show_active()]["weth_token"]
    print(f'wETH Kovan wallet address: {weth_wallet_addr}')

    lending_pool = get_lending_pool()
    deposit_amount = Web3.toWei(0.001, "ether")
    print(f'Amount to deposit: {deposit_amount}')

    approve_erc20(deposit_amount, lending_pool.address, weth_wallet_addr, my_wallet_address)
    # lending_pool.deposit(
    #   weth_wallet_addr, deposit_amount, my_wallet_address.address, 0, {"from": my_wallet_address}
    # )

    borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, my_wallet_address)
    erc20_eth_price = get_asset_price()

    amount_erc20_to_borrow = (1 / erc20_eth_price) * (borrowable_eth * 0.95)
    print(f"Borrow {amount_erc20_to_borrow} DAI")
    # borrow_erc20(lending_pool, amount_erc20_to_borrow, my_wallet_address)

    # borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, my_wallet_address)
    # # amount_erc20_to_repay = (1 / erc20_eth_price) * (total_debt_eth * 0.95)
    # repay_all(amount_erc20_to_borrow, lending_pool, my_wallet_address)


def get_lending_pool():
    """Get the aave lending pool address
    """
    aave_lending_pool_addr_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["aave_lending_pool_addresses_provider"]
    )
    print(f'Address of the Aave lending pool address provider: {aave_lending_pool_addr_provider}')
    lending_pool_address = aave_lending_pool_addr_provider.getLendingPool()
    print(f'Address of the Aave lending pool: {lending_pool_address}')
    lending_pool = interface.ILendingPool(lending_pool_address)

    return lending_pool


def approve_erc20(amount, lending_pool_address, erc20_addr, my_acct_addr):
    """Check if provided wETH token is ERC20 compliant. Wait for confirmations
    """
    weth_wallet_addr = interface.IERC20(erc20_addr)
    print(f'wETH Kovan wallet address: {weth_wallet_addr}')

    tx_hash = weth_wallet_addr.approve(lending_pool_address, amount, {"from": my_acct_addr})
    confirmations_required = 3
    tx_hash.wait(confirmations_required)

    return True


def get_borrowable_data(lending_pool, account):
    """Check how much wETH is deposited with Aave, how much is currently borrowed and how much can
    be borrowed
    """
    (
        total_collateral_wei, total_debt_wei, available_borrow_wei, _, _, health_factor,
    ) = lending_pool.getUserAccountData(account.address)

    print(f'Borrower Aave health factor: {health_factor}')

    available_borrow_eth = Web3.fromWei(available_borrow_wei, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_wei, "ether")
    total_debt_eth = Web3.fromWei(total_debt_wei, "ether")
    print(f"{total_collateral_eth} worth of ETH is deposited")
    print(f"{total_debt_eth} worth of ETH is borrowed")
    print(f"{available_borrow_eth} worth of ETH can be borrowed")

    return (float(available_borrow_eth), float(total_debt_eth))


def get_asset_price():
    dai_eth_price_feed = interface.AggregatorV3Interface(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    latest_price = Web3.fromWei(dai_eth_price_feed.latestRoundData()[1], "ether")
    print(f"The DAI/ETH price is {latest_price}")

    return float(latest_price)


def borrow_erc20(lending_pool, borrow_amount, my_acct, erc20_address=None):
    """Borrow DAI on Aave. Stable interest rate is 1. Referral code is 0.
    """
    erc20_address = config["networks"][network.show_active()]["aave_dai_token"]

    transaction = lending_pool.borrow(
        erc20_address, Web3.toWei(borrow_amount, "ether"), 1, 0, my_acct.address, {"from": my_acct},
    )
    confirmations_required = 2
    transaction.wait(confirmations_required)
    print(f"{borrow_amount} DAI is borrowed")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["aave_dai_token"],
        account,
    )
    tx = lending_pool.repay(
        config["networks"][network.show_active()]["aave_dai_token"],
        Web3.toWei(amount, "ether"),
        1,
        account.address,
        {"from": account},
    )
    tx.wait(1)
    print("Repaid!")


if __name__ == "__main__":
    main()
