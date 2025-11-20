import logging
from unittest.mock import (
    patch, call, Mock
)
from pytest import (
    raises, fixture
)

from kiwi.partitioner.gpt import PartitionerGpt

from kiwi.exceptions import KiwiPartitionerGptFlagError


class TestPartitionerGpt:
    @fixture(autouse=True)
    def inject_fixtures(self, caplog):
        self._caplog = caplog

    def setup(self):
        disk_provider = Mock()
        disk_provider.get_device = Mock(
            return_value='/dev/loop0'
        )
        self.partitioner = PartitionerGpt(disk_provider)

    def setup_method(self, cls):
        self.setup()

    @patch('kiwi.partitioner.gpt.Command.run')
    @patch('kiwi.partitioner.gpt.PartitionerGpt.set_flag')
    def test_create(self, mock_flag, mock_command):
        self.partitioner.create('name', 100, 't.linux', ['t.csm'])
        mock_command.assert_called_once_with(
            ['sgdisk', '-n', '1:0:+100M', '-c', '1:name', '/dev/loop0']
        )
        call = mock_flag.call_args_list[0]
        assert mock_flag.call_args_list[0] == \
            call(1, 't.linux')
        call = mock_flag.call_args_list[1]
        assert mock_flag.call_args_list[1] == \
            call(1, 't.csm')

    @patch('kiwi.partitioner.gpt.Command.run')
    @patch('kiwi.partitioner.gpt.PartitionerGpt.set_flag')
    def test_create_custom_start_sector(self, mock_flag, mock_command):
        disk_provider = Mock()
        disk_provider.get_device = Mock(
            return_value='/dev/loop0'
        )
        partitioner = PartitionerGpt(disk_provider, 4096)
        partitioner.create('name', 100, 't.linux', ['t.csm'])
        partitioner.create('name', 100, 't.linux', ['t.csm'])
        mock_command.assert_has_calls([
            call([
                'sgdisk', '-n', '1:4096:+100M', '-c', '1:name', '/dev/loop0'
            ]),
            call([
                'sgdisk', '-n', '2:0:+100M', '-c', '2:name', '/dev/loop0'
            ])
        ])
        assert mock_flag.call_args_list[0] == \
            call(1, 't.linux')
        assert mock_flag.call_args_list[1] == \
            call(1, 't.csm')

    @patch('kiwi.partitioner.gpt.Command.run')
    @patch('kiwi.partitioner.gpt.PartitionerGpt.set_flag')
    def test_create_all_free(self, mock_flag, mock_command):
        self.partitioner.create('name', 'all_free', 't.linux')
        mock_command.assert_called_once_with(
            ['sgdisk', '-n', '1:0:0', '-c', '1:name', '/dev/loop0']
        )

    def test_set_flag_invalid(self):
        with raises(KiwiPartitionerGptFlagError):
            self.partitioner.set_flag(1, 'foo')

    @patch('kiwi.partitioner.gpt.Command.run')
    def test_set_flag(self, mock_command):
        self.partitioner.set_flag(1, 't.csm')
        mock_command.assert_called_once_with(
            ['sgdisk', '-t', '1:EF02', '/dev/loop0']
        )

    def test_set_flag_ignored(self):
        with self._caplog.at_level(logging.WARNING):
            self.partitioner.set_flag(1, 'f.active')

    @patch('kiwi.partitioner.gpt.Command.run')
    def test_set_hybrid_mbr(self, mock_command):
        self.partitioner.partition_id = 5
        self.partitioner.set_hybrid_mbr()
        mock_command.assert_called_once_with(
            ['sgdisk', '-h', '1:2:3', '/dev/loop0']
        )

    @patch('kiwi.partitioner.gpt.Command.run')
    def test_set_mbr(self, mock_command):
        command_output = Mock()
        command_output.output = '...(EFI System)'
        self.partitioner.partition_id = 4
        mock_command.return_value = command_output
        self.partitioner.set_mbr()
        assert mock_command.call_args_list == [
            call(['sgdisk', '-i=1', '/dev/loop0']),
            call(['sgdisk', '-i=2', '/dev/loop0']),
            call(['sgdisk', '-i=3', '/dev/loop0']),
            call(['sgdisk', '-i=4', '/dev/loop0']),
            call(['sgdisk', '-t', '4:8300', '/dev/loop0']),
            call(['sgdisk', '-m', '1:2:3:4', '/dev/loop0'])
        ]

    @patch('kiwi.partitioner.gpt.Command.run')
    def test_resize_table(self, mock_command):
        self.partitioner.resize_table(42)
        mock_command.assert_called_once_with(
            ['sgdisk', '--resize-table', '42', '/dev/loop0']
        )

    @patch('kiwi.partitioner.gpt.Command.run')
    def test_set_uuid(self, mock_Command_run):
        self.partitioner.set_uuid(42, 'ID')
        mock_Command_run.assert_called_once_with(
            ['sgdisk', '--typecode', '42:ID', '/dev/loop0']
        )

    @patch('kiwi.partitioner.gpt.Command.run')
    def test_create_ec2_layout_root_gets_partition_id_1(self, mock_command):
        """Test EC2 layout assigns partition ID 1 to root partitions"""
        self.partitioner.set_ec2_part_layout(True)
        
        # Create EFI partition first
        efi_id = self.partitioner.create('p.UEFI', 100, 't.efi')
        
        # Create root partition - should get ID 1 even though created second
        root_id = self.partitioner.create('p.lxroot', 1000, 't.linux')
        
        assert root_id == 1, f"Root partition should get ID 1 in EC2 layout, got {root_id}"
        assert efi_id == 2, f"EFI partition should get ID 2 in EC2 layout, got {efi_id}"
