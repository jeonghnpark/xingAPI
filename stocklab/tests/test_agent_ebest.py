import unittest
from stocklab.agent.ebest import EBest

import inspect
import time


class TestEbest(unittest.TestCase):
    def setUp(self):
        self.ebest = EBest("DEMO")
        self.ebest.login()

    # def test_get_current_call_price_by_code(self):
    #     print(inspect.stack()[0][3])
    #     result = self.ebest.get_current_call_price_by_code("005930")
    #     assert result
    #     result = 1
    #     print(result)

    def test_get_code_list(self):
        print(inspect.stack()[0][3])  # test명
        all_result = self.ebest.get_code_list("ALL")
        assert all_result is not None
        kosdaq_result = self.ebest.get_code_list("KOSDAQ")
        assert kosdaq_result is not None
        # kospi_result = self.ebest.get_code_list("KOSPI")
        # assert kospi_result is not None
        # try:
        #     error_result = self.ebest.get_code_list("kospi")
        # except:
        #     error_result = None
        # assert error_result is None

        # print(f"result : ALL {len(all_result)} KOSPI {len(kospi_result)} KOSDAQ {len(kosdaq_result)}")
        print(f"result : ALL {len(all_result)}  KOSDAQ {len(kosdaq_result)}")

    def tearDown(self):
        self.ebest.logout()


if __name__ == "__main__":
    unittest.main()
