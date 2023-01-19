from brownie import * 
from brownie.convert.datatypes import EthAddress 
import os
import json
import yaml
import time

##from sha3 import keccak_256 ## pipx install pysha3
from dotenv import load_dotenv ##pipx install python-dotenv 

load_dotenv()

def brownie_project(tag):
    with open("brownie-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        for entry in config_dict["dependencies"]:
            if tag in entry:
                return  project.load(entry)
    return project.main

def updatemapjson( network, title, address):
    open("./build/deployments/map.json", "a+")
    with open("./build/deployments/map.json", "r+") as map_json:
        map_json.seek(0)
        try:
            data = json.load(map_json)
        except:
            data = json.loads("{}")
        list = []
        if data.get(network) is None:
            data[network] = dict()
        if not data[network].get(title) is None:
            list = data[network][title]
            if list[len(list)-1] == address:
                return
        ##if list[-1]!=address:
        list.append(address)
        data[network][title] = list
        map_json.seek(0)
        map_json.write(json.dumps(data,sort_keys=True,indent=2))


def find_network(chainid):
    with open("network-config.json", "r") as network_config:
        data = json.load(network_config)
        for entry in data["live"]:
            for network in entry["networks"]:
                print(network)
                if network["chainid"] == chainid:
                    return network["host"]

def export_network():
    print(f"\nExporting network")
    with open("network-config.yaml", "r") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)
        with open("network-config.json", "w") as brownie_config_json:
            json.dump(config_dict, brownie_config_json,sort_keys=True,indent=2)

def supply(accountfrom,account,amount):
    if account.balance() < amount:
        accountfrom.transfer(account,amount-account.balance()).wait(1)



EthAddress0 = EthAddress("0x0000000000000000000000000000000000000000")

def mainaccount():
    if network.show_active() in {"development", "ganache"}:
        return accounts[0]
    else:
        return accounts.add(os.getenv("MAIN_PKEY"))

def extraaccount():
    if network.show_active() in {"development", "ganache"}:
        return accounts[1]
    else:
        return accounts.add(os.getenv("EXTRA_PKEY"))

def botaccount():
    if network.show_active() in {"development", "ganache"}:
        return accounts[2]
    else:
        return accounts.add(os.getenv("BOT_PKEY"))

def supply(accountfrom,account,amount):
    if account.balance() < amount:
        accountfrom.transfer(account,amount-account.balance()).wait(1)
    assert(account.balance() >= amount)


LocatorAddress = EthAddress("0x455b153B592d4411dCf5129643123639dcF3c806")
mycontracts = brownie_project("bffr05/contracts")
kAccess = network.web3.keccak(bytes("Access", 'ascii'))
kRandom = network.web3.keccak(bytes("Random", 'ascii'))

def main():
    supply(mainaccount(),extraaccount(),5*10**18)
    supply(mainaccount(),botaccount(),1*10**18)
    export_network()
    myLocator = LocatorAddress
    nolocator = (len(network.web3.eth.get_code(myLocator)) == 0)

    if nolocator and len(mycontracts.Locator) > 0:
        myLocator = mycontracts.Locator[-1].address
    if nolocator:
        mycontracts.Locator.deploy({"from": mainaccount()})
        myLocator = mycontracts.Locator[-1].address
    print(f"LocatorAddress = {myLocator}")
    print(f"nolocator = {nolocator}")
    print(f"len = {len(network.web3.eth.get_code(myLocator))}")

    updatemapjson(str(network.web3.chain_id),"Locator",myLocator)
    print()

    ILocator = mycontracts.interface.ILocator(myLocator)

    TestAccess = True

    if True: ##len(Access) ==0 or ILocator.get(kAccess) != Access[-1]:
        addr = mycontracts.Access.deploy({"from": mainaccount()})
        ILocator.set(kAccess,addr,{"from": mainaccount()})

        if nolocator:
            addr.setLocator(myLocator,{"from": mainaccount()}) ## mycontracts.addr.setLocator(myLocator,{"from": mainaccount()})
            assert(addr.locator()==myLocator)
        else:
            assert(addr.locator()==LocatorAddress)

        if TestAccess:
            addr.setOperator(LocatorAddress,True,{"from": mainaccount()})
            assert(addr.isOperator(mainaccount(),LocatorAddress))
    updatemapjson(str(network.web3.chain_id),"Access",ILocator.get['bytes32'](kAccess))

    if True: ##len(Random) ==0 or ILocator.get(kRandom) != Random[-1]:
        addr = Random.deploy({"from": mainaccount()})
        ILocator.set(kRandom,addr,{"from": mainaccount()})
        ##isTrusted
        if nolocator:
            addr.setLocator(myLocator,{"from": mainaccount()}) ## mycontracts.addr.setLocator(myLocator,{"from": mainaccount()})
            assert(addr.locator()==myLocator)
        else:
            assert(addr.locator()==LocatorAddress)

        assert(addr.referral()==ILocator.location(kAccess))
        if TestAccess:
            assert(not addr.isOperator(mainaccount(),LocatorAddress))
            addr.setOperator(LocatorAddress,True,{"from": mainaccount()})
            assert(addr.isOperator(mainaccount(),LocatorAddress))
            addr.setOperator(LocatorAddress,False,{"from": mainaccount()})
            assert(not addr.isOperator(mainaccount(),LocatorAddress))

        interface.IRTrustable(ILocator.location(kAccess)).setContract(addr,True,{"from": mainaccount()}) ## mycontracts.interface.IRTrustable(ILocator.location(ILocator.hash("Access"))).setContract(addr,True,{"from": mainaccount()})

        if TestAccess:
            assert(addr.isOperator(mainaccount(),LocatorAddress))
    updatemapjson(str(network.web3.chain_id),"Random",ILocator.get['bytes32'](kRandom))


    if True: ##len(xRandom) ==0 or ILocator.get(kRandom) != xRandom[-1]:
        addr = xRandom.deploy({"from": mainaccount()})
        ILocator.set(kRandom,addr,{"from": mainaccount()})
        ##isTrusted
        if nolocator:
            addr.setLocator(myLocator,{"from": mainaccount()}) ## mycontracts.addr.setLocator(myLocator,{"from": mainaccount()})
            assert(addr.locator()==myLocator)
        else:
            assert(addr.locator()==LocatorAddress)

        assert(addr.referral()==ILocator.location(kAccess))

        if TestAccess:
            assert(not addr.isOperator(mainaccount(),LocatorAddress))
            addr.setOperator(LocatorAddress,True,{"from": mainaccount()})
            assert(addr.isOperator(mainaccount(),LocatorAddress))
            addr.setOperator(LocatorAddress,False,{"from": mainaccount()})
            assert(not addr.isOperator(mainaccount(),LocatorAddress))

        interface.IRTrustable(ILocator.location(kAccess)).setContract(addr,True,{"from": mainaccount()}) ## mycontracts.interface.IRTrustable(ILocator.location(ILocator.hash("Access"))).setContract(addr,True,{"from": mainaccount()})

        if TestAccess:
            assert(addr.isOperator(mainaccount(),LocatorAddress))
    updatemapjson(str(network.web3.chain_id),"xRandom",ILocator.get['bytes32'](kRandom))

    time.sleep(0.5)