# -*- coding: utf-8 -*-
"""
Created on Thu Jun  4 18:40:14 2020

@author: Hp
"""

######################THIS PROJECT WILL WORK ONLY ON QUANTOPIAN#####################


#SIMPLE MOVING AVERAGE CROSSOVER
#Import the Libraries 
from quantopian.research import prices, symbols, returns
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


#CLOSING PRICES FOR PEPSI AND COKE FROM 2018 to MAY 2020

pep_close = prices(assets=symbols('PEP'),
                  start='2018-01-01',
                  end='2020-05-27')
coke_close = prices(assets = symbols('KO'),
                   start='2018-01-01',
                   end='2020-05-27')


#ROLLING WINDOW FOR 15 and 75 DAY MOVING AVERAGE FOR BOTH STOCKS

pep_sma_15 = pep_close.rolling(window=15,min_periods=1,center=False).mean()
coke_sma_15 = coke_close.rolling(window=15,min_periods=1,center=False).mean()
pep_sma_75 = pep_close.rolling(window=75,min_periods=1,center=False).mean()
coke_sma_75 = coke_close.rolling(window=75,min_periods=1,center=False).mean()


#DATA FRAME TO CALCULATE THE SIGNALS (TRADING POINTS)
trade_points = pd.DataFrame()

#INITIALIZING THE DATA FRAME WITH THE 15- & 75-DAY MOVING AVERAGES
trade_points['Pepsi_15_Day_SMA'] = pep_sma_15
trade_points['Pepsi_75_Day_SMA'] = pep_sma_75
trade_points['Coke_15_Day_SMA'] = coke_sma_15
trade_points['Coke_75_Day_SMA'] = coke_sma_75


#CALCULATE THE TRADE SIGNALS OVER THE TIME PERIOD WHEN THERE WAS A CROSSOVER
trade_points['Pepsi_Trade_Signals'] = np.where(trade_points['Pepsi_15_Day_SMA']
                                              > trade_points['Pepsi_75_Day_SMA'],1,0)
trade_points['Coke_Trade_Signals'] = np.where(trade_points['Coke_15_Day_SMA']
                                             > trade_points['Coke_75_Day_SMA'],1,0)

#DIFFERENCE IN TRADE SIGNALS
trade_points['Pepsi_Diff']=trade_points['Pepsi_Trade_Signals'].diff()
trade_points['Coke_Diff']=trade_points['Coke_Trade_Signals'].diff()



#PLOT THE FIGURE OF THE STRATEGIES IN THE SAME GRAPH

fig = plt.figure(figsize=(30,20))

ax1 = fig.add_subplot(111,ylabel='Price')
ax2 = fig.add_subplot(111,ylabel='Price')

pd.DataFrame({'PEPSI':pep_close,
             'COCA-COLA':coke_close,
             'PEPSI 15D SMA': pep_sma_15,
             'PEPSI 75D SMA': pep_sma_75,
             'COKE 15D SMA': coke_sma_15,
             'COKE 75D SMA': coke_sma_75}).plot(title='PEPSI vs COKE',ax=ax1)

ax1.plot(trade_points.loc[trade_points.Pepsi_Diff==1.0].index,
        trade_points.Pepsi_15_Day_SMA[trade_points.Pepsi_Diff==1.0],
        '^',markersize=10,color='g')
ax1.plot(trade_points.loc[trade_points.Pepsi_Diff==-1.0].index,
        trade_points.Pepsi_15_Day_SMA[trade_points.Pepsi_Diff==-1.0],
        'v',markersize=10,color='r')

ax2.plot(trade_points.loc[trade_points.Coke_Diff==1.0].index,
        trade_points.Coke_15_Day_SMA[trade_points.Coke_Diff==1.0],
        '^',markersize=10,color='g')
ax2.plot(trade_points.loc[trade_points.Coke_Diff==-1.0].index,
        trade_points.Coke_15_Day_SMA[trade_points.Coke_Diff==-1.0],
        'v',markersize=10,color='r')

############################################----BACKTEST----##################################################

#CREATING A VIRTUAL PORTFOLIO WITH $500,000 as CAPITAL WITH WEIGHTED INVESTMENTS IN PEPSI AND COKE

capital = float(500000)

#INITIALIZE THE POSITIONS IN A DATA FRAME
pepsiPosition = pd.DataFrame(index=trade_points.index).fillna(0.0)
cokePosition = pd.DataFrame(index=trade_points.index).fillna(0.0)

#BUYING 300 STOCKS OF PEPSI AND SELLING 300 STOCKS OF COKE
pepsiPosition['Pepsi_In_USD']=300*trade_points['Pepsi_Trade_Signals']
cokePosition['Coke_In_USD']=-300*trade_points['Coke_Trade_Signals']

#INITIALIZING THE PORTFOLIO
portfolio = pepsiPosition.multiply(pep_close,axis=0)

#TOTAL INVESTMENT
difference = pepsiPosition.diff()+cokePosition.diff()

#HOLDINGS THROUGHOUT THE TIME PERIOD
portfolio['holdings'] = pepsiPosition.multiply(pep_close,axis=0).sum(axis=1).add(
    cokePosition.multiply(coke_close,axis=0).sum(axis=1),fill_value=0)

#CASH THROUGHOUT THE TIME PERIOD
portfolio['cash'] = capital - ((difference.multiply(pep_close,axis=0)).sum(axis=1).cumsum()+
                              (difference.multiply(coke_close,axis=0)).sum(axis=1).cumsum())

#CALCULATING THE TOTAL VALUE AND RETURN OF THE INVESTMENT OVER THE TIME
portfolio['total'] = portfolio['cash'] + portfolio['holdings']
portfolio['returns'] = portfolio['total'].pct_change()

#DELETING THE UNNCESSARY COLUMNS
del portfolio['Pepsi_In_USD']
