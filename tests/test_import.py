import unittest


class ImportTests(unittest.TestCase):
    def test_import_spine(self):
        import spine

        self.assertEqual(spine.__version__, "0.0.0")
