from calendar import c
import json
from operator import truediv
import random
from web3 import Web3,IPCProvider,middleware
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from eth_keys import keys
import time
from requests.exceptions import ConnectionError
import json
from eth_account import Account
import os
from dotenv import load_dotenv ##pipx install python-dotenv  
from decimal import Decimal

load_dotenv()


PRIVATE_KEY = os.getenv("EXTRA_PKEY")
account = Account.from_key(PRIVATE_KEY)
print(f"account.address :               {account.address}")
print(f"\n")

def get(count,fee):
    nonce = web3.eth.get_transaction_count(account.address)
    txn = Random.functions.random(count,0,True).buildTransaction({
        'chainId': web3.eth.chain_id,
        'gasPrice': web3.eth.generate_gas_price() ,
        'from': account.address,
        'nonce': nonce,
        'value': int(fee*1.5*count),
        })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)  
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"requested {count} random sentfee={int(fee*1.5*count)/10**18} fee={int(fee*count)/10**18} totalcost={(tx_receipt.gasUsed*tx_receipt.effectiveGasPrice)/10**18+int(fee*count)/10**18}")
    return tx_receipt


while True:
    try:
        web3 = Web3() ##Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))     
        ##if poa:
        web3.eth.default_account = account.address
        web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)

        print(f"\n")
        print(f"api :                   {web3.api}")
        print(f"clientVersion :         {web3.clientVersion}")
        print(f"\n")

        print(f"chainid :               {web3.eth.chain_id}")
        print(f"gasPrice :              {web3.eth.gasPrice}")
        print(f"generate_gas_price :    {web3.eth.generate_gas_price()}")
        print(f"coinbase :              {web3.eth.coinbase}")
        print(f"hashrate :              {web3.eth.hashrate}")
        print(f"syncing :               {web3.eth.syncing}")
        print(f"accounts :              {web3.eth.accounts}")
        print(f"block_number :          {web3.eth.block_number}")
        ##print(f"protocol_version :      {web3.eth.protocol_version}")
        print(f"mining :                {web3.eth.mining}")
        print(f"\n")

        print(f"net.peer_count :        {web3.net.peer_count}")
        print(f"net.version :           {web3.net.version}")
        print(f"net.listening :         {web3.net.listening}")
        print(f"\n")

        mygasPrice=web3.eth.gasPrice

        mapjsonfilename = 'build/deployments/map.json'
        mapjson = json.load(open(mapjsonfilename))
        RandomAddress = mapjson[str(web3.eth.chain_id)]['Random'][0]

        RandomJSON = json.load(open('build/contracts/Random.json'))
        Random = web3.eth.contract(address=RandomAddress, abi=RandomJSON['abi'])

        print(f"Random Address :        {RandomAddress}")
        print(f"\n")

        Randoms_filter = Random.events.Randoms.createFilter(fromBlock='latest')
        Remaining_filter = Random.events.Remaining.createFilter(fromBlock='latest')
        Reset_filter = Random.events.Reset.createFilter(fromBlock='latest')
        Fee_filter = Random.events.Fee.createFilter(fromBlock='latest')

        fee = Random.functions.fee().call()
        print(f"Random fee :        {fee}")

        while True:
            ##balance = web3.eth.get_balance(web3.eth.default_account)
            ##print(f"Balance :           {Decimal(balance)/10**18}")
            mygasPrice=int(web3.eth.gasPrice*1.1)

            if True: ##(balance > fee*1.1*64):
                startbalance = Decimal(web3.eth.get_balance(web3.eth.default_account))/10**18
                tx_receipt = get(256,fee)
                endbalance = Decimal(web3.eth.get_balance(web3.eth.default_account))/10**18
                deltabalance = endbalance-startbalance
                print(f"balance={endbalance} deltabalance={deltabalance}")

                
                #print(f"tx.events={tx_receipt}")
                for event in Randoms_filter.get_new_entries():
                    print(f"Randoms:    {event.args.random}")
                    pass
                for event in Remaining_filter.get_new_entries():
                    count = event.args.count
                    print(f"Remaining:  {count}")
                for event in Reset_filter.get_new_entries():
                    count = event.args.count
                    print(f"Reset:  {count}")
                for event in Fee_filter.get_new_entries():
                    fee = event.args.fee
                    print(f"Fee:        {fee}")


            print(f"\n")
            time.sleep(0.1)
    except KeyboardInterrupt:
        raise
    except:
        raise

        time.sleep(5)

