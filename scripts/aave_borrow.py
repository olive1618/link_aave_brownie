from brownie import accounts, config, interface, network
from web3 import Web3

from scripts.get_weth import get_weth




def main():
    my_wallet_address = accounts.add(config["wallets"]["from_key"])
    my_balance = my_wallet_address.balance()
    print(f'My wallet address: {my_wallet_address}')
    print(f'Account balance: {my_balance} in Wei')

    weth_wallet_addr = config["networks"][network.show_active()]["weth_token"]
    print(f'wETH Kovan wallet address: {weth_wallet_addr}')

    lending_pool = get_lending_pool()
    amount = Web3.toWei(0.01, "ether")
    print(f'Amount to borrow: {amount}')

    approve_erc20(amount, lending_pool.address, weth_wallet_addr, my_wallet_address)

    # print("Depositing...")
    # lending_pool.deposit(weth_wallet_addr, amount, my_wallet_address.address, 0, {"from": my_wallet_address})
    # print("Deposited!")
    # borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, my_wallet_address)
    # print(f"LETS BORROW IT ALL")
    # erc20_eth_price = get_asset_price()
    # amount_erc20_to_borrow = (1 / erc20_eth_price) * (borrowable_eth * 0.95)
    # print(f"We are going to borrow {amount_erc20_to_borrow} DAI")
    # borrow_erc20(lending_pool, amount_erc20_to_borrow, my_wallet_address)

    # borrowable_eth, total_debt_eth = get_borrowable_data(lending_pool, my_wallet_address)
    # # amount_erc20_to_repay = (1 / erc20_eth_price) * (total_debt_eth * 0.95)
    # repay_all(amount_erc20_to_borrow, lending_pool, my_wallet_address)


def get_lending_pool():
    """Get the 
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
    """Check if Aave protocol approves provided wETH token as ERC20 compliant
    """
    print("Approving ERC20...")
    erc20 = interface.IERC20(erc20_addr)
    tx_hash = erc20.approve(lending_pool_address, amount, {"from": my_acct_addr})
    tx_hash.wait(1)
    print("Approved!")
    return True


def get_borrowable_data(lending_pool, account):
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        tlv,
        health_factor,
    ) = lending_pool.getUserAccountData(account.address)
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"You have {total_collateral_eth} worth of ETH deposited.")
    print(f"You have {total_debt_eth} worth of ETH borrowed.")
    print(f"You can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def borrow_erc20(lending_pool, amount, account, erc20_address=None):
    erc20_address = (
        erc20_address
        if erc20_address
        else config["networks"][network.show_active()]["aave_dai_token"]
    )
    # 1 is stable interest rate
    # 0 is the referral code
    transaction = lending_pool.borrow(
        erc20_address,
        Web3.toWei(amount, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    transaction.wait(1)
    print(f"Congratulations! We have just borrowed {amount}")


def get_asset_price():
    # For mainnet we can just do:
    # return Contract(f"{pair}.data.eth").latestAnswer() / 1e8
    dai_eth_price_feed = interface.AggregatorV3Interface(
        config["networks"][network.show_active()]["dai_eth_price_feed"]
    )
    latest_price = Web3.fromWei(dai_eth_price_feed.latestRoundData()[1], "ether")
    print(f"The DAI/ETH price is {latest_price}")
    return float(latest_price)


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
