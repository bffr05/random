// SPDX-License-Identifier: MIT
// Beef MarketPlace Contracts v0.0.0 hello@mcdu.com

pragma solidity ^0.8.0;

import "./Random.sol";


contract xRandom is Random {
    mapping(uint256 => uint256) private _usedrandoms;

    constructor() {}

function _random(uint256 random_) internal virtual override returns (uint256 out_) {
        _reset();

        for (uint b = 0; b < 256; b++) {
            uint ki = (random_ + b)%256;
            for (uint256 p = _ptrstart; p < _ptr; p++)
                if (_usedrandoms[p] & (1 << ki) == 0) {
                    _usedrandoms[p] |= 1 << ki;

                    out_ = _randoms[p][ki];
                    for (
                        uint256 i = block.number > 10
                            ? block.number - 10
                            : 1;
                        i < block.number;
                        i++
                    )
                        out_ = uint256(
                            keccak256(abi.encode(out_, blockhash(i)))
                        );
                    while (_usedrandoms[_ptrstart] == type(uint256).max)
                    {
                        delete _usedrandoms[_ptrstart];
                        _ptrstart++;
                    }
                    _count--;
                    _lastrandom = out_;
                    return out_;
                }            
        }
        assert(false);
    }

}