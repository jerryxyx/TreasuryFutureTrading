import pandas as pd


def disaggregateInputData(df):
    dfPrices = df.iloc[:, 0:6]
    dfDurations = df.iloc[:, [0, 6, 7, 8, 9, 10]]
    dfOptWeights = df.iloc[:, [0, 11, 12, 13, 14, 15]]
    dfRollingStats = df.loc[:, ["DateTime", "RollingAvg", "RollingStd"]]

    dfPrices.set_index("DateTime", inplace=True)
    dfDurations.set_index("DateTime", inplace=True)
    dfOptWeights.set_index("DateTime", inplace=True)
    dfRollingStats.set_index("DateTime", inplace=True)

    dfPrices.index = pd.to_datetime(dfPrices.index)
    dfDurations.index = pd.to_datetime(dfDurations.index)
    dfOptWeights.index = pd.to_datetime(dfOptWeights.index)
    dfRollingStats.index = pd.to_datetime(dfRollingStats.index)
    return (dfPrices, dfDurations, dfOptWeights, dfRollingStats)