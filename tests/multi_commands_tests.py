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

class TestMultipleCommands(unittest.TestCase):

  def test_ssss(self):
    out = run_args(['-f', abcdef_path, 's/c/abcdef', 's/c/abcdef', 's/c/abcdef', 's/c/abcdef', 's/c/abcdef'])
    self.assertEqual(out, 'ababababababcdefdefdefdefdefdef\n')

  def test_ais(self):
    out = run_piped(['a/top\nbottom', 'i/1/middle', 's/^/> '], '')
    self.assertEqual(out, '> top\n> middle\n> bottom\n')
    out = run_piped(['a/top\nbottom', 'i/1/mid\ndle', 's/^/> '], '')
    self.assertEqual(out, '> top\n> mid\n> dle\n> bottom\n')

  def test_aiss(self):
    out = run_piped(['a/top\nbottom', 'i/1/middle', 's/^m.*/two\nlines/', 's/^/> '], '')
    self.assertEqual(out, '> top\n> two\n> lines\n> bottom\n')
    out = run_piped(['a/top\nbottom', 'i/1/mid\ndle', 's/^m.*/two\nlines/', 's/^/> '], '')
    self.assertEqual(out, '> top\n> two\n> lines\n> dle\n> bottom\n')

  def test_ss(self):
    out = run_args(['-f', short_path, 's/thing/\n', 's/^/> '])
    self.assertEqual(out, '> this is a test\n> of this \n>  here \n> and you might be special.\n')

  def test_as(self):
    out = run_piped(['a/a\nb\nc', 's/^/> /'], '')
    self.assertEqual(out, '> a\n> b\n> c\n')

  def test_ps(self):
    out = run_piped(['p/a\nb\nc', 's/^/> /'], '')
    self.assertEqual(out, '> a\n> b\n> c\n')

  def test_is(self):
    out = run_piped(['i/1/xx\nyy\nzz', 's/^/> /'], 'a\nb\nc')
    self.assertEqual(out, '> a\n> xx\n> yy\n> zz\n> b\n> c\n')

  def test_ys(self):
    out = run_piped(['y/1/1/xx\nyy\nzz', 's/^/> /'], 'a\nb\nc')
    self.assertEqual(out, '> a\n> xx\n> yy\n> zz\n> c\n')


if __name__ == '__main__':
    unittest.main()
