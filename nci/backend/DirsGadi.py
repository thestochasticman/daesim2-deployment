from dataclasses import dataclass
from json import load

@dataclass(frozen=True)
class DirsGadi:
  input : str
  output: str

  @classmethod
  def __from_json__(cls: 'DirsGadi', file: str)->'DirsGadi':
    return DirsGadi(**(load(open(file, 'r'))))
  
def t():
  dg = DirsGadi.__from_json__('nci/configs/dirs_gadi.json')
  return dg

if __name__ == '__main__': print('test passed' if t() else 'test failed')