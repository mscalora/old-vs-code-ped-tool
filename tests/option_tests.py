import unittest
import subprocess
import sys
from io import StringIO
from unittest.mock import patch
import os
#sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from importlib.util import spec_from_loader, module_from_spec
from importlib.machinery import SourceFileLoader 

ped_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ped')
spec = spec_from_loader("ped", SourceFileLoader("ped",ped_path))
ped = module_from_spec(spec)
spec.loader.exec_module(ped)

tests_path = os.path.dirname(__file__)
data_path = os.path.join(tests_path, 'data')
abcdef_path = os.path.join(data_path, 'abcdef.txt')

def run_args(args):
  with patch('sys.stdout', new = StringIO()) as output:
    ped.main(args)
    return output.getvalue()

class TestOptions(unittest.TestCase):

  def test_noop(self):
    out = run_args(['-f', abcdef_path])
    self.assertEqual(out, 'abcdef')
    out = run_args(['--filepath', abcdef_path])
    self.assertEqual(out, 'abcdef')

  def test_noop_norm(self):
    out = run_args(['-n', '-f', abcdef_path])
    self.assertEqual(out, 'abcdef\n')
    out = run_args(['--no-eof', '--normalize', '--filepath', abcdef_path])
    self.assertEqual(out, 'abcdef')

  def test_noop_norm_ending(self):
    out = run_args(['-n', '-f', abcdef_path, '--line-ending', '\r'])
    self.assertEqual(out, 'abcdef\r')
    out = run_args(['-n', '-f', abcdef_path, '--line-ending', ':'])
    self.assertEqual(out, 'abcdef:')

  def test_normalize(self):
    with patch('sys.stdout', new = StringIO()) as output:
          ped.main(['-f', abcdef_path, '-n'])
          self.assertEqual(output.getvalue(), 'abcdef\n')

if __name__ == '__main__':
    unittest.main()
