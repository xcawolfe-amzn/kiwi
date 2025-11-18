#!/usr/bin/env python3

"""
Test to validate partition ID mapping for EC2 layout across all partitioners
"""

import unittest
from unittest.mock import Mock, patch

from kiwi.partitioner.gpt import PartitionerGpt
from kiwi.partitioner.msdos import PartitionerMsdos
from kiwi.partitioner.dasd import PartitionerDasd


class MockDeviceProvider:
    def get_device(self):
        return '/dev/loop0'


class TestPartitionIDMapping(unittest.TestCase):

    @patch('kiwi.partitioner.gpt.Command.run')
    def test_gpt_partition_id_mapping(self, mock_command):
        """Test GPT partitioner returns correct partition IDs"""
        partitioner = PartitionerGpt(MockDeviceProvider())
        partitioner.set_ec2_layout(True)
        
        # Test non-root partition gets ID 2 (skips reserved ID 1)
        efi_id = partitioner.create('p.UEFI', 100, 't.efi')
        self.assertEqual(efi_id, 2)
        
        # Test root partition gets ID 1
        root_id = partitioner.create('p.lxroot', 'all_free', 't.linux')
        self.assertEqual(root_id, 1)

    @patch('kiwi.partitioner.msdos.Command.run')
    def test_msdos_partition_id_mapping(self, mock_command):
        """Test MSDOS partitioner returns correct partition IDs"""
        partitioner = PartitionerMsdos(MockDeviceProvider())
        partitioner.set_ec2_layout(True)
        
        # Test non-root partition gets ID 2
        boot_id = partitioner.create('p.lxboot', 500, 't.linux')
        self.assertEqual(boot_id, 2)
        
        # Test root partition gets ID 1
        root_id = partitioner.create('p.lxroot', 'all_free', 't.linux')
        self.assertEqual(root_id, 1)

    @patch('kiwi.partitioner.dasd.Command.run')
    def test_dasd_partition_id_mapping(self, mock_command):
        """Test DASD partitioner returns correct partition IDs"""
        partitioner = PartitionerDasd(MockDeviceProvider())
        partitioner.set_ec2_layout(True)
        
        # Test non-root partition gets ID 2
        spare_id = partitioner.create('p.spare', 1000, 't.linux')
        self.assertEqual(spare_id, 2)
        
        # Test root partition gets ID 1
        root_id = partitioner.create('p.lxroot', 'all_free', 't.linux')
        self.assertEqual(root_id, 1)

    def test_normal_layout_unchanged(self):
        """Test normal layout still works with sequential IDs"""
        partitioner = PartitionerGpt(MockDeviceProvider())
        # Don't enable EC2 layout
        
        with patch('kiwi.partitioner.gpt.Command.run'):
            id1 = partitioner.create('p.UEFI', 100, 't.efi')
            id2 = partitioner.create('p.lxroot', 'all_free', 't.linux')
            
        self.assertEqual(id1, 1)
        self.assertEqual(id2, 2)


if __name__ == '__main__':
    unittest.main()
