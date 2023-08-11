def calc_strikerate(runs,balls):
    strike_rate = round(runs / balls * 100, 2 ) if balls else float("NaN")
    return strike_rate

def calc_average(runs, outs):
    average = round(runs / outs, 2) if outs > 0 else float("NaN")
    return average

def get_battervbowler(df, batter, bowler):
    return df[(df["batter"] == batter) & (df["bowler"] == bowler) ]

def headon(df,batter, bowler):
    df_headon = get_battervbowler(df,batter, bowler)
    runs = df_headon["runs.total"].sum()
    outs = df_headon["isWicketDelivery"].sum()
    balls = len(df_headon)
    average = calc_average(runs, outs)
    strike_rate = calc_strikerate(runs, balls)
    sixes = len(df_headon[df_headon["runs.batter"] == 6])
    fours = len(df_headon[df_headon["runs.batter"] == 4])
    dots =  len(df_headon[df_headon["runs.batter"] == 0])
    
    return runs, outs, balls, average, strike_rate, sixes, fours, dots  