
from .config import CONFIG, setup_class_logger
import tempfile
import os
import subprocess
import json
import re
import shlex

class GethRunner(object):
    '''
    Class to setup and run a geth-for-test instance
    '''

    def __init__(self):
        '''
        The contract descriptor is a json file which acts as an
        adjunct to a contract source file
        '''
        self.log = setup_class_logger(self)
        self.data_path = CONFIG.get('data_path')
        self.passfile_path = None
        self.genesis_path = None
        self.addresses_to_fund = []  # genesis file needs these
        self.proc = None  # Popen instance

    def _clear_cruft(self, root=None, top_level_too=False):
        if not root:
            root = self.data_path
        for path in (os.path.join(root,f) for f in os.listdir(root)):
            if os.path.isdir(path):
                self._clear_cruft(path,False)
                #self.log.info('rmdir: {0}'.format(path))                
                os.rmdir(path)                 
            else:
                #self.log.info('Del: {0}'.format(path))
                os.unlink(path)
        if top_level_too:
            #self.log.info('rmdir: {0}'.format(root))            
            os.rmdir(root)      

    def _setup(self):
        '''
        Create folders, accounts
        '''
        if not self.data_path:
            self.data_path = tempfile.mkdtemp(prefix="g4t_")
        self.log.info("Path: {0}".format(self.data_path))
        self.passfile_path = os.path.join(self.data_path, 'passfile')
        self.genesis_path = os.path.join(self.data_path, 'genesis.json')        
        self._clear_cruft()
        self._write_passfile()
        self._write_genesis() # one with no accounts so create_accts can work        
        self._create_accts()
        if CONFIG['ext_accts']:
            self.addresses_to_fund.extend(CONFIG['ext_accts'])
        self._write_genesis() # real one
        

    def _cleanup(self):
        '''
        Clean everything up
        '''
        self._clear_cruft(top_level_too=True)

    def _make_args_str(self, setup=False, added_args=None):
        '''
        Return args string.
        '''
        baseDict = CONFIG['base_args']
        # Replace computed vals
        baseDict['datadir'] = '--datadir {0}'.format(self.data_path)
        baseDict['password'] = '--password {0}'.format(self.passfile_path)            
        baseDict['genesis'] = '--genesis {0}'.format(self.genesis_path)
        args = baseDict.values()
        if not setup:
            args += CONFIG['run_args'].values()
        if added_args:
            args += added_args
        return ' '.join(args)
  
    def _exec_sync(self, added_args):
        '''
        Run geth synchronously and capture output.
        Base args used are only what is required, and do not include
        any of the mining options
        '''
        argStr = self._make_args_str(setup=True, added_args=added_args)
        geth_cmd = "{0} {1}".format(CONFIG['geth_cmd'], argStr)         
        self.log.info("sync cmd: {0}".format(geth_cmd))              
        result = subprocess.check_output(geth_cmd, shell=True)  
        return result        
  
    def _exec_async(self, added_args):
        '''
        The *real* run. geth is run asynchronously and the
        Popen object is returned so it can be used later to 
        check status or terminate.
        '''
        # args = [, ]
        argStr = self._make_args_str(setup=False, added_args=added_args)
        gethStr = '{0} {1}'.format(CONFIG['geth_cmd'], argStr)
        self.log.info("geth cmd: {0}".format(gethStr))
        cmdStr = CONFIG['term_cmd'].format(gethStr)
        cmdList = shlex.split(cmdStr)   
        self.log.info("async cmdList: {0}".format(cmdList))
        self.proc = subprocess.Popen(cmdList)
   
    def _write_passfile(self):
        '''
        Empty file
        '''
        with open(self.passfile_path, 'w') as outfile:
            outfile.write('')        
   
    def _write_genesis(self):
        genesis_data = {
                          "alloc": {
                           },
                        
                          "nonce": "0x0000000000000042",
                          "difficulty": "0x01000",
                          "mixhash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                          "coinbase": "0x0000000000000000000000000000000000000000",
                          "timestamp": "0x00",
                          "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
                          "extraData": "0x11bbe8db4e347b4e8c937c1c8370e4b5ed33adb3db69cbdb7a38e1e50b1b82fa",
                          "gasLimit": "0x1000000"
                        }
        # pre-fund accounts
        for addr in self.addresses_to_fund:
            genesis_data['alloc'][addr] =  {"balance": "1000000000000000000000000000000"}
        with open(self.genesis_path, 'w') as outfile:
            json.dump(genesis_data, outfile)
                            
   
    def _create_accts(self):
        '''
        Note that you have to write a genesis file without the accts before you can create the accts
        '''
        cnt = CONFIG.get('create_accts')
        if cnt:
            for _ in range(cnt):
                result = self._exec_sync( ['account new'])
                # result will be of form: "Address: {value}"
                if result:
                    match = re.match('.*{(.*)}.*', result)
                    if match:
                        addr = match.group(1)
                        self.addresses_to_fund.append(addr)
                        self.log.info("New Addr: {0}".format(addr))
                 
#
# Public API
#

    def set_args(self, new_args_dict):
        '''
        dict is keyed by the lower case argument name:
            { 'rpcport': '--rpcport "8545"' }
        Note that full arg sped is required in the value.
        Any arg already spcified will be replaced.
        If arg is not found it is put into the 
        '''
        for k in new_args_dict.keys():
            dst = CONFIG['run_args']
            if k in CONFIG['base_args'].keys():
                dst = CONFIG['base_args']
            v = new_args_dict[k]
            if v is None:
                if k in dst.keys():
                    del dst[k]
            else:
                dst[k] = v
    
    def create_accts(self, count):
        '''
        Create, fund and unlock this number of accounts.
        Overrides CONFIG default
        '''
        CONFIG['create_accts'] = count
    
    def ext_accts(self, addr_list):
        '''
        List of addresses that will be managed by and external wallet
        and need to be funded in the genesis file
        '''
        CONFIG['ext_accts'] = addr_list

    def run(self):
        self._setup()
        if CONFIG.get('create_accts'):
            unlock_str = '--unlock "{0}" '.format(','.join([str(i) for i in range(CONFIG.get('create_accts'))]))
        self._exec_async([unlock_str])
        
    def running(self):
        val = False
        if self.proc:
            val = self.proc.poll() is None
        return val
    
    def stop(self, cleanup=True):
        if self.proc:
            self.proc.terminate()
            self.proc.wait()
        if cleanup:
            self._cleanup()
 
