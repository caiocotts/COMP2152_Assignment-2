"""
Unit Tests for Assignment 2 — Port Scanner
"""

import unittest

from assignment2_101571045 import PortScanner
from assignment2_101571045 import common_ports


# TODO: Import your classes and common_ports from assignment2_studentID
# from assignment2_studentID import PortScanner, common_ports


class TestPortScanner(unittest.TestCase):

    def test_scanner_initialization(self):
        """Test that PortScanner initializes with correct target and empty results list."""
        # TODO: Create a PortScanner with target "127.0.0.1"
        # TODO: Assert scanner.target equals "127.0.0.1"
        # TODO: Assert scanner.scan_results is an empty list
        ps = PortScanner('127.0.0.1')
        self.assertEqual(ps.target, '127.0.0.1')
        self.assertEqual(ps.scan_results, [])

    def test_get_open_ports_filters_correctly(self):
        """Test that get_open_ports returns only Open ports."""
        # TODO: Create a PortScanner object
        # TODO: Manually add these tuples to scanner.scan_results:
        #   (22, "Open", "SSH"), (23, "Closed", "Telnet"), (80, "Open", "HTTP")
        # TODO: Call get_open_ports() and assert the returned list has exactly 2 items
        ps = PortScanner('127.0.0.1')
        ps.scan_results = [(22, "Open", "SSH"), (23, "Closed", "Telnet"), (80, "Open", "HTTP")]
        open_ports = ps.get_open_ports()
        self.assertEqual(len(open_ports), 2)

    def test_common_ports_dict(self):
        """Test that common_ports dictionary has correct entries."""
        # TODO: Assert common_ports[80] equals "HTTP"
        # TODO: Assert common_ports[22] equals "SSH"
        self.assertEqual(common_ports[80], "HTTP")
        self.assertEqual(common_ports[22], "SSH")

    def test_invalid_target(self):
        """Test that setter rejects empty string target."""
        # TODO: Create a PortScanner with target "127.0.0.1"
        # TODO: Try setting scanner.target = "" (empty string)
        # TODO: Assert scanner.target is still "127.0.0.1"
        ps = PortScanner('127.0.0.1')
        ps.target = ''
        self.assertEqual(ps.target, '127.0.0.1')


if __name__ == "__main__":
    unittest.main()
