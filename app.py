import json
from flask import Flask, render_template, request
import pandas as pd
from Headon import calc_average, calc_strikerate, get_battervbowler, headon
from utils import get_player_image, readrankcsv, df_filter , batter_dismissals_plotter , batter_runs_plotter
app = Flask(__name__)
from batterstats import *
from bowlerstats import *
from urllib.request import Request, urlopen  

# Read main dataset and rankings



ball_by_ball_url = r"https://drive.google.com/uc?export=download&id=10pLZZTF0lzgYw3WcX0q4SXzS17sDZY7N"
names_url = r"https://drive.google.com/uc?export=download&id=17em2t0mkgR-zmp0jU2hejqYCz5fmNDd7"
battingranks_url = r"https://drive.google.com/uc?export=download&id=11gArqsq82uLSU4Ng0hzHzTMX8x3oI-ax"
bowlingranks_url = r"https://drive.google.com/uc?export=download&id=1ZIThb4MGETWSeaf5Ygyf-8lm36ZkWdcv"

urls = [ball_by_ball_url, battingranks_url,bowlingranks_url]
contents = []
for i in urls:
    req = Request(i)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')
    contents.append(urlopen(req))


df = pd.read_csv(contents[0])
batrank = readrankcsv(contents[1] , "bat")
bowlrank = readrankcsv(contents[2] , "bowl")

# Home page route
@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

# Head-to-Head analysis route
@app.route("/headon", methods=["POST", "GET"])
def headvhead():
    if request.method == "GET":
        return render_template("headon.html", show_table=0)
    if request.method == "POST":
        # Get batter and bowler names from form
        batter = request.form.get("batter")
        bowler = request.form.get("bowler")
        # Get player images and colors
        batter_unique, batter_img, batter_color = get_player_image(batter)
        bowler_unique, bowler_img, bowler_color = get_player_image(bowler)
        # Perform head-to-head analysis
        runs, outs, balls, average, strike_rate, sixes, fours, dots = headon(df, batter_unique, bowler_unique)
        # Render template with results
        return render_template("headon.html", show_table=1, runs=runs, outs=outs, balls=balls, average=average,
                               strikerate=strike_rate, sixes=sixes, fours=fours, dots=dots,
                               batter_img=batter_img, bowler_img=bowler_img,
                               bowler_color=bowler_color, batter_color=batter_color,
                               player1=batter, player2=bowler)

# Global variable to store selected player
globalplayer = "hi"

# Player search route
@app.route("/playersearch", methods=["POST", "GET"])
def playersearch():
    if request.method == "GET":
        return render_template("playerprofile.html", show_table=0)
    if request.method == "POST":
        player = request.form.get("player")
        player_unique, player_img, player_color = get_player_image(player)
        global globalplayer
        globalplayer = player_unique
        # Get and display batting and bowling statistics
        battingstats = []
        bowlingstats = []
        # Append career statistics
        battingstats.append(("Career",) + display_batter_overall(df, player_unique))
        bowlingstats.append(("Career",) + display_bowler_overall(df, player_unique))
        # Append year-wise statistics
        battingstats.extend(get_batter_stats_by_year(df, player_unique))
        bowlingstats.extend(get_bowler_stats_by_year(df, player_unique))
        # Sort year-wise statistics
        battingstats[1:] = sorted(battingstats[1:], key=lambda t: (t[0]))
        bowlingstats[1:] = sorted(bowlingstats[1:], key=lambda t: (t[0]))
        # Perform dismissal analysis
        dismissal_dict, bdf = batterwickets(df, player_unique)
        howpie, scatter = batter_dismissals_plotter(bdf, dismissal_dict)
        # Render template with results
        return render_template("playerprofile.html", show_table=1, batNest=battingstats, bowlNest=bowlingstats,
                               pimg=player_img, pcol=player_color, player1=player, graphJSON=scatter, pieJSON=howpie)

# Callback route for dismissal analysis
@app.route('/callback', methods=['POST', 'GET'])
def cb():
    minballs = int(request.args.get('data'))
    dism_dict, bdf1 = batterwickets(df, globalplayer)
    howp, scatter = batter_dismissals_plotter(bdf1, dism_dict, minballs)
    return scatter

# Routes for batting and bowling rankings
@app.route("/bat", methods=["GET"])
def batrankfunc():
    if request.method == "GET":
        return render_template("batrank.html", show_table=1)

@app.route("/api/bat", methods=["GET", "POST"])
def batterrank():
    if request.method == "POST":
        args = json.loads(request.values.get("arguments"))
        inns, balls, runs = int(args[0]), int(args[1]), int(args[2])
        rankjson = df_filter(batrank, balls, inns, runs).to_json(orient="records")
        return rankjson

@app.route("/bowl", methods=["GET"])
def bowlrankfunc():
    if request.method == "GET":
        return render_template("bowlrank.html", show_table=1)

@app.route("/api/bowl", methods=["POST"])
def bowlerrank():
    if request.method == "POST":
        args = json.loads(request.values.get("arguments"))
        inns, balls, runs = int(args[0]), int(args[1]), int(args[2])
        rankjson = df_filter(bowlrank, balls, inns, runs).to_json(orient="records")
        return rankjson

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
