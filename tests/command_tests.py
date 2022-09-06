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
abc_def_path = os.path.join(data_path, 'abc_def.txt')
short_path = os.path.join(data_path, 'short.txt')
short_uc_path = os.path.join(data_path, 'short_uc.txt')
long_path = os.path.join(data_path, 'long.txt')

short_text = 'this is a test\nof this thing here \nand you might be special.'

def run_args(args):
  with patch('sys.stdout', new = StringIO()) as output:
    ped.main(args)
    return output.getvalue()

class TestCommands(unittest.TestCase):

  def test_line_sub(self):
    out = run_args(['-f', abcdef_path, 's/c/C/'])
    self.assertEqual(out, 'abCdef\n')
    out = run_args(['-f', abc_def_path, 's/^../x/'])
    self.assertEqual(out, 'xc\nxf\n')
    out = run_args(['-f', abc_def_path, 's/[ace]/@@@/'])
    self.assertEqual(out, '@@@b@@@\nd@@@f\n')
    out = run_args(['-f', short_path, 's/this|here/----/'])
    self.assertEqual(out, '---- is a test\nof ---- thing ---- \nand you might be special.\n')
    out = run_args(['-f', short_path, '-L', '1', 's/this|here/----/'])
    self.assertEqual(out, '---- is a test\nof ---- thing here \nand you might be special.\n')
    out = run_args(['-f', short_path, 's/[aeiou]/#/'])
    self.assertEqual(out, 'th#s #s # t#st\n#f th#s th#ng h#r# \n#nd y## m#ght b# sp#c##l.\n')
    out = run_args(['-f', short_path, '-L', '3', '-M', '8', 's/[aeiou]/•'])
    self.assertEqual(out, 'th•s •s • test\n•f th•s th•ng here \n•nd y•u might be special.\n')

  def test_file_sub(self):
    out = run_args(['-f', abcdef_path, 'S/c/C/'])
    self.assertEqual(out, 'abCdef')
    out = run_args(['-n', '-f', abcdef_path, 'S/c/C/'])
    self.assertEqual(out, 'abCdef\n')
    out = run_args(['-n', '-f', abc_def_path, 'S/c/C/'])
    self.assertEqual(out, 'abC\ndef\n')
    out = run_args(['-n', '-f', abc_def_path, 'S/c\nd/C\nD/'])
    self.assertEqual(out, 'abC\nDef\n')
    out = run_args(['-nm', '-f', abc_def_path, 'S/.$/X/'])
    self.assertEqual(out, 'abX\ndeX\n')

  def test_fixed_sub(self):
    out = run_args(['-f', short_path, 'f/./!/'])
    self.assertEqual(out, 'this is a test\nof this thing here \nand you might be special!\n')

  def test_grep(self):
    out = run_args(['-f', short_path, 'g/thing'])
    self.assertEqual(out, 'of this thing here \n')
    out = run_args(['-f', short_path, r'g/\b\w{5}\b/'])
    self.assertEqual(out, 'of this thing here \nand you might be special.\n')
    out = run_args(['-f', short_path, r'g/\b\w{5}\b/'])
    self.assertEqual(out, 'of this thing here \nand you might be special.\n')
    e = ('Python is an interpreted, interactive, object-oriented programming language. It \n' +
      'applications that need a programmable interface. Finally, Python is portable: it \n')
    out = run_args(['-f', long_path, '-im', r'g/it $'])
    self.assertEqual(out, e)

  def test_line_grep(self):
    out = run_args(['-f', short_path, 'G/.*special.*'])
    self.assertEqual(out, 'and you might be special.\n')
    out = run_args(['-f', short_path, r'G/of.*here\s?'])
    self.assertEqual(out, 'of this thing here \n')

  def test_file_only(self):
    out = run_args(['-f', short_path, '--dotall', r'O/\b\w{5}\b.*\b\w{5}\b/'])
    self.assertEqual(out, 'thing here \nand you might')

  def test_exclude(self):
    out = run_args(['-f', short_path, r'x/this'])
    self.assertEqual(out, 'and you might be special.\n')
    out = run_args(['-f', long_path, '-dm', r'x/\b[A-Z]'])
    text = ('incorporates modules, exceptions, dynamic typing, very high level dynamic data \n' +
      'object-oriented programming, such as procedural and functional programming. \n' +
      'many system calls and libraries, as well as to various window systems, and is \n')
    self.assertEqual(out, text)

  def test_line_exclude(self):
    out = run_args(['-f', short_path, '-dm', r'X/[a-eg-z .]*/'])
    self.assertEqual(out, 'of this thing here \n')

  def test_line_only(self):
    out = run_args(['-f', short_path, '-dm', r'o/\b\w{7}\b'])
    self.assertEqual(out, 'special\n')
    out = run_args(['-f', long_path, '-dm', r'o/\b\w+[ .]*$', r'S/\s+/ ', r'S/ $|\./'])
    self.assertEqual(out, 'It data beyond programming to is for it Windows')

  def test_file_only(self):
    out = run_args(['-f', short_path, '-dm', r'O/\b\w{7}\b'])
    self.assertEqual(out, 'special')
    out = run_args(['-f', long_path, '-dm', r'O/\b\w{7}\b'])
    self.assertEqual(out, 'modulesdynamicdynamicclassesvarioussystemsFinallyWindows')

  def test_line_remove(self):
    out = run_args(['-f', short_path, '-dm', r'r/\b\w{2,5}\b( |$|.)'])
    self.assertEqual(out, 'a \n\nspecial.\n')

  def test_file_remove(self):
    out = run_args(['-f', short_path, '-dm', r'R/\b\w{2,5}\b( |\n|$|\.)+/'])
    self.assertEqual(out, 'a special.')
    
  def test_line_upper(self):
    out = run_args(['-f', short_path, r'u/\b\w{3,4}\b'])
    self.assertEqual(out, 'THIS is a TEST\nof THIS thing HERE \nAND YOU might be special.\n')

  def test_file_upper(self):
    out = run_args(['-f', short_path, '-dm', r'U/\b\w{4}\s?\n\w{2,4}\b'])
    self.assertEqual(out, 'this is a TEST\nOF this thing HERE \nAND you might be special.')

  def test_line_lower(self):
    out = run_args(['-f', short_uc_path, r'l/\b\w{3,4}\b'])
    self.assertEqual(out, 'this IS A test\nOF this THING here \nand you MIGHT BE SPECIAL.\n')

  def test_file_lower(self):
    out = run_args(['-f', short_uc_path, '-dm', r'L/\b\w{4}\s?\n\w{2,4}\b'])
    self.assertEqual(out, 'THIS IS A test\nof THIS THING here \nand YOU MIGHT BE SPECIAL.')

  def test_line_title(self):
    out = run_args(['-f', short_uc_path, r't/\b\w.*\w\b'])
    self.assertEqual(out, 'This Is A Test\nOf This Thing Here \nAnd You Might Be Special.\n')

  def test_file_title(self):
    out = run_args(['-f', short_path, '-dm', r'T/\b\w{4}\s?\n\w{2,4}\b'])
    self.assertEqual(out, 'this is a Test\nOf this thing Here \nAnd you might be special.')
    out = run_args(['-f', short_uc_path, '-dm', r'T/\b\w{4}\s?\n\w{2,4}\b'])
    self.assertEqual(out, 'THIS IS A Test\nOf THIS THING Here \nAnd YOU MIGHT BE SPECIAL.')

  def test_line_cap(self):
    out = run_args(['-f', short_uc_path, r'c/\b\w.*\w\b'])
    self.assertEqual(out, 'This is a test\nOf this thing here \nAnd you might be special.\n')

  def test_file_cap(self):
    out = run_args(['-f', short_path, '-dm', r'C/\b\w{4}\s?\n\w{2,4}\b'])
    self.assertEqual(out, 'this is a Test\nof this thing Here \nand you might be special.')
    out = run_args(['-f', short_uc_path, '-dm', r'C/\b\w{4}\s?\n\w{2,4}\b'])
    self.assertEqual(out, 'THIS IS A Test\nof THIS THING Here \nand YOU MIGHT BE SPECIAL.')

  def test_append_line(self):
    out = run_args(['-f', abcdef_path, r'a/123456'])
    self.assertEqual(out, 'abcdef\n123456\n')
    out = run_args(['-f', short_path, 'a/oh yea?\nyea!'])
    self.assertEqual(out, 'this is a test\nof this thing here \nand you might be special.\noh yea?\nyea!\n')

  def test_append_char(self):
    out = run_args(['-f', abcdef_path, r'A/123456'])
    self.assertEqual(out, 'abcdef123456')
    out = run_args(['-f', short_path, 'A/oh yea?\nyea!'])
    self.assertEqual(out, 'this is a test\nof this thing here \nand you might be special.oh yea?\nyea!')
    out = run_args(['-n', '-f', short_path, 'A/oh yea?\nyea!'])
    self.assertEqual(out, 'this is a test\nof this thing here \nand you might be special.\noh yea?\nyea!')

  def test_prepend_line(self):
    out = run_args(['-f', abcdef_path, 'p/123456'])
    self.assertEqual(out, '123456\nabcdef\n')
    out = run_args(['-f', short_path, 'p/oh yea?\nyea!'])
    self.assertEqual(out, 'oh yea?\nyea!\nthis is a test\nof this thing here \nand you might be special.\n')

  def test_prepend_char(self):
    out = run_args(['-f', abcdef_path, 'P/123456'])
    self.assertEqual(out, '123456abcdef')
    out = run_args(['-f', short_path, 'P/oh yea?\nyea!'])
    self.assertEqual(out, 'oh yea?\nyea!this is a test\nof this thing here \nand you might be special.')
    out = run_args(['-n', '-f', short_path, 'P/oh yea?\nyea!'])
    self.assertEqual(out, 'oh yea?\nyea!this is a test\nof this thing here \nand you might be special.\n')

  def test_insert_line(self):
    out = run_args(['-f', abcdef_path, 'i/0/123456'])
    self.assertEqual(out, '123456\nabcdef\n')
    out = run_args(['-f', abcdef_path, 'i/1/123456'])
    self.assertEqual(out, 'abcdef\n123456\n')
    out = run_args(['-f', abcdef_path, 'i/-5/123456'])
    self.assertEqual(out, '123456\nabcdef\n')
    out = run_args(['-f', abcdef_path, 'i/5/123456'])
    self.assertEqual(out, 'abcdef\n123456\n')
    out = run_args(['-f', short_path, 'i/2/123456'])
    self.assertEqual(out, 'this is a test\nof this thing here \n123456\nand you might be special.\n')
    out = run_args(['-f', short_path, 'i/-2/123456'])
    self.assertEqual(out, 'this is a test\n123456\nof this thing here \nand you might be special.\n')

  def test_insert_char(self):
    out = run_args(['-f', abcdef_path, 'I/0/123456'])
    self.assertEqual(out, '123456abcdef')
    out = run_args(['-f', abcdef_path, 'I/6/123456'])
    self.assertEqual(out, 'abcdef123456')
    out = run_args(['-f', abcdef_path, 'I/-50/123456'])
    self.assertEqual(out, '123456abcdef')
    out = run_args(['-f', abcdef_path, 'I/10000/123456'])
    self.assertEqual(out, 'abcdef123456')
    out = run_args(['-f', short_path, 'I/6/123456'])
    self.assertEqual(out, 'this i123456s a test\nof this thing here \nand you might be special.')
    out = run_args(['-f', short_path, 'I/-10/123456'])
    self.assertEqual(out, 'this is a test\nof this thing here \nand you might b123456e special.')

  def test_replace_lines(self):
    out = run_args(['-f', abcdef_path, 'y/0/0/123456'])
    self.assertEqual(out, '123456\nabcdef\n')
    out = run_args(['-f', abcdef_path, 'y/1/0/123456'])
    self.assertEqual(out, 'abcdef\n123456\n')
    out = run_args(['-f', short_path, 'y/2/0/123456'])
    self.assertEqual(out, 'this is a test\nof this thing here \n123456\nand you might be special.\n')
    out = run_args(['-f', short_path, 'y/1/1/123456'])
    self.assertEqual(out, 'this is a test\n123456\nand you might be special.\n')
    out = run_args(['-f', short_path, 'y/1/2/123456'])
    self.assertEqual(out, 'this is a test\n123456\n')
    out = run_args(['-f', short_path, 'y/0/2/123456'])
    self.assertEqual(out, '123456\nand you might be special.\n')
    
  def test_replace_chars(self):
    out = run_args(['-f', abcdef_path, 'Y/0/0/123456'])
    self.assertEqual(out, '123456abcdef')
    out = run_args(['-f', abcdef_path, 'Y/6/0/123456'])
    self.assertEqual(out, 'abcdef123456')
    out = run_args(['-f', abcdef_path, 'Y/-50/0/123456'])
    self.assertEqual(out, '123456abcdef')
    out = run_args(['-f', abcdef_path, 'Y/10000/0/123456'])
    self.assertEqual(out, 'abcdef123456')
    out = run_args(['-f', abcdef_path, 'Y/2/2/123456'])
    self.assertEqual(out, 'ab123456ef')
    out = run_args(['-f', short_path, 'Y/5/4/123456'])
    self.assertEqual(out, 'this 123456 test\nof this thing here \nand you might be special.')
    out = run_args(['-f', short_path, 'Y/-11/2/123456'])
    self.assertEqual(out, 'this is a test\nof this thing here \nand you might 123456 special.')

  def test_delete_lines(self):
    out = run_args(['-f', abcdef_path, 'd/0/0'])
    self.assertEqual(out, 'abcdef\n')
    out = run_args(['-f', short_path, 'd/2/4/'])
    self.assertEqual(out, 'this is a test\nof this thing here \n')
    out = run_args(['-f', short_path, 'd/0/2/123456'])
    self.assertEqual(out, 'and you might be special.\n')
    
  def test_delete_chars(self):
    out = run_args(['-f', abcdef_path, 'D/2/2'])
    self.assertEqual(out, 'abef')
    out = run_args(['-f', abcdef_path, 'D/3/6'])
    self.assertEqual(out, 'abc')
    out = run_args(['-f', abcdef_path, 'D/0/4'])
    self.assertEqual(out, 'ef')
    out = run_args(['-f', short_path, 'D/5/44'])
    self.assertEqual(out, 'this be special.')
    out = run_args(['-f', short_path, 'D/-32/200'])
    self.assertEqual(out, 'this is a test\nof this thing')

  # def test_bad_regexp(self):
  #   out = run_args(['-f', abcdef_path, 'D/2/2'])
  #   with self.assertRaises(TypeError):
  #     print(out)

    #     self.assertEqual('foo'.upper(), 'FOO')
    #     self.assertTrue('FOO'.isupper())
    #     self.assertFalse('Foo'.isupper())
    #     with self.assertRaises(TypeError):
    #         s.split(2)

if __name__ == '__main__':
    unittest.main()

# 'this is a test\nof this thing here \nand you might be special.'