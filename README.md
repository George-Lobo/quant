# quant

Building a platform for quant trading from scratch. Initial focus on Statistical Arbitrage using prices and relative returns. GetStockData.py should contain the bulk of the work so far.

TO DOs:

- Fix (?) negatively correlated stocks in check_arbitrage_opps (already added SPY, now need to count it into the returns)
- Implement a test for opportunities that seem to be maintaining a high z-score for some time.
- Analyze histograms of returns to try and find hints about distributions.


FUTURE:

- construct_pair_df: treat ratios of series to avoid infs and nans; create ratio columns
- check_stationarity: implement other methods besides ADF; only be called inside another function
- Function that receives current_date and analyzes if an investment opportunity arose in this date; must return True or False;
- stop_loss(loss)
- add Kalman Filter

Useful links:

- https://ghannami.com/the-art-of-statistical-arbitrage%E2%80%8A-%E2%80%8Aan-overview/
- https://stackoverflow.com/questions/47349422/how-to-interpret-adfuller-test-results
- 
