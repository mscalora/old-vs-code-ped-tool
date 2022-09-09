import os
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader
from io import StringIO
from unittest.mock import patch 

tests_path = os.path.dirname(__file__)
data_path = os.path.join(tests_path, 'data')
abcdef_path = os.path.join(data_path, 'abcdef.txt')
abc_def_path = os.path.join(data_path, 'abc_def.txt')
short_path = os.path.join(data_path, 'short.txt')
short_uc_path = os.path.join(data_path, 'short_uc.txt')
long_path = os.path.join(data_path, 'long.txt')

ped_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ped')
spec = spec_from_loader("ped", SourceFileLoader("ped",ped_path))
ped = module_from_spec(spec)
spec.loader.exec_module(ped)

def run_args(args: list[str]):
  with patch('sys.stdout', new = StringIO()) as output:
    ped.catching_main(args)
    return output.getvalue()

def run_piped(args: list[str], input: str):
  with patch('sys.stdin', new = StringIO(input)) as output:
    with patch('sys.stdout', new = StringIO()) as output:
      ped.catching_main(args)
      return output.getvalue()

def file_get_contents(path: str):
  with open(path, encoding='utf8') as f:
    return f.read()
