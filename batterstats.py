import pandas as pd
from Headon import headon, get_battervbowler


# Function to get total runs scored by a batter in a match
def get_batter_runs_in_match(match_df,name):
    balls = match_df[(match_df["innings"] < 3) & (match_df["extras.wides"] == 0) & (match_df["batter"] == name)]
    runs = balls["runs.batter"].sum()
    
    return runs

# Function to get various batting statistics for a batter
def get_batter_stats(df,name,super_over):
    if super_over == "include":
        balls = df[(df["extras.wides"] == 0) & (df["batter"] == name)]
        runs_that_count = balls["runs.batter"].sum()
        sixes = len(balls[balls["runs.batter"] == 6])
        fours = len(balls[balls["runs.batter"] == 4])
        dots = len(balls[balls["runs.batter"] == 0])
        outs = len(df[df["batterOut"] == name])
    
    elif super_over == "exclude":
        balls = df[(df["innings"] < 3) & (df["extras.wides"] == 0) & (df["batter"] == name)]
        runs_that_count = balls["runs.batter"].sum()
        sixes = len(balls[balls["runs.batter"] == 6])
        fours = len(balls[balls["runs.batter"] == 4])
        dots = len(balls[balls["runs.batter"] == 0])
        outs = len(df[(df["innings"] < 3) & (df["batterOut"] == name)])

    elif super_over == "only":
        balls = df[(df["innings"] >= 3) & (df["extras.wides"] == 0) & (df["batter"] == name)]
        runs_that_count = balls["runs.batter"].sum()
        sixes = len(balls[balls["runs.batter"] == 6])
        fours = len(balls[balls["runs.batter"] == 4])
        dots = len(balls[balls["runs.batter"] == 0])   
        outs = len(df[(df["innings"] >= 3) & (df["batterOut"] == name)])

    return len(balls) , runs_that_count, sixes , fours ,dots, outs

# Function to calculate batting metrics
def get_batting_metrics(balls, runs, outs, sixes, fours, dots):
    average = round(runs / outs, 2) if outs > 0 else float("NaN")
    balls_per_boundary = round(balls/ (sixes + fours),2) if sixes or fours else float("NaN")
    balls_per_four = round(balls / fours,2) if fours else float("NaN")
    balls_per_six = round(balls / sixes,2) if sixes else float("NaN")
    
    runs_from_fours = round(4 * fours,2)
    runs_from_sixes = round(6 * sixes,2)
    runs_from_boundaries = round(runs_from_fours + runs_from_sixes,2)
    
    dot_ball_percentage = round(dots /balls, 2) * 100 if balls else float("NaN")
    runs_per_boundary = round(runs_from_boundaries / (sixes + fours), 2) if sixes or fours else float("NaN")
    
    strike_rate = round(runs / balls * 100, 2 ) if balls else float("NaN")
    
    if strike_rate != float("NaN") and average != float("NaN"):
        basra = round(average + strike_rate, 2)
    else:
        basra = float("NaN")
    
    
    return average, strike_rate, basra, balls_per_boundary, balls_per_four, balls_per_six \
            ,runs_from_fours, runs_from_sixes, runs_from_boundaries, runs_per_boundary, dot_ball_percentage  


# Function to get highest scores and count of milestone scores of a batter
def get_batter_highest(df, name):
    innings = df[df["batter"] == name]["MatchID"].unique()
    runs_list = []
    for inning in innings:
        match_df = df[df["MatchID"] == inning]
        runs_list.append(get_batter_runs_in_match(match_df, name))
    cents, hfcents, thirty = len([i for i in runs_list if i > 99]), len([i for i in runs_list if i < 100 and i > 49]) ,len([i for i in runs_list if i < 50 and i > 29])
    
    hs = max(runs_list) if len(runs_list) > 0 else float("NaN")

    return len(innings), hs, cents, hfcents, thirty

# Function to return overall batting statistics for a batter
def display_batter_overall(df,name):
    total_balls , total_runs, sixes , fours ,dots, outs = get_batter_stats(df, name, "exclude")
    avg, strike_rate, basra, balls_per_boundary, balls_per_four, balls_per_six \
    ,runs_from_fours, runs_from_sixes, runs_from_boundaries, runs_per_boundary, dot_ball_percentage   = get_batting_metrics(total_balls, total_runs, outs, sixes, fours, dots)
    career_innings, career_highest, cents, fifty, thirty = get_batter_highest(df, name)
    
    return career_innings, total_balls , total_runs,career_highest, avg, strike_rate,cents,fifty,thirty,outs, sixes , fours ,dots, balls_per_boundary, balls_per_four, balls_per_six, runs_from_fours, runs_from_sixes, runs_from_boundaries, runs_per_boundary ,basra,dot_ball_percentage

# Function to analyze wickets taken against a batter 
def batterwickets(df, name):
    batterdf = df[df["batter"] == name]
    outdf = df[df["batterOut"] == name]
        
    runs, outs, balls, average, strike_rate = [] , [] , [] , [] , []
    
    stats = [runs, outs, balls, average, strike_rate]
    
    wicketdf = batterdf[batterdf["wicketKind"] != "run out"].groupby(["bowler"])["isWicketDelivery"].sum().to_frame().reset_index().sort_values(by = ["isWicketDelivery"], ascending = False)
    
    for bowler in wicketdf["bowler"].to_list():
        
        bdf = get_battervbowler(batterdf , name , bowler)
        temp = headon(bdf,name,bowler)[:5]

        for stat, value in zip(stats, temp):
            stat.append(value)
    
    wicketdf["runs"] = runs
    wicketdf["balls"] = balls
    wicketdf["average"] = average
    wicketdf["strikerate"] = strike_rate
    
    wicketdf.rename(columns={'isWicketDelivery':'out'}, inplace=True)
    
    how = outdf["wicketKind"].unique()
    howlist = [outdf[outdf["wicketKind"] == i]["isWicketDelivery"].sum() for i in how]
    howdict = {how : count for (how,count) in zip(how,howlist)}

    return howdict , wicketdf

# Function to get batter statistics by year
def get_batter_stats_by_year(df , name):
    batterdf = df[df["batter"] == name]
    years = batterdf["year"].unique()
    yearwise =[]
    for year in years:
        yearwise.append( (year ,) +  display_batter_overall(batterdf[batterdf["year"] == year] , name) ) 
    return yearwise