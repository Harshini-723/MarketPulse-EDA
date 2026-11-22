import unittest
import pandas as pd
from modules.analysis import (
    detect_columns, dataset_profile, prepare_dates, percentage_table,
    contingency_table, resample_series
)

class MarketPulseTests(unittest.TestCase):
    def setUp(self):
        self.df=pd.DataFrame({
            "Date":["2025-01-01","2025-01-02","2025-01-08","2025-02-01"],
            "Commodity":["Tomato","Onion","Tomato","Onion"],
            "Market":["A","A","B","B"],
            "Price":[20,30,24,28],
            "Arrival":[100,120,90,130]
        })

    def test_detection(self):
        d=detect_columns(self.df)
        self.assertIn("Price",d["numeric"])
        self.assertIn("Commodity",d["categorical"])
        self.assertIn("Date",d["dates"])

    def test_profile(self):
        p=dataset_profile(self.df)
        self.assertEqual(len(p),5)
        self.assertIn("Detected as",p.columns)

    def test_date_parse(self):
        parsed,n=prepare_dates(self.df,"Date")
        self.assertEqual(n,4)
        self.assertIn("_date",parsed.columns)

    def test_percentage(self):
        p=percentage_table(self.df,"Commodity")
        self.assertAlmostEqual(p["Percentage"].sum(),100)

    def test_contingency(self):
        t=contingency_table(self.df,"Commodity","Market")
        self.assertEqual(int(t.to_numpy().sum()),4)
        pct=contingency_table(self.df,"Commodity","Market","Row percentages")
        self.assertAlmostEqual(float(pct.loc["Tomato"].sum()),100)

    def test_resampling(self):
        parsed,_=prepare_dates(self.df,"Date")
        out=resample_series(parsed,"Price","Monthly","Mean")
        self.assertEqual(len(out),2)
        self.assertIn("Value",out.columns)

if __name__=="__main__":
    unittest.main()
