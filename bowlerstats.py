import pandas as pd

# Function to calculate bowling statistics for a player
def get_bowling_stats(df, name):
    balls = df[df["bowler"] == name]
    wickets = balls[(balls["isWicketDelivery"] == 1) & (balls["wicketKind"].isin(['caught', 'bowled','lbw','caught and bowled','stumped','hit wicket']))]["isWicketDelivery"].sum()
    runs_that_count = balls[(balls["extras.legbyes"] == 0) &(balls["extras.byes"] == 0)]["runs.total"].sum()
    balls_that_count = balls[(balls["extras.noballs"] == 0) & (balls["extras.wides"] == 0)]
    
    noballs = len(balls[balls["extras.noballs"] > 0])
    wides = len(balls[balls["extras.wides"] > 0])
    
    return len(balls_that_count), runs_that_count, wickets, noballs, wides

# Function to calculate total overs from balls
def total_overs(balls):
    if balls % 6 == 0: 
        return balls / 6
    return balls % 6 / 10 + balls // 6

# Function to get maiden overs for a bowler
def get_maidens(df, name):
    balls = df[df["bowler"] == name]
    innings = balls["MatchID"].unique()
    maiden_list = []
    for inning in innings:
        for over in balls[balls["MatchID"] == inning]["over"].unique():
            that_over = balls[(balls["MatchID"] == inning) & (balls["over"] == over)]
            runs_that_count = that_over[(that_over["extras.legbyes"] == 0) &(that_over["extras.byes"] == 0)]["runs.total"].sum()

            if runs_that_count == 0 and len(that_over) >= 6:
                maiden_list.append((inning, over))    
                
    return maiden_list

# Function to get wickets taken by a bowler in a match
def get_bowler_wickets_in_match(matchdf, name):
    balls = matchdf[matchdf["bowler"] == name]
    return balls[(balls["isWicketDelivery"] == 1) & (balls["wicketKind"].isin(['caught', 'bowled','lbw','caught and bowled','stumped','hit wicket']))]["isWicketDelivery"].sum()

# Function to calculate bowling metrics
def get_bowling_metrics(balls, runs, wickets, noballs, wides):
    average = round(runs / wickets, 2) if wickets > 0 else None
    overs_bowled = total_overs(balls)
    economy = round(runs / overs_bowled, 2 ) if overs_bowled > 1 else None
    strike_rate = round(balls / wickets, 2) if wickets > 0 else None
    wicketsper4overs = round(wickets / overs_bowled * 4 , 2) if overs_bowled > 0 else None
    accuracy = round((balls - (noballs + wides)) * 100 / balls , 2) if balls > 0 else None
    
    return average, overs_bowled, economy, strike_rate, wicketsper4overs, accuracy

# Function to get bowler's wicket hauls in matches
def get_bowler_hauls(df, name):
    innings = df[df["bowler"] == name]["MatchID"].unique()
    wickets_list = []
    for inning in innings:
        match_df = df[df["MatchID"] == inning]
        wickets_list.append(get_bowler_wickets_in_match(match_df, name))

    wi0 = len([i for i in wickets_list if i == 0])
    wi3 = len([i for i in wickets_list if i == 3])
    wi4 = len([i for i in wickets_list if i == 4])
    wi5 = len([i for i in wickets_list if i == 5])
    
    return len(innings), wi0, wi3, wi4, wi5

# Function to display overall bowling statistics for a player
def display_bowler_overall(df, name):
    balls, runs, wickets, noballs, wides = get_bowling_stats(df, name)
    average, overs_bowled, economy, strike_rate, wicketsper4overs, accuracy = get_bowling_metrics(balls, runs, wickets, noballs, wides)
    innings, wi0, wi3, wi4, wi5 = get_bowler_hauls(df, name)
    
    maidens = len(get_maidens(df, name))
    wiperinn = round(wickets / innings, 2) if innings > 0 else None
    
    return innings, balls, overs_bowled, maidens, runs, wickets, average, economy, strike_rate, wiperinn, wicketsper4overs, wi0, wi3, wi4, wi5, wides, noballs, accuracy

# Function to get bowler statistics by year
def get_bowler_stats_by_year(df, name):
    bowlerdf = df[df["bowler"] == name]
    years = bowlerdf["year"].unique()
    yearwise = []
    for year in years:
        yearwise.append((year,) + display_bowler_overall(bowlerdf[bowlerdf["year"] == year], name)) 
    return yearwise
