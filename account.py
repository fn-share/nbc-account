# account.py

import sys, os
if sys.version_info.major < 3:
  raise Exception('only support python v3+')

_data_dir = os.environ.get('LOCAL_DIR','./data')
os.makedirs(_data_dir,exist_ok=True)

#----

import time, struct, json, traceback
from binascii import hexlify, unhexlify

from nbc import util as nbc_util
from nbc import wallet

import getpass, shutil, click
from binascii import hexlify, unhexlify

class _Help:
  figerprint = 'figerprint of account'
  version    = "account version, default is '0x00'"
  seed       = 'seed string to generate account, use random value if absent'
  vcn        = 'virtual chain number, 0~65535 or None when absent'
  password   = 'password for the account'
  password2  = 'passphrase, empty string for no protecting'

def load_config(cfg_file):
  if os.path.isfile(cfg_file):
    with open(cfg_file,'r') as f:
      return json.load(f)
  else: return {}

@click.group()
def cmd_line():
  pass

@cmd_line.command(name='list')
@click.option('--figerprint','-fp',default='',help=_Help.figerprint)
@click.option('--ver',default='',help=_Help.version)
def account_list(figerprint, ver):
  cfg_file = os.path.join(_data_dir,'config.json')
  cfg = load_config(cfg_file)
  accounts = cfg.get('accounts',{})
  if not accounts:
    print('No account found, please uses "generate" command to create one first.\n')
    return
  
  if figerprint:   # only list one account
    acc = accounts.get(figerprint)
    if acc:
      vcn = acc.get('vcn',None)
      pubkey = acc.get('pubkey','')
      pubkey2 = unhexlify(pubkey)
      
      if not ver: ver = '0x00'
      if ver[:2].lower() == '0x':  # version style
        ver = unhexlify('%02x' % int(ver,16))
        addr = nbc_util.key.publickey_to_address(pubkey2,vcn,ver).decode('utf-8')
      else:    # by prefix style
        addr = nbc_util.key.publickey_to_prefix_addr(pubkey2,vcn,ver).decode('utf-8')
      pubhash = nbc_util.key.publickey_to_hash(pubkey2).hex()
      
      encrypted = 1 if acc.get('encrypted',False) else 0
      prvkey = acc.get('prvkey','')
      prvkey = '****' if prvkey else 'none'
      
      print('Figerprint : %s' % (figerprint,))
      print('VCN        : %s' % (vcn,))
      print('Encrypted  : %s' % (encrypted,))
      print('Private key: %s' % (prvkey,))
      print('Public key : %s' % (pubkey,))
      print('Address    : %s' % (addr,))
      print('Pubkey hash: %s' % (pubhash,))
    else: print('Can not find account: %s' % (figerprint,))
    
    print()
    return
  
  default_fp = cfg.get('default','')
  print('Default account: %s' % (default_fp or '',))
  kv = list(accounts.items())
  print('Total %i account(s):' % len(kv))
  
  for k,v in kv:
    encrypted = 1 if v.get('encrypted',False) else 0
    vcn = v.get('vcn',None)
    pubkey = v.get('pubkey','')
    prvkey = v.get('prvkey','')
    prvkey = '****' if prvkey else 'none'
    print('  fp=%s, vcn=%s, encrypted=%s, prvkey=%s, pubkey=%s' % (k,vcn,encrypted,prvkey,pubkey[:8]+'...'+pubkey[-8:]))
  print()

def save_cfg_file(cfg_file, cfg):
  with open(cfg_file,'w') as f:
    s = json.dumps(cfg,indent=2)
    f.write(s)

@cmd_line.command(name='set')
@click.argument('key_value',nargs=2)
def account_set(key_value):
  cfg_file = os.path.join(_data_dir,'config.json')
  cfg = load_config(cfg_file)
  
  k,v = key_value
  k = k.lower()
  if k == 'config.default':
    figerprint = v
    
    accounts = cfg.get('accounts',{})
    if v not in accounts:
      print('failed: can not find account (%s)!\n' % (v,))
      return
    
    cfg['default'] = v
    save_cfg_file(cfg_file,cfg)
    print('set default account (%s) successful.\n' % (v,))
  
  else:
    print('error: invalid key (%s)' % (k,))

@cmd_line.command()
@click.option('--seed',default='',help=_Help.seed)
@click.option('--password','-p',help=_Help.password2)
@click.option('--vcn',type=click.INT,default=65536,help=_Help.vcn)
def generate(seed, password, vcn):
  if password is None:
    password = getpass.getpass('input password (empty for no protecting):')
    if password:
      password2 = getpass.getpass('input again:')
      if password != password2:
        print('error: the second input is not same to previous!\n')
        return
  if not password: password = ''
  
  cfg_file = os.path.join(_data_dir,'config.json')
  cfg = load_config(cfg_file)
  
  if not seed:
    seed = os.urandom(32)       # generate account by random seed
  else: seed = seed.encode('utf-8')
  if vcn < 0 or vcn >= 65535: vcn = None
  
  acc = wallet.HDWallet.from_master_seed(seed,vcn)
  hex_pubkey = acc.publicKey().hex()
  same_count = [1 for item in cfg.get('accounts',{}).values() if item['pubkey'] == hex_pubkey]
  if same_count:
    print('same account already exists, overwrite it?')
    if input('Yes or No (Y/N): ').strip().upper() != 'Y':
      print('overwrite ignored!\n')
      return
  
  print('generate account successful\n')
  wallet.saveTo(cfg_file,acc,passphrase=password,cfg=cfg)

@cmd_line.command()
@click.option('--figerprint','-fp',help=_Help.figerprint)
def delete(figerprint):
  if not figerprint:
    figerprint = input('input figerprint:').strip().lower()
    if not figerprint: return
  
  cfg_file = os.path.join(_data_dir,'config.json')
  cfg = load_config(cfg_file)
  accounts = cfg.get('accounts',{})
  if figerprint not in accounts:
    print('failed: can not find account (%s)!\n' % (figerprint,))
    return
  
  accounts.pop(figerprint,None)
  b = [(v['time'],k) for k,v in accounts.items()]
  if b:
    cfg['default'] = sorted(b)[-1][1]  # try shift to last created item
  else: cfg['default'] = ''
  save_cfg_file(cfg_file,cfg)
  print('delete account (%s) successful.\n' % (figerprint,))

@cmd_line.command(name='export')
@click.option('--figerprint','-fp',help=_Help.figerprint)
@click.option('--with_private',default=False,is_flag=True,help='include private key, be careful!')
@click.option('--password','-p',help=_Help.password)
def account_export(figerprint, with_private, password):
  cfg_file = os.path.join(_data_dir,'config.json')
  cfg = load_config(cfg_file)
  
  accounts = cfg.get('accounts',{})
  acc_item = accounts.get(figerprint,None)
  if not acc_item:
    print('no account (%s).\n' % (figerprint,))
    return
  elif acc_item.get('type') != 'HD':
    print('only support HD account.\n')
    return
  
  if acc_item.get('encrypted'):
    if not password:
      password = getpass.getpass('input password:')
      if not password: return
  else: password = ''
  
  acc = wallet.loadFrom(cfg,password,figerprint)
  if acc.publicKey().hex() != acc_item.get('pubkey'):
    print('error: incorrect password!\n')
    return
  
  print(acc.to_extended_key(include_prv=with_private))

@cmd_line.command(name='import')
@click.option('--password','-p',help=_Help.password2)
@click.option('--vcn',type=click.INT,default=65536,help=_Help.vcn)
@click.argument('keycode',nargs=1)
def account_import(password, vcn, keycode):
  if keycode[:4] not in ('xpub','xprv'):
    print('error: invalid keycode!')
    return
  
  if password is None and keycode[:4] == 'xprv':
    password = getpass.getpass('input password (empty for no protecting):')
    if password:
      password2 = getpass.getpass('input again:')
      if password != password2:
        print('error: the second input is not same to previous!\n')
        return
  if not password: password = ''
  
  cfg_file = os.path.join(_data_dir,'config.json')
  cfg = load_config(cfg_file)
  
  if vcn >= 65536: vcn = None
  acc = wallet.HDWallet.from_extended_key(keycode,vcn)
  
  hex_pubkey = acc.publicKey().hex()
  same_count = [1 for item in cfg.get('accounts',{}).values() if item['pubkey'] == hex_pubkey]
  if same_count:
    print('same account already exists, overwrite it?')
    if input('Yes or No (Y/N): ').strip().upper() != 'Y':
      print('overwrite ignored!\n')
      return
  
  print('generate account successful\n')
  wallet.saveTo(cfg_file,acc,passphrase=password,cfg=cfg)


if __name__ == '__main__':
  if sys.flags.interactive:
    try:
      cmd_line()
    except SystemExit: pass
  else:
    cmd_line()

# usage: LOCAL_DIR=./data python3 account.py --help
