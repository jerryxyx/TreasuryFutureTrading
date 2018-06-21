import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from BackTesting import BackTestingSystem
from utils import disaggregateInputData

df = pd.read_csv("InputData.csv")

# input data
(dfPrices,dfDurations,dfOptWeights,dfRollingStats) = disaggregateInputData(df)

# print(rollingStats.head())
pointPrices = [2000,1000,1000,1000,1000]
tickSizePrices = [1/128,1/128,1/64,1/32,1/32]
margins = [380,625,1300,2700,3700]
transactionCostCoeff = 0.5
# hyper parameteres
numEquities = 5
AUM = 10000000

# model parameters
rollDate = datetime(2017,3,1)
# rollDate = datetime(2017,1,20)

triggerS = 2
triggerT = 5
exitUpLevel = 2
exitDownLevel = 20
pctInvested = 0.3
maxPositions = 30

# plug in
# HyperParameteres
backTesting = BackTestingSystem(numEquities,pointPrices,tickSizePrices,margins,transactionCostCoeff)
# Model Parameters
backTesting.set_AUM(AUM)
backTesting.set_percentageInvested(pctInvested)
backTesting.set_maxPoistions(maxPositions)
backTesting.set_rollDate(rollDate)
backTesting.set_triggerS(triggerS)
backTesting.set_triggerT(triggerT)
backTesting.set_exitUpLevel(exitUpLevel)
backTesting.set_exitDownLevel(exitDownLevel)
# History Data
backTesting.input_data(dfPrices,dfDurations,dfOptWeights,dfRollingStats)

# pre-processing
df2 = backTesting.preprocessing()
print(df2.head())

# strategy's cumulative positions
output_data = backTesting.output_data()
output_data.to_csv("~/Downloads/output.csv")
