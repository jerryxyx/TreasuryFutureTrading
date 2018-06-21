"""
    class: BackTestingSystem
    author: Jerry Xia
    email: xyxjerry@gmail.com
    date: 20/Apr/2017
    modules:
     - data input
     - preprocessing
     - PnL relative computing
     - data output
"""



import numpy as np
from datetime import datetime
import pandas as pd


class Positions:
    def __init__(self, positions, startIdx, endIdx):
        self.positions = np.array(positions)
        self.startIdx = startIdx
        self.endIdx = endIdx

    def duration(self):
        return self.endIdx - self.startIdx


class PortPositions:
    def __init__(self, timeSize, numEquities):
        # print(timeSize)
        self.startIdx = 0
        self.endIdx = timeSize - 1
        self.cumPositions = np.zeros((timeSize, numEquities))
        self.numPositions = np.zeros(timeSize)

    # todo: i in range number to number
    # i in df.index[]
    def addPositions(self, positionsChange):
        if (positionsChange.startIdx >= positionsChange.endIdx):
            return
        for i in range(positionsChange.startIdx, positionsChange.endIdx):
            #             print("##################################################")
            #             print(type(positionsChange.positions))
            #             print(type(self.cumPositions[i,:]))
            self.cumPositions[i, :] = self.cumPositions[i, :] + positionsChange.positions
            self.numPositions[i] = self.numPositions[i] + 1

    def maxPosJudge(self, positionsChange, maxPos):
        startIdx = positionsChange.startIdx
        # print(startIdx)
        # print(self.numPositions[startIdx])
        return self.numPositions[startIdx] < maxPos

    def get_cumPositions():
        return self.cumPositions

    def get_numPositions():
        return self.numPositions


class BackTestingSystem:

    def __init__(self, numEquities, pointPrices, tickSizePrices, margins, transactionCostCoeff):
        self.numEquities = numEquities
        if (len(pointPrices) == numEquities):
            self.pointPrices = np.array(pointPrices)
        else:
            print("number of equities unmatch: point prices")
        if (len(tickSizePrices) == numEquities):
            self.tickSizePrices = np.array(tickSizePrices)
        else:
            print("number of equities unmatch: tickSizes")
        if (len(margins) == numEquities):
            self.margins = np.array(margins)
        else:
            print("number of equities unmatch: margins")

        self.transactionCostCoeff = transactionCostCoeff
        # others
        self.PnL = None
        self.transactionCost = None
        self.netPnL = None

    def set_rollDate(self, rollDate):
        self.rollDate = rollDate

    def get_rollDate(self):
        return self.rollDate

    def set_exitUpLevel(self, exitUpLevel):
        self.exitUpLevel = exitUpLevel

    def set_exitDownLevel(self, exitDownLevel):
        self.exitDownLevel

    def set_triggerS(self, triggerS):
        self.triggerS = triggerS

    def set_triggerT(self, triggerT):
        self.triggerT = triggerT

    def get_marginPrices(self):
        return self.margins / self.pointPrices

    def get_tickSizes(self):
        return self.pointPrices * tickSizePrices

    def set_AUM(self, AUM):
        self.AUM = AUM

    def set_rollingStats(self, dfRollingStats):
        self.dfRollingStats = dfRollingStats
        self.df = pd.concat([self.df, self.rollingStats], axis=1)

    def set_maxPoistions(self, maxPositions):
        self.maxPositions = 30

    def set_percentageInvested(self, pctInvest):
        self.percentageInvested = pctInvest

    def set_maxPositions(self, maxPositions):
        self.maxPositions = maxPositions

    def set_exitUpLevel(self, exitUpLevel):
        self.exitUpLevel = exitUpLevel

    def set_exitDownLevel(self, exitDownLevel):
        self.exitDownLevel = exitDownLevel

    def input_data(self, dfPrices, dfDurations, dfOptWeights, dfRollingStats):
        self.dfPrices = dfPrices
        self.dfDurations = dfDurations
        self.dfOptWeights = dfOptWeights
        self.df = pd.concat([self.dfPrices, self.dfDurations, self.dfOptWeights, dfRollingStats], axis=1)

    # todo: delete
    #     def input_whole_data(self,df):
    #         self.df = df

    def get_df(self):
        return self.df

    def time_delta_365(self, timeDelta):
        if (timeDelta.days > 0):
            return timeDelta.days / 365
        else:
            return 0

    def preprocessing(self):

        print("****************************************************************")
        print("Start preprocessing...")
        # basic setting
        self.marginPrices = self.margins / self.pointPrices
        self.maxInitMargin = self.AUM * self.percentageInvested
        self.positionInitMargin = self.maxInitMargin / self.maxPositions
        self.tickSizes = self.pointPrices * self.tickSizePrices
        self.marginPrices = self.margins / self.pointPrices

        # time to maturity
        timeDeltas = self.rollDate - self.df.index
        self.df['TimeToMaturity'] = timeDeltas
        self.df.TimeToMaturity = self.df.TimeToMaturity.apply(self.time_delta_365)
        self.timeToMaturity = self.df.TimeToMaturity
        print(self.df.head())
        # future duration
        futureDurationsColumns = ["dfFutureDuration" + dur_str[8:] for dur_str in self.dfDurations.columns]
        self.dfFutureDurations = pd.DataFrame(index=self.df.index, columns=futureDurationsColumns)
        for index, row in self.dfDurations.iterrows():
            self.dfFutureDurations.loc[index, :] = (row - self.df.TimeToMaturity[index]).values

        # margin unit
        #         self.marginUnit = pd.Series(index = self.df.index, name="MarginUnit")
        #         for index, row in self.dfOptWeights.iterrows():
        #             self.marginUnit[index] = np.inner(np.abs(row.values), self.marginPrices)
        self.marginUnit = self.dfOptWeights.apply(lambda x: np.inner(np.abs(x), self.marginPrices), axis=1)
        self.marginUnit.rename("MarginUnit")

        # national
        self.portNotional = self.positionInitMargin / self.marginUnit
        self.portNotional.rename("PortNotional", inplace=True)

        # positions
        positionsColumns = ["dfPosition" + dur_str[8:] for dur_str in self.dfDurations.columns]
        self.dfPositions = pd.DataFrame(index=self.df.index, columns=positionsColumns)
        for index, row in self.dfOptWeights.iterrows():
            self.dfPositions.loc[index, :] = row.values * self.portNotional[index] / self.pointPrices
        # tick size
        self.portTickSize = self.dfPositions.apply(lambda x: np.inner(np.abs(x), self.tickSizes), axis=1)
        self.portTickSize.rename("PortTickSize", inplace=True)

        # current price
        self.portPrice = pd.Series(index=self.df.index, name="PortPrice")
        for idx in self.df.index:
            self.portPrice[idx] = np.inner(self.dfPrices.loc[idx, :], self.dfOptWeights.loc[idx, :])

        # tick size price
        self.portTickSizePrice = pd.Series(index=self.df.index, name="PortTickSizePrice")
        for idx in self.df.index:
            self.portTickSizePrice[idx] = self.portTickSize[idx] / self.portNotional[idx]

        # z-score
        self.ZScore = pd.Series(index=self.df.index, name="ZScore")
        for idx in self.df.index:
            self.ZScore[idx] = (self.portPrice[idx] - self.df.RollingAvg[idx]) / self.df.RollingStd[idx]

        # t-score
        self.TScore = pd.Series(index=self.df.index, name="TScore")
        for idx in self.df.index:
            self.TScore[idx] = (self.portPrice[idx] - self.df.RollingAvg[idx]) / self.portTickSizePrice[idx]

        # concat all results
        self.df = pd.concat([self.df, self.dfFutureDurations, self.marginUnit, self.portNotional,
                             self.dfPositions, self.portTickSize, self.portPrice, self.portTickSizePrice,
                             self.ZScore, self.TScore], axis=1)

        print("Preprocessing finished!")
        print("****************************************************************")
        return self.df

    def _enterSignal(self, time):
        return self.ZScore[time] <= -self.triggerS and self.TScore[time] <= -self.triggerT and time < self.rollDate

    def _exitTime(self, startTime, rollTime=None):
        #         print("rollTimehere",rollTime)
        positions = self.dfPositions.loc[startTime, :]
        p0 = np.sum(positions.values * self.dfPrices.loc[startTime, :].values * self.pointPrices)
        exitUp = self.exitUpLevel * self.portTickSize[startTime]
        exitDown = self.exitDownLevel * self.portTickSize[startTime]
        startIdx = self.df.index.get_loc(startTime)
        for time in self.df.index[startIdx:]:
            price = np.sum(positions.values * self.dfPrices.loc[time, :].values * self.pointPrices)
            #             print(price)
            #             print(p0)
            if (price - p0 >= exitUp):
                break
            if (price - p0 <= -exitDown):
                break
            #         print(time)

        if (rollTime and time > rollTime):
            #             print("############$$$$$$$$$$$$$$$$$$$$#################")
            #             print("time",time)
            #             print("rolltime",rollTime)
            time = rollTime
        #             print("after changing, time",time)
        #             print("############$$$$$$$$$$$$$$$$$$$$#################")

        return time

    # todo: change misleading name upwards, "port" is the term for portfolio, if not execute, call "df"
    def calculateCumPositions(self):
        print("**************************************************")
        print("start calculate strategy positions")
        self.portPositions = PortPositions(len(self.df.index), self.numEquities)
        for idx, time in enumerate(self.df.index):
            positions = self.dfPositions.iloc[idx, :]
            #             print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            #             print("endtime",self._exitTime(time,self.rollDate))
            #             print("rolltime",self.rollDate)
            #             print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
            endTimeIdx = self.df.index.get_loc(self._exitTime(time, self.rollDate))

            #             print("roll date",self.rollDate)
            positionsChange = Positions(positions, idx, endTimeIdx)
            #             print("positionsChange.positions",positionsChange.positions)
            if (self._enterSignal(time) and time < self.rollDate
                    and self.portPositions.maxPosJudge(positionsChange,
                                                                                                    self.maxPositions)):
                self.portPositions.addPositions(positionsChange)
                print("##########################################")
                print("add positions:", positionsChange.positions)
                print("time:", time)
                print("number of positions:", self.portPositions.numPositions[idx])
                print("startTime:", self.df.index[positionsChange.startIdx])
                print("endTime:", self.df.index[positionsChange.endIdx])
                print("cumPositions:", self.portPositions.cumPositions[idx])
                print("##########################################")
        print("complete calculation")
        print("**************************************************")
        return self.portPositions

    def calculateInitMargin(self):
        portInitMargin = np.inner(np.abs(self.portPositions.cumPositions), self.margins)
        self.portInitMargin = pd.Series(index=self.df.index, data=portInitMargin, name="InitMargin")
        return self.portInitMargin

    def calculateDailyPnL(self):
        self.dailyPnL = pd.Series(index=self.df.index, name="DailyPnL")
        self.dailyPnL[0] = 0
        for idx, time in enumerate(self.df.index[1:]):
            self.dailyPnL[time] = np.sum(self.pointPrices * self.portPositions.cumPositions[idx]
                                         * (self.dfPrices.iloc[idx + 1] - self.dfPrices.iloc[idx]))
        return self.dailyPnL

    def calculateTransactionCost(self):
        self.transactionCost = pd.Series(index=self.df.index, name="TransactionCost")
        self.transactionCost[0] = 0
        for idx, time in enumerate(self.df.index[1:]):
            self.transactionCost[time] = (np.inner(
                np.abs(self.portPositions.cumPositions[idx + 1] - self.portPositions.cumPositions[idx]),
                self.tickSizes) * self.transactionCostCoeff)
        return self.transactionCost

    def calculateDailyNetPnL(self):
        self.netDailyPnL = self.dailyPnL - self.transactionCost
        self.netDailyPnL.name = "DailyNetPnL"
        return self.netDailyPnL

    def calculateCumNetPnL(self):
        self.cumNetPnL = pd.Series(data=np.cumsum(self.netDailyPnL), index=self.df.index, name="CumNetPnL")
        return self.cumNetPnL

    def output_data(self):
        self.preprocessing()
        self.calculateCumPositions()
        self.calculateInitMargin()
        self.calculateDailyPnL()
        self.calculateTransactionCost()
        self.calculateDailyNetPnL()
        self.calculateCumNetPnL()
        dfOutput = pd.concat([self.dfPrices, self.dfOptWeights, self.portNotional,
                              self.dfPositions, self.portPrice, self.portInitMargin,
                              self.dailyPnL, self.cumNetPnL],
                             axis=1)
        return dfOutput
