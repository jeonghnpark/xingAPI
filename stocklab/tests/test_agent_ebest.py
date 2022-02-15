import unittest
from stocklab.agent.ebest import EBest

import inspect
import time
import pandas as pd
import matplotlib.pyplot as plt


class TestEbest(unittest.TestCase):
    def setUp(self):
        self.ebest = EBest("DEMO")
        self.ebest.login()

    def _test_get_current_call_price_by_code(self):
        print(inspect.stack()[0][3])
        result = self.ebest.get_current_call_price_by_code("005930")
        print(f"price of 005930 is {result[0]['price']}")

    def _test_get_code_list(self):
        print(inspect.stack()[0][3])  # test명
        all_result = self.ebest.get_code_list("ALL")
        assert all_result is not None
        kosdaq_result = self.ebest.get_code_list("KOSDAQ")
        assert kosdaq_result is not None
        # kospi_result = self.ebest.get_code_list("KOSPI")
        # assert kospi_result is not None
        try:
            error_result = self.ebest.get_code_list("kospi")
        except:
            error_result = None
        assert error_result is None

        # print(f"result : ALL {len(all_result)} KOSPI {len(kospi_result)} KOSDAQ {len(kosdaq_result)}")
        print(f"result : ALL {len(all_result)}  KOSDAQ {len(kosdaq_result)}")

    def _test_historical_closing_price(self):
        closing = self.ebest.get_historical_closing_price('005930', startdate='20100101', enddate='20220107')
        df_closing = pd.DataFrame(closing)
        type(df_closing)
        df_closing['close'] = pd.to_numeric(df_closing['close'], errors='coerce')
        df_closing['date'] = pd.to_datetime(df_closing['date'], errors='coerce')

        # MA
        ma_range = [5, 25, 120, 250]
        # ma_color = ['red', 'yellow', 'pink', 'black']
        for i in range(len(ma_range)):
            df_closing[f"ma{ma_range[i]}"] = df_closing['close'].rolling(window=ma_range[i]).mean()

        print(df_closing.head())
        ### plot test
        ax = plt.gca()
        df_closing.plot(kind='line', x='date', y='close', ax=ax)

        for i in range(len(ma_range)):
            df_closing.plot(kind='line', x='date', y=f'ma{ma_range[i]}', ax=ax)

        plt.show()

    def test_get_stock_price_by_code(self):
        close = self.ebest.get_stock_price_by_code('005930', 1, "2")
        assert close is not None
        print(close)

    def tearDown(self):
        self.ebest.logout()


if __name__ == "__main__":
    unittest.main()
