#
# default poker config parms
#
import logging
import os

CONFIG = {
    'create_accts': 2,  # geth will create, fund and unlock this many accounts
                        # You'll have to ask it for the addresses
    'ext_accts': ['0xe51f7e720f4201f8bdd9a1bfd935f738bd028315'],  # geth will fund these, assuming you have them in a wallet somewhere
        
    'data_path': None,  # if none will create a folder in a tmp area and delete it on exit
    'term_cmd': 'xterm -e sh -c \'{0}\'',  # geth + args is put into {0}
    'geth_cmd': 'geth',  # let it be found in PATH
    
    # args always used, even during synchronous setup ('geth account new') invocations
    'base_args': {   'maxpeers': '--maxpeers "0"',
                     'nodiscover': '--nodiscover',
                     'port': '--port "30333"',
                     'networkid': '--networkid "195"',  # No particular reason 
                     'rpccorsdomain': '--rpccorsdomain "*"',
                     'shh': '--shh',
                     'rpc': '--rpc',
                     'rpcapi': '--rpcapi "eth,net,shh"',
                     'rpcport': '--rpcport 8545',  # this one will often be changed              
                      # these require replacing with computed values
                     'datadir': '--datadir DATA_DIR',
                     'password': '--password PASSFILE'
    },
          
    # added to base_args for async (final run) invocations
    'run_args': { 'mine': '--mine',
                     # 'autodag': '--autodag',  # How would you turn this off?
                     'minerthreads': '--minerthreads "1"',
                     'gasprice': '--gasprice "20000000"',                       
                     'etherbase': '--etherbase "0"',
    },          
    
    # String, usually set by the "set_cmd()" method, that gets appended to the run cmd  

    'logging': {
        # Global logging data. Code wishing to use
        # it needs to import CONFIG and call setup_class_logger(self)
        'GethRunner': logging.INFO,
    }

}

def setup_class_logger(cls_inst):
    log =  logging.getLogger(cls_inst.__class__.__name__)
    if CONFIG['logging'].get(cls_inst.__class__.__name__):
        log.setLevel(CONFIG['logging'].get(cls_inst.__class__.__name__))
    return log
