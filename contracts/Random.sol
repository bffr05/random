// SPDX-License-Identifier: MIT
// Beef MarketPlace Contracts v0.0.0 hello@mcdu.com

pragma solidity ^0.8.0;

import "@openzeppelin/contracts/utils/introspection/IERC165.sol";
import "@bffr05/contracts/access/Operatorable.sol";


interface IRandom {
    event Randoms(uint256[] random);
    event Remaining(uint256 count);
    event Reset(uint256 count);
    event Fee(uint256 fee);

    function fee() external view returns (uint256);
    function count() external view returns (uint256);
    function random( uint256 count_, uint256 random_, bool event_ ) external payable returns (uint256[] memory out_);
    function freeRandom( uint256 count_, uint256 random_) external view returns (uint256[] memory out_);
}

interface RIRandom {
    function resetFee() external;
    function purgeAll() external;
    function collectFund() external;
    function setCost(uint256 gascost_, uint256 count_) external;
    function add(uint256[256] calldata newrandoms_) external;
}

contract Random is IERC165,Operatorable,IRandom,RIRandom {
    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    //          supportsInterface
    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    function supportsInterface(bytes4 interfaceId)
        public
        view
        virtual
        override(Operatorable, IERC165)
        returns (bool)
    {
        return
            Operatorable.supportsInterface(interfaceId) ||
            interfaceId == type(IRandom).interfaceId||
            interfaceId == type(RIRandom).interfaceId;
    }

    uint256 public immutable margin = 1.05 * 10**18;
    uint256 public immutable threashold = 256;

    uint256 internal _addedgascost;
    uint256 internal _addedcount;
    uint256 internal _ptr;
    uint256 internal _ptrstart;
    uint256 internal _count;
    uint256 internal _lastrandom;

    mapping(uint256 => uint256[256]) internal _randoms;


    constructor() {}

    function resetFee() public onlyOwner {
        _addedcount = 0;
    }

    function purgeAll() external onlyOwner {
        _ptrstart = _ptr;
        _count = 0;
    }

    function collectFund() external onlyOwner {
        payable(msg.sender).transfer(address(this).balance);
    }

    function setCost(uint256 gascost_, uint256 count_)
        external
        onlyOperator(ownerOf())
    {
        if (_addedcount > threashold) {
            _addedgascost = (_addedgascost * threashold) / _addedcount;
            _addedcount = threashold;
        }
        _addedgascost += gascost_;
        _addedcount += count_;
        emit Fee(fee());
    }

    function fee() public view returns (uint256) {
        if (_addedcount == 0) return 0;
        return ((_addedgascost * margin) / _addedcount) / 10**18;
    }

    function count() public view returns (uint256) {
        return _count;
    }

    function add(uint256[256] calldata newrandoms_)
        external
        onlyOperator(ownerOf())
    {
        unchecked {
            _count += 256;
            _randoms[_ptr++] = newrandoms_;
        }
        if (fee() != 0 && address(this).balance > fee() * 256)
            payable(msg.sender).transfer(fee() * 256);
    }

    function random( uint256 count_, uint256 random_, bool event_ ) public payable returns (uint256[] memory out_) {
        if (msg.sender != ownerOf()) {
            require(fee() != 0, "Random: desactivated");
            require(msg.value >= fee() * count_, "Random: Must pay fee");
            payable(msg.sender).transfer(msg.value - (fee() * count_));
        }
        out_ = new uint256[](count_);
        for (uint256 i; i < count_; i++) {
            out_[i] = _random(random_);
            random_ = out_[i];
        }
        if (event_) emit Randoms(out_);
        emit Remaining(_count);
    }

    function _reset() internal {
        if (_count == 0) {
            require(_ptr > 0, "Random: no random available");
            _ptrstart = 0;
            _count = _ptr * 256;
            emit Reset(_count);
        }
    }
    function _random(uint256 random_) internal virtual returns (uint256 out_) {
        _reset();

        out_ = uint256(
            keccak256(
                abi.encode(
                    random_,
                    _lastrandom,
                    _randoms[_ptrstart][255 - (_count % 256)]
                )
            )
        );

        for (
            uint256 i = block.number > 10 ? block.number - 10 : 1;
            i < block.number;
            i++
        ) out_ = uint256(keccak256(abi.encode(out_, blockhash(i))));

        if (_count % 256 == 0) _ptrstart++;
        _count--;
        _lastrandom = out_;
    }
    function freeRandom( uint256 count_, uint256 random_) public view returns (uint256[] memory out_) {
        out_ = new uint256[](count_);
        for (uint256 i; i < count_; i++) {
            out_[i] = _freeRandom(random_);
            random_ = out_[i];
        }
    }

    function _freeRandom(uint256 random_) internal view returns (uint256) {
        for (
            uint256 i = block.number > 20 ? block.number - 20 : 1;
            i < block.number;
            i++
        ) random_ = uint256(keccak256(abi.encode(random_, blockhash(i))));
        random_ = uint256(keccak256(abi.encode(random_, _lastrandom)));

        unchecked {
            if (_ptrstart != _ptr) {
                uint256 k = uint8(random_ % (256 * _ptr));
                random_ = _randoms[k / 256][k % 256];
                for (
                    uint256 i = block.number > 20 ? block.number - 20 : 1;
                    i < block.number;
                    i++
                )
                    random_ = uint256(
                        keccak256(abi.encode(random_, blockhash(i)))
                    );
            }
        }

        return random_;
    }
}
