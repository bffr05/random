# Random

A solution attempt to try to provide random number service to smartcontracts.

The idea is to inject Randoms to the contract thru a bot. The bots inserts 256 Random at a time, the bots gets transfer fees for inserting, and update the cost of fees per random number.
The user request randoms and must send enought msg.value for random it wants to get.


## Client API
    - function fee() public view returns (uint256)
        returns the msg.value you have to pay for each random, if you request multiple randoms, you must pya multiple fees
    - function random( uint256 count_, uint256 random_, bool event_ ) public payable returns (uint256[] memory out_)
        request randoms. 
        count_ is the number of random you request 
        random_ is a random initialiser for more complex random generator, can be any number, address, or previous random value
        event_ if you cant a event Randoms(uint256[] random) to be generated
        return is the randoms you requested
    - function freeRandom( uint256 count_, uint256 random_) public view returns (uint256[] memory out_)
        request random for free, the generator used previously generated randoms and the randoms_ to provide you a random.
        the random depends on the random_ argument.
        this is partially effective as random but its free and can be used for testing purpose (witout having to pay fees)
        

## Random.sol
    basic random smart contract 
## xRandom.sol
    advanced random smart contract inherited from Random.sol


## Scripts
    deploy.py is the deploy script for brownie. Deploy script deploys the xRandom contract that is the random advanced contract compared to Random Contract.
        run: brownie run scripts/deploy.py
    bot.py is a python sample script to run a bot inserting random to smartcontract
        run: python3 bot.py
    user.py is a python sample script to run a client requesting randoms
        run: python3 user.py

