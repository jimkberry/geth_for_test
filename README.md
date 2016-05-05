# geth_for_test #

## Goals ##

The point to this package is to provide a python-callable way to run `geth` as a temporary, 1-node, mining Ethereum testnet in a subprocess that can be fired-up for shutdown by test scripts.

## Installing ##

- Clone this repo
- `python setup.py install` (or `develop`)

## Some potential gotchas ##

- It is assumed that a new shell will find `geth` in the path
- The `geth` subprocess currently runs in a shell attached to an `xterm` window. It is controlled by config vars, but there is currently nothing in place to make it work differently.
- In order to mine, `geth` needs a 1GB "DAG" file, which appears to always be the same and stored in the same place for a new blockchain. 
At the moment you can create a DAG by running the `g4t.py` example script until it's done, but that's dumb. There should be a frontend command to just create the DAG and exit.
-It takes a while for `geth` to get up and running even if there's a pre-existing DAG. You will need some way to check if it is ready to accept commands before your tests run. I didn't want to add any Ethereum-comms dependencies to it (especially since I wrote it to be the test rigging for `eth_proxy.py` so there's a certain amount of chicken/egg here.

## Using in a python script ##

## Using with non-python code ##


---
let me know if you find anything or have any ideas.

-jim


