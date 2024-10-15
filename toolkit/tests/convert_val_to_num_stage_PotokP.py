from unittest import TestCase, main
from toolkit.sdp_lib.controller_management import PotokP
import asyncio


class TestPotokP(TestCase):
    def setUp(self) -> None:
        self.host = PotokP('10.45.154.11', host_id=2)

    def test_convert_val_stage_to_num_stage(self):
        self.assertEqual(self.host.convert_val_stage_to_num_stage('0x1000'), 13)
        self.assertEqual(self.host.convert_val_stage_to_num_stage('@'), 7)


if __name__ == '__main__':
    main()
