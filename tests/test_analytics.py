import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from src.analytics_data import load_data, building_summary, parse_remaining_lease
from src.analytics_charts import lease_heatmap, time_bubbles

ROOT=Path(__file__).resolve().parents[1]

class DataIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=pd.read_csv(ROOT/'data/resale_flat_prices.csv')
        cls.df=load_data(ROOT/'data/resale_flat_prices.csv')

    def test_no_dropped_or_multiplied_records(self):
        self.assertEqual(len(self.df),242454)
        self.assertEqual(len(self.df),len(self.raw))
        self.assertTrue(self.df.record_id.is_unique)
        np.testing.assert_array_equal(self.df.resale_price,self.raw.resale_price)
        self.assertEqual(self.raw.duplicated().sum(),318)

    def test_unlocated_records_stay_unlocated(self):
        self.assertEqual(self.df.has_coordinates.sum(),36290)
        self.assertEqual(self.df.has_spatial.sum(),36290)
        self.assertEqual(self.df.loc[self.df.has_coordinates,'address'].nunique(),1462)
        self.assertTrue(self.df.loc[~self.df.has_spatial,'min_mrt_dist_km'].isna().all())

    def test_price_and_lease_units(self):
        self.assertAlmostEqual(parse_remaining_lease('61 years 04 months'),61+4/12)
        self.assertEqual(parse_remaining_lease('60 years'),60)
        self.assertTrue(np.isnan(parse_remaining_lease('unknown')))
        self.assertAlmostEqual(self.df.iloc[0].price_per_sqm,232000/44)
        self.assertTrue(self.df.remaining_lease_years.notna().all())
        self.assertNotIn('depreciation_per_year',self.df.columns)
        self.assertNotIn('sora_rate',self.df.columns)

    def test_building_medians_are_from_transactions(self):
        b=building_summary(self.df)
        self.assertEqual(b.transactions.sum(),36290)
        address=b.iloc[0].address
        self.assertAlmostEqual(b.iloc[0].price_per_sqm,self.df[self.df.address==address].price_per_sqm.median())

    def test_small_cells_suppressed(self):
        fig,a=lease_heatmap(self.df,30)
        self.assertEqual(a.n.sum(),242454)
        self.assertTrue(np.isnan(np.array(fig.data[0].z,dtype=float)[0,0]))

    def test_animation_identity_and_observed_counts(self):
        fig,a=time_bubbles(self.df,30)
        self.assertGreater(len(fig.frames),1)
        names=[trace.name for trace in fig.data]
        for frame in fig.frames:
            self.assertEqual([trace.name for trace in frame.data],names)
            for trace in frame.data:
                rows=a[(a.quarter==frame.name)&(a.town==trace.name)]
                self.assertEqual(len(trace.x),len(rows))
                if len(rows):
                    self.assertAlmostEqual(trace.y[0],rows.iloc[0].price_per_sqm)
        self.assertEqual(a.transactions.sum(),self.df.groupby(['quarter','town']).size().loc[lambda s:s>=30].sum())

if __name__=='__main__':
    unittest.main()
