# account.py

import sys, os
if sys.version_info.major < 3:
  raise Exception('only support python v3+')

_data_dir = os.environ.get('LOCAL_DIR','./data')
os.makedirs(_data_dir,exist_ok=True)

#----

import time, struct, traceback
from binascii import hexlify, unhexlify

from nbc import util as nbc_util
from nbc import wallet

import getpass, shutil, click
from binascii import hexlify, unhexlify

@click.group()
def cmd_line():
  pass

if __name__ == '__main__':
  if sys.flags.interactive:
    try:
      cmd_line()
    except SystemExit: pass
  else:
    cmd_line()
