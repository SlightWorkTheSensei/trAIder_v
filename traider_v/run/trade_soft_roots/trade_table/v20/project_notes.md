project_notes.md

00done00 --
() - 
------------------------------------------------------------------------------

----Problems:

(e) - 

------------------------------------------------------------------------------


----Suggested fixes:


(c.1) - Perhaps consider having the backtest results named after something like the datetime and its ticker, and then having the backtest results moved to another folder when the user wants to change the parameters for the backtest.

(e) - 
------------------------------------------------------------------------------


----Completed :

00done00 -- (a) - When app.py runs, there are 7 days worth of 1 minute data saved from the current datetime. Or 6770 rows of data and not 24,000 for futures and a around 12,000 for stocks. 
00done00 -- (a) - Ensure that chunks of 7 days worth of data are being concatonated into one csv for that ticker


00done00 -- (d) - array for stop loss sizes needs to include more like  ($0.01,  $0.05, $0.10, $0.20)
00done00 -- (d) - in form.html and in the app.py there must be more elements added to the stop loss size arrays.


00done00 -- (c) - If user wants to go back and try new parameters, then the backtest results csv is not updated and so the results.html prints the same table over and over with no changes with respect to the user's parameters. Thus the user has to delete the csv files to remake them based on the parameters. 
00done00 --(c) - Whenever the user submits a ticker be backtested check if there is already a csv for that ticker's price data. If there is, then add the new price data to it. If not, then make a new csv for that price data. Then check if there already exists a backtest results for that ticker. If there does, then overwrite the csv with the new backtest results. 

00done00 -- (b) - Sometimes If backtest logic is ran with parameters of only open, high, low, or close, then it will return nan for net profit and loss and unrealized gains and losses. NAN appears when the intervals are larger than 1 minute - but not for every row. 
------If the user chooses only open, high, low, or close instead of open-high, open-low, close-high, close-low, then all net profit and unrealized gains/losses will return as nan. 
00done00 -- (b) - Ensure that backtest logic for the open-high, open-low, close-high, close-low doesnt overwrite the logic for only open, high, low, or close backtesting. Could be a problem with run backtests vectorized and run single backtest vectorized? Unsure upon first read thru



------------------------------------------------------------------------------

