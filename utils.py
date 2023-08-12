import json
from thefuzz import process, fuzz
import pandas as pd
import os
from ast import literal_eval
import plotly
import plotly.express as px
import cloudinary

cloudinary.config( 
  cloud_name = "dzkylos5o", 
  api_key = "342758611647946", 
  api_secret = "04IpZaH-TW_hrU3dCxFbdPRYe8I",
  secure = True
)
CLOUDINARY_URL= "cloudinary://342758611647946:04IpZaH-TW_hrU3dCxFbdPRYe8I@dzkylos5o"
names_url = r"https://drive.google.com/uc?export=download&id=17em2t0mkgR-zmp0jU2hejqYCz5fmNDd7"

import cloudinary.uploader
import cloudinary.api
from urllib.request import Request, urlopen


req = Request(names_url)
req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')
content = urlopen(req)

# Read the 'names.csv' file, converting 'team' column to a list
names = pd.read_csv(content, converters={'team': literal_eval})
common_names = names["cname"].tolist()

# Function to get common names based on partial matching
def get_common_names(name):
    return [i[0] for i in process.extract(name, common_names, scorer=fuzz.partial_ratio)]

# Function to get teams and batter's unique name
def get_teams(cname):
    batter_unique, teams = names[names["cname"] == cname]["unique_name"].to_string(index=False), names[names["cname"] == cname]["team"]
    try:
        teams = teams.to_list()[0]
    except:
        if len(names[names["name"] == cname]["team"].to_list()[0]) > 0:
            teams = names[names["name"] == cname]["team"].to_list()[0]
            batter_unique = names[names["name"] == cname]["unique_name"].to_string(index=False)
    return teams, batter_unique

# Function to create a dictionary of player images
def make_image_dict():
    images_dict = {}
    players_with_images = {}
    folders = [folder["name"] for folder in cloudinary.api.root_folders()["folders"]]
    folders.remove("samples")
    for i in folders:
        images_dict[i] = []
        temp_dict = cloudinary.api.resources(type = "upload" , prefix= i , max_results = 30)
        for j in temp_dict["resources"]:
                images_dict[i].append(j["public_id"].lstrip(i + "//"))
                players_with_images[j["public_id"].lstrip(i + "//")] = j["secure_url"]
    return images_dict, players_with_images

images_dict, images_list = make_image_dict()

# Function to get player's image
def get_player_image(cname):
    teams, name = get_teams(cname)
    colors = { 'delhi-capitals' : "#c90006", 'kolkata-knight-riders': "#563089" , "chennai-super-kings": "#ffcb04", 
              'gujarat-titans': "#77c7f2", 'lucknow-super-giants': "#0155e1", 'mumbai-indians' : "#143975",
 'punjab-kings' : "#d71820" , 'rajasthan-royals' : "#eb83b5" , 'royal-challengers-bangalore':"#cb2e2e" , 
 'sunrisers-hyderabad': "#ef4023"}
    for i in teams:
        team = process.extractOne(i, images_dict.keys())[0]
        if cname in images_dict[team] or name in images_dict[team]:
            temp_ = process.extractOne(cname, images_dict[team])[0]
            print(temp_)
            
            return name, images_list[temp_],colors[team]
        
        elif process.extractOne(cname, images_dict[team], scorer=fuzz.partial_ratio)[1] == 100:
            temp = process.extractOne(cname, images_dict[team],scorer=fuzz.partial_ratio)[0]
            return name, images_list[temp] ,colors[team] 

# Function to read ranks CSV file and standardize column names
def readrankcsv(name , m):
    df = pd.read_csv(name)
    if "Unnamed: 0" in df.columns:
        df.drop("Unnamed: 0", axis=1, inplace=True)
        
    if m =="bowl":
        bowlcols = ["name", "innings", "balls", "overs", "maidens", "runs", "wickets", "avg", "economy", "strike_rate",
                    "wiperinn", "wicketsper4overs", "wi0", "wi3", "wi4", "wi5", "wides", "noballs", "accuracy"]
        df.columns = bowlcols
    elif m =="bat":
        batcols = ["name", "innings", "balls", "runs", "highest", "avg", "strike_rate", "cents", "fifty", "thirty",
                   "outs", "sixes", "fours", "dots", "balls_per_boundary", "balls_per_four", "balls_per_six",
                   "runs_from_fours", "runs_from_sixes", "runs_from_boundaries", "runs_per_boundary", "basra",
                   "dot_ball_percentage"]
        df.columns = batcols
    return df

# Function to filter Batter/Bowler Rank DataFrame based on certain conditions
def df_filter(df, minballs=100, mininns=10, minruns=100):
    filtered = df[(df["balls"] > minballs) & (df["innings"] > mininns) & (df["runs"] > minruns)]
    return filtered

# Function to plot batter dismissal data
def batter_dismissals_plotter(db, dismissal_dict, minballs=1):
    dismissal_db = pd.DataFrame.from_dict(dismissal_dict.items())
    dismissal_db.columns = ["way", "outs"]
    
    db = db[db["balls"] > minballs]
    
    pie = px.pie(dismissal_db, values="outs", names="way", template="ggplot2", color_discrete_sequence=px.colors.sequential.Agsunset)
    pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#000000', width=1)))
    pie.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')

    scatter = px.scatter(db, x="runs", y="balls", color="average", size="out",
                         hover_data=['strikerate', "bowler"], trendline="ols")
    scatter.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')

    outliers = db.loc[(db["out"] > db["out"].quantile(0.9)), ["runs", "balls"]]

    for x, y in outliers.itertuples(index=False):
        scatter.add_annotation(
            x=x, y=y,
            text=db[(db["runs"] == x) & (db["balls"] == y)]["bowler"].to_string(index=False),
            showarrow=False,
            yshift=15
        )
    scatter.update_xaxes(showgrid=False)
    scatter.update_yaxes(showgrid=False)

    graphJSON = json.dumps(scatter, cls=plotly.utils.PlotlyJSONEncoder)
    pieJSON = json.dumps(pie, cls=plotly.utils.PlotlyJSONEncoder)

    return pieJSON, graphJSON

# Function to plot batter runs data
def batter_runs_plotter(db):
    fig = px.scatter(db, x="runs", y="balls", color="average",
                     hover_data=['strikerate', "bowler"], trendline="ols", template="plotly_dark")

    fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide')

    outliers = db.loc[(db["average"] > db["average"].quantile(0.9)), ["runs", "balls"]]

    for x, y in outliers.itertuples(index=False):
        fig.add_annotation(
            x=x, y=y,
            text=db[(db["runs"] == x) & (db["balls"] == y)]["bowler"].to_string(index=False),
            showarrow=False,
            yshift=15
        )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON