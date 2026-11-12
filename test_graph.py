import unittest
from rpm_graph import parse_repodata 
import mock 

class TestGraph(unittest.TestCase):
    def test_parse(self):
        mock_xml = b'<package><name>pkg1</name><requires><reqname>dep1</reqname></requires></package>'
        self.assertEqual(len(graph.nodes()), 1)

if __name__ == '__main__':
    unittest.main()