import os
from pathlib import Path
import unittest
from lib.migration import StateFile, Migration


class TestMigration(unittest.TestCase):
    def setUp(self) -> None:
        self.migration = Migration()

    def test_run(self):
        self.assertTrue(self.migration_state == 'success')


class TestStateFile(unittest.TestCase):
    def setUp(self) -> None:
        test_file = './lib/test/' + "1.1.1.1.json"
        self.state_file = StateFile(test_file)

    def test_read(self):
        """Checks is content of a file dict type or not"""
        self.assertTrue(isinstance(self.state_file.read(), dict))

    def test_write(self):
        """Checks file size change."""
        data = self.state_file.read()
        file_ = Path(self.state_file.file)
        first_size = file_.stat().st_size
        del data["mount_points"]["c:\\"]
        self.state_file.write(data)
        second_size = file_.stat().st_size
        data = self.state_file.read()
        data["mount_points"]["c:\\"] = 12222222
        self.state_file.write(data)
        self.assertTrue(file_.exists() and file_.stat().st_size != 0 and first_size > second_size)

    def test_new(self):
        """Checks new file exists and not empty."""
        data = self.state_file.read()
        file_ = Path(self.state_file.file)
        data["source"]["source_ip"] = "2.2.2.2"
        self.state_file.new(data)
        self.assertTrue(file_.exists() and file_.stat().st_size != 0)
        os.remove("migrations/2.2.2.2.json")

    def TestRemove(self):
        """Creates and remove file."""
        test_file = '2.2.2.2.json'
        with open(test_file, 'w') as file:
            file.write('test')
        file_ = Path(test_file)
        self.state_file.remove(test_file)
        self.assertTrue(not file_.exists())


if __name__ == "__main__":
    unittest.main()
