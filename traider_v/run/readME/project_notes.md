
00done00 --
() - 
------------------------------------------------------------------------------

----Problems:

(F) - In table or graphic, allow the user to choose intervals of time to specifiy backtesting

(G) - Create a sort of histoplot or scatterplot to showcase which plans result in net profitability

(H) - There has been a problem for quite some time with certain plans not being backtested. 


(J) - What if we used average trading range mixed with the levels AND the recent backtest summary compared to the larger dataset backtest summary aka Trade Table to decide conditions to take which kinds of trade management plans?

------------------------------------------------------------------------------


----Suggested fixes:


(c.1) - Perhaps consider having the backtest results named after something like the datetime and its ticker, and then having the backtest results moved to another folder when the user wants to change the parameters for the backtest.

(e) - 

(e.1) - 

(F) - Perhaps, allow the user in the html of the table graphic to choose which timeframes they want, then collect all of the price data, and then use python with csv library to delete the time signatures that are not from the interval requested by the user, then have the backtests ran on the remaining data. 

(G) - Use the backtest results csv as a reference to simply plot the plans by their variable? So by net profit, by net loss, so on and so forth for each quantitive variable. 

(H) - Perhaps consider using something like c++ to run algorithms for backtested more elabortaly than python

(J) - The idea is that we would be able to see if the either support or resistance are stronger for the price action, then determine what is then average trading range for each timeframe and the most profitable plan for the recent time interval. We would then have a summary that suggest something like "Current market condition: Strong/Weak Resistance/Support, Average Trading Range for 1m, 15m, 60m, daily, most profitable trading plans" I  suppose the idea would be to determine which plans are more preferable based on the average trading range. Essenentially we want to establish confirmation through the price action, volumetric commitment, average trading range, and success of trading plans within those trading ranges. 

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

00done00 -- (e.1) - Trade graphic should also include a sort of heatmap or indication that a the specified plan has run its course. Such is the case where there is a grouping of successful trades in an area. 

00done00 -- (e) - Trade graphic should allow the user to enter the reward to risk ratio to backtest

00done00 -- (I) - No documentation or guide for project 
00done00 -- (I) - organize project directory and write documentation 


------------------------------------------------------------------------------

