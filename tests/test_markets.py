import unittest

from aggregation.markets import Trade, aggregate_trades, brier, signed_yes_exposure


class MarketAggregationTests(unittest.TestCase):
    def test_trade_signs_share_yes_axis(self):
        base = dict(wallet="w", timestamp=1, size=2)
        self.assertEqual(signed_yes_exposure(Trade(**base, side="BUY", outcome_index=0)), 2)
        self.assertEqual(signed_yes_exposure(Trade(**base, side="SELL", outcome_index=0)), -2)
        self.assertEqual(signed_yes_exposure(Trade(**base, side="BUY", outcome_index=1)), -2)
        self.assertEqual(signed_yes_exposure(Trade(**base, side="SELL", outcome_index=1)), 2)

    def test_repeated_trades_do_not_add_wallet_votes(self):
        trades = [
            Trade("a", 1, 100, "BUY", 0),
            Trade("a", 2, 100, "BUY", 0),
            Trade("b", 3, 1, "BUY", 1),
            Trade("c", 4, 1, "BUY", 1),
        ]
        result = aggregate_trades(trades, cutoff=10)
        self.assertAlmostEqual(result.one_wallet, 1 / 3)
        self.assertGreater(result.exposure_weighted, 0.98)

    def test_correlated_wallets_form_one_component(self):
        trades = []
        for wallet in ("a", "b"):
            for hour in (1, 2, 3):
                trades.append(Trade(wallet, hour * 3600, 1, "BUY", 0))
        trades.append(Trade("c", 4 * 3600, 1, "BUY", 1))
        result = aggregate_trades(trades, cutoff=20_000)
        self.assertEqual(result.wallets, 3)
        self.assertEqual(result.components, 2)
        self.assertEqual(result.dependence_adjusted, 0.5)
        self.assertIsNone(result.abstaining_dependence_adjusted)

    def test_cutoff_blocks_future_trades(self):
        result = aggregate_trades(
            [Trade("early", 10, 1, "BUY", 0), Trade("late", 20, 10, "BUY", 1)],
            cutoff=15,
        )
        self.assertEqual(result.one_wallet, 1.0)
        self.assertEqual(result.wallets, 1)

    def test_brier(self):
        self.assertAlmostEqual(brier(0.8, 1), 0.04)


if __name__ == "__main__":
    unittest.main()
