from brownie import * 
import os
import sys
import random

from eth_utils import keccak

sys.path.append('./scripts')
from deploy import main

from dotenv import load_dotenv ##pipx install python-dotenv 
load_dotenv()


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

def test_deploy():
    main()
    
def test_add():
    lst = []
    for x in range(256):
        lst.append(random.getrandbits(256))
    tx = Random[-1].add(lst,{"from": mainaccount()})
    tx.wait(1)
    print(tx.events)
    gascost = (tx.gas_used+Random[-1].setCost.estimate_gas(0,0,{"from": mainaccount()}))*tx.gas_price
    Random[-1].setCost(gascost,256,{"from": mainaccount()})

def test_random1():
    tx = Random[-1].random(1,0,True,{"from": mainaccount()})
    print(tx.events)
    assert(len(tx.events['Randoms'])==1)
    assert(len(tx.events['Randoms'][0]['random'])==1)

def test_random10():
    tx = Random[-1].random(10,0,True,{"from": mainaccount()})
    assert(len(tx.events['Randoms'])==1)
    assert(len(tx.events['Randoms'][0]['random'])==10)

def test_freerandom1():
    r = Random[-1].freeRandom(1,0,{"from": mainaccount()})
    assert(len(r)==1)

def test_freerandom10():
    r = Random[-1].freeRandom(10,0,{"from": mainaccount()})
    assert(len(r)==10)
