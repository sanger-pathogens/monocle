import unittest
import DataSources.monocledb

monocledb = DataSources.monocledb.MonocleDB()

class MonocleDBTest(unittest.TestCase):
   
   def setUp(self):
      monocledb = DataSources.monocledb.MonocleDB()

      self.db = DataSources.monocledb.MonocleDB()

   def test_init(self):
      self.assertIsInstance(self.db,DataSources.monocledb.MonocleDB)
