import json
from operator import truediv
import random
from web3 import Web3,IPCProvider,middleware
##from web3.auto.gethdev import w3
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.time_based import medium_gas_price_strategy
from web3.gas_strategies.rpc import rpc_gas_price_strategy
from eth_keys import keys
import time
from requests.exceptions import ConnectionError
import json
from eth_account import Account
import os
import sys
from dotenv import load_dotenv ##pipx install python-dotenv  
from decimal import Decimal

print(f"starting...")
load_dotenv()

poa = True
minrandombuffer = 256*16

PRIVATE_KEY = os.getenv("BOT_PKEY")
account = Account.from_key(PRIVATE_KEY)
print(f"account.address :               {account.address}")
print(f"\n")


def setCost(gas,count):
    nonce = web3.eth.get_transaction_count(account.address)
    txn = Random.functions.setCost(gas,count).buildTransaction({
        'chainId': web3.eth.chain_id,
        'gasPrice': web3.eth.generate_gas_price() ,
        'from': account.address,
        'nonce': nonce,

        })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)  
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt


def add():
    lst = []
    for x in range(256):
        lst.append(random.getrandbits(256))
    nonce = web3.eth.get_transaction_count(account.address)

    txn = Random.functions.add(lst).buildTransaction({
        'chainId': web3.eth.chain_id,
        'gasPrice': web3.eth.generate_gas_price() ,
        'from': account.address,
        'nonce': nonce,
        })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)  
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Random added")
    return tx_receipt




while True:
    try:
        web3 = Web3() ##Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))     
        ##if poa:
        ##web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        web3.eth.default_account = account.address
        web3.eth.set_gas_price_strategy(rpc_gas_price_strategy)

        ##web3.middleware_onion.add(middleware.time_based_cache_middleware)
        ##web3.middleware_onion.add(middleware.latest_block_based_cache_middleware)
        ##web3.middleware_onion.add(middleware.simple_cache_middleware)

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


        mapjsonfilename = 'build/deployments/map.json'
        mapjson = json.load(open(mapjsonfilename))
        RandomAddress = mapjson[str(web3.eth.chain_id)]['Random'][0]

        RandomJSON = json.load(open('build/contracts/Random.json'))
        Random = web3.eth.contract(address=RandomAddress, abi=RandomJSON['abi'])

        print(f"Random Address :        {RandomAddress}")
        print(f"Random Owner :          {Random.functions.ownerOf().call()}")
        print(f"\n")

        startbalance = Decimal(web3.eth.get_balance(web3.eth.default_account))/10**18
        startscbalance = Decimal(web3.eth.get_balance(RandomAddress))/10**18
        startfee = Random.functions.fee().call()

        gasSetCost = Random.functions.setCost(0,0).estimateGas({"from": account.address})
        print(f"gas setCost :      {Decimal(gasSetCost)}")            

        margin = Random.functions.margin().call()
        print(f"margin :                {Decimal(margin)}")            

        if Random.functions.fee().call() == 0:
            tx_receipt = add()
            print(f"gasUsed :               {Decimal(tx_receipt.gasUsed)}")            
            print(f"gasPrice :              {Decimal(tx_receipt.effectiveGasPrice)}")            
            setCost((tx_receipt.gasUsed+gasSetCost)*tx_receipt.effectiveGasPrice,256)
            print(f"Random Fee :            {Decimal(Random.functions.fee().call())/10**18}")            

        count = Random.functions.count().call()
        added = 0
        feeadded = 0
        while (count+added<minrandombuffer):
            print(f"count :                 {count+added}")
            tx_receipt = add()
            added+=256
            print(f"gasUsed :               {Decimal(tx_receipt.gasUsed)}")            
            print(f"gasPrice :              {Decimal(tx_receipt.effectiveGasPrice)}")            
            feeadded +=(tx_receipt.gasUsed+gasSetCost)*tx_receipt.effectiveGasPrice
        if added>0:
            setCost(feeadded,added)

        endfee = Random.functions.fee().call()
        print(f"Random Start Fee :      {Decimal(startfee)/10**18}({startfee})")            
        print(f"Random Fee :            {Decimal(endfee)/10**18}({endfee})")            
        print(f"Random Fee Delta :      {(Decimal(endfee)-Decimal(startfee))}")            
        endbalance = Decimal(web3.eth.get_balance(web3.eth.default_account))/10**18
        endscbalance = Decimal(web3.eth.get_balance(RandomAddress))/10**18
        deltabalance = endbalance-startbalance
        deltascbalance = endscbalance-startscbalance
        print(f"init balance={endbalance} endscbalance={endscbalance} deltabalance={deltabalance} deltascbalance={deltascbalance}")

        Remaining_filter = Random.events.Remaining.createFilter(fromBlock='latest')
        Reset_filter = Random.events.Reset.createFilter(fromBlock='latest')
        lastgasused = 0
        while (True):
            #for event in Reset_filter.get_new_entries():
            #    count = event.args.count
            #    print(f"RandomReset({count})")
            #for event in Remaining_filter.get_new_entries():
            #    count = event.args.count
            #    print(f"RandomRemaining({count})")
            count = Random.functions.count().call()
            if count<minrandombuffer:
                startbalance = Decimal(web3.eth.get_balance(web3.eth.default_account))/10**18
                startscbalance = Decimal(web3.eth.get_balance(RandomAddress))/10**18
                startfee = Random.functions.fee().call()
                
                added = 0
                feeadded = 0
                while (count+added<minrandombuffer):
                    print(f"count :                 {count+added}")

                    lst = []
                    for x in range(256):
                        lst.append(random.getrandbits(256))

                    estimateGas = Random.functions.add(lst).estimateGas()
                    print(f"estimateGas :           {Decimal(estimateGas)}")     

                    tx_receipt = add()
                    ##print(tx_receipt)
                    added+=256
                    print(f"gasUsed :               {Decimal(tx_receipt.gasUsed)}")     
                    print(f"gasUsed Delta :         {Decimal(tx_receipt.gasUsed)-lastgasused}")     

                    lastgasused = Decimal(tx_receipt.gasUsed)
                    print(f"gasPrice :              {Decimal(tx_receipt.effectiveGasPrice)}")            
                    feeadded +=(tx_receipt.gasUsed+gasSetCost)*tx_receipt.effectiveGasPrice
                if added>0:
                    setCost(feeadded,added)
                    endfee = Random.functions.fee().call()
                    endaddedgascost = Random.functions.addedgascost().call()
                    endaddedcount = Random.functions.addedcount().call()
                    print(f"addedgascost :    {Decimal(endaddedgascost)}")     
                    print(f"addedcount :      {Decimal(endaddedcount)}")     
                    print(f"feeadded :              {feeadded}")            
                    print(f"added :                 {added}")            
                    print(f"just added Ratio :  -------------->    {Decimal(feeadded)/added}")     
                    print(f"added Ratio :       -------------->    {Decimal(endaddedgascost)/endaddedcount}")     
                    ##print(f"addedgascost Delta :    {(Decimal(endaddedgascost)-Decimal(startaddedgascost))}")            
                    ##print(f"addedcount Delta :      {(Decimal(endaddedcount)-Decimal(startaddedcount))}")   
                    ##calculatedfee = Decimal(endaddedgascost)*margin/endaddedcount/10**18
                    ##print(f"calculatedfee :         {Decimal(calculatedfee)/10**18}({calculatedfee})")            
                    print(f"Random Start Fee :      {Decimal(startfee)/10**18}({startfee})")            
                    print(f"Random End Fee :        {Decimal(endfee)/10**18}({endfee})")            
                    print(f"Random Fee Delta :      {(Decimal(endfee)-Decimal(startfee))}")            

                endbalance = Decimal(web3.eth.get_balance(web3.eth.default_account))/10**18
                endscbalance = Decimal(web3.eth.get_balance(RandomAddress))/10**18
                deltabalance = endbalance-startbalance
                deltascbalance = endscbalance-startscbalance
                print(f"balance={endbalance} endscbalance={endscbalance} deltabalance={deltabalance} deltascbalance={deltascbalance}")
            sys.stdout.flush()
            time.sleep(0.1)
                   
    except KeyboardInterrupt:
        raise
    finally:
        pass



