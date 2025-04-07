from dataclasses import dataclass
from dataclasses import field
from typing import Self
from json import load
import paramiko
import io

@dataclass(frozen=True)
class Credentials:
  USER  : str
  KEY   : str
  PKEY  : paramiko.rsakey.RSAKey = field(init=False)
  HOST  : str = field(init=False, default='gadi.nci.org.au')

  def __post_init__(s: Self):
    object.__setattr__(
      s,
      'PKEY',
      paramiko.RSAKey.from_private_key(io.StringIO(s.KEY))
    )

  @classmethod
  def __from_file__(cls: 'Credentials', user: str, path_id_rsa: str )->'Credentials':
    return Credentials(user, open(path_id_rsa, 'r').read())
  
  def __str__(s: Self)->str: return ' '.join([s.USER])

  @classmethod
  def __from_json__(cls: 'Credentials', file: str)->'Credentials':
    return Credentials.__from_file__(**load(open(file, 'r')))

def t():
  c = Credentials.__from_json__('nci/configs/credentials.json')
  print(c)
  return c

if __name__ == '__main__': print('test passed' if t() else 'test failed')
