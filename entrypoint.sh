#!/bin/bash
./komodo/src/komodod -regtest -ac_name=LIST &
sleep 3
./pos64staker/genaddresses.py