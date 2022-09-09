import random
import shutil
from tempfile import mkdtemp
import unittest
import subprocess
import sys
import glob
from io import StringIO
from unittest.mock import patch
import os
from test_utils import *

short_text = 'this is a test\nof this thing here \nand you might be special.'

class TestOptions(unittest.TestCase):

  def test_noop(self):
    out = run_args(['-f', abcdef_path])
    self.assertEqual(out, 'abcdef')
    out = run_args(['--filepath', abcdef_path])
    self.assertEqual(out, 'abcdef')

  def test_noop_norm(self):
    out = run_args(['-f', abcdef_path])
    self.assertEqual(out, 'abcdef')
    out = run_args(['-n', '-f', abcdef_path])
    self.assertEqual(out, 'abcdef\n')
    out = run_args(['--normalize', '-f', abcdef_path])
    self.assertEqual(out, 'abcdef\n')
    out = run_args(['--no-eof', '--normalize', '--filepath', abcdef_path])
    self.assertEqual(out, 'abcdef')

  def test_line_ending(self):
    out = run_args(['-n', '-f', abcdef_path, '--line-ending', '\r'])
    self.assertEqual(out, 'abcdef\r')
    out = run_args(['-n', '-f', abcdef_path, '--line-ending', ':'])
    self.assertEqual(out, 'abcdef:')

  def test_delimiters(self):
    out = run_piped(['S:this:------'], 'this or that, that or this')
    self.assertEqual(out, '------ or that, that or ------')

  def test_normalize(self):
    out = run_args(['-f', abcdef_path, '-n'])
    self.assertEqual(out, 'abcdef\n')

  def test_inplace(self):
    import shutil
    import tempfile
    with tempfile.TemporaryDirectory('_test') as temp_dir:
      temp_path = os.path.join(temp_dir, 'shorty.txt')
      shutil.copy2(short_path, temp_path)
      out = run_args(['-e', '-f', temp_path, 's/[aeiou]/-'])
      text = file_get_contents(temp_path)
      self.assertEqual(text, 'th-s -s - t-st\n-f th-s th-ng h-r- \n-nd y-- m-ght b- sp-c--l.\n')
      out = run_args(['--in-place', '-f', temp_path, 's/[aeiou]/-'])
      text = file_get_contents(temp_path)
      self.assertEqual(text, 'th-s -s - t-st\n-f th-s th-ng h-r- \n-nd y-- m-ght b- sp-c--l.\n')

  def test_ignore_case(self):
    out = run_args(['-i', '-f', short_path, 's/[aeIOU]/-'])
    self.assertEqual(out, 'th-s -s - t-st\n-f th-s th-ng h-r- \n-nd y-- m-ght b- sp-c--l.\n')
    out = run_args(['--ignore-case', '-f', short_uc_path, 's/[aeiOU]/-'])
    self.assertEqual(out, 'TH-S -S - T-ST\n-F TH-S TH-NG H-R- \n-ND Y-- M-GHT B- SP-C--L.\n')
    out = run_args(['--ignore-case', '-f', short_path, 'g/thing|SPECIAL/-'])
    self.assertEqual(out, 'of this thing here \nand you might be special.\n')
    out = run_args(['-f', short_uc_path, 'g/thIS', '-i'])
    self.assertEqual(out, 'THIS IS A TEST\nOF THIS THING HERE \n')

  def test_fixed(self):
    out = run_piped(['--fixed', 'S/+++++/-----'], '#####&&&&&+++++((((()))))')
    self.assertEqual(out, '#####&&&&&-----((((()))))')
    out = run_piped(['-F', 'S/+++++/-----'], '#####&&&&&+++++((((()))))')
    self.assertEqual(out, '#####&&&&&-----((((()))))')
    out = run_piped(['S/#+/-----'], '#####&&&&&+++++((((()))))')
    self.assertEqual(out, '-----&&&&&+++++((((()))))')

  def test_multiline(self):
    out = run_args(['-f', short_path, r'S/^/===> '])
    self.assertEqual(out, '===> this is a test\nof this thing here \nand you might be special.')
    out = run_args(['-m', '-f', short_path, r'S/^\W*/===> '])
    self.assertEqual(out, '===> this is a test\n===> of this thing here \n===> and you might be special.')
    out = run_args(['--multiline', '-f', short_path, r'S/^\W*/===> '])
    self.assertEqual(out, '===> this is a test\n===> of this thing here \n===> and you might be special.')

  def test_dotall(self):
    out = run_piped(['S/##.*&&/-----'], '#####\n&&&&&\n*****\n((((()))))')
    self.assertEqual(out, '#####\n&&&&&\n*****\n((((()))))')
    out = run_piped(['--dotall', 'S/##.*&&/-----'], '#####\n&&&&&\n*****\n((((()))))')
    self.assertEqual(out, '-----\n*****\n((((()))))')
    out = run_piped(['-d', 'S/##.*&&/-----'], '#####\n&&&&&\n*****\n((((()))))')
    self.assertEqual(out, '-----\n*****\n((((()))))')

  def test_ascii(self):
    out = run_piped(['S/\s/-'], ' \t\n\r\xA0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a')
    self.assertEqual(out, '----------------')
    out = run_piped(['--ascii', 'S/\s/-'], ' \t\n\r\xA0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a')
    self.assertEqual(out, '----\xA0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a')
    out = run_piped(['-a', 'S/\s/-'], ' \t\n\r\xA0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a')
    self.assertEqual(out, '----\xA0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a')

  def test_backup(self):
    for opt in ['-b', '--backup-path']:
      num = random.randint(1000000, 9999999)
      temp_inplace = f'/tmp/temp_inplace_test_{num}.txt'
      temp_path = f'/tmp/backup_test_{num}'
      shutil.copy2(short_path, temp_inplace)
      before = file_get_contents(temp_inplace)
      self.assertEqual(short_text, before)
      run_args(['-e', opt, temp_path, '-f', temp_inplace, 's/[aeiou]/-'])
      file_list = glob.glob(os.path.join(temp_path, '*'))
      self.assertEqual(len(file_list), 1)
      backup = file_get_contents(file_list[0])
      self.assertEqual(before, backup)
      after = file_get_contents(temp_inplace)
      self.assertNotEqual(before, after)

  def test_no_eof(self):
    out = run_piped(['s/[aeiou]/-'], 'abcdefghi\njklmnopqrs\ntuvwxyz')
    self.assertEqual(out, '-bcd-fgh-\njklmn-pqrs\nt-vwxyz\n')
    out = run_piped(['--no-eof', 's/[aeiou]/-'], 'abcdefghi\njklmnopqrs\ntuvwxyz')
    self.assertEqual(out, '-bcd-fgh-\njklmn-pqrs\nt-vwxyz')
    out = run_piped(['-Z', 's/[aeiou]/-'], 'abcdefghi\njklmnopqrs\ntuvwxyz')
    self.assertEqual(out, '-bcd-fgh-\njklmn-pqrs\nt-vwxyz')

  def test_no_eof(self):
    out = run_piped(['s/[aeiou]/-'], 'abcdefghijklmnopqrstuvwxyz\nabcdefghijklmnopqrstuvwxyz')
    self.assertEqual(out, '-bcd-fgh-jklmn-pqrst-vwxyz\n-bcd-fgh-jklmn-pqrst-vwxyz\n')
    out = run_piped(['-M', '3', 's/[aeiou]/-'], 'abcdefghijklmnopqrstuvwxyz\nabcdefghijklmnopqrstuvwxyz')
    self.assertEqual(out, '-bcd-fgh-jklmnopqrstuvwxyz\nabcdefghijklmnopqrstuvwxyz\n')
    out = run_piped(['--max-sub', '8', 's/[aeiou]/-'], 'abcdefghijklmnopqrstuvwxyz\nabcdefghijklmnopqrstuvwxyz')
    self.assertEqual(out, '-bcd-fgh-jklmn-pqrst-vwxyz\n-bcd-fgh-jklmnopqrstuvwxyz\n')
    out = run_piped(['-M', '6', '-L', '4', 's/[aeiou]/-'], 'abcdefghijklmnopqrstuvwxyz\nabcdefghijklmnopqrstuvwxyz')
    self.assertEqual(out, '-bcd-fgh-jklmn-pqrstuvwxyz\n-bcd-fghijklmnopqrstuvwxyz\n')
    out = run_piped(['--line-max-sub', '2', 's/[aeiou]/-'], 'abcdefghijklmnopqrstuvwxyz\nabcdefghijklmnopqrstuvwxyz')
    self.assertEqual(out, '-bcd-fghijklmnopqrstuvwxyz\n-bcd-fghijklmnopqrstuvwxyz\n')

if __name__ == '__main__':
    unittest.main()
