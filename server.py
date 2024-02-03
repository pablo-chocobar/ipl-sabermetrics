from urllib.request import Request, urlopen
from bowlerstats import *
from batterstats import *
import json
from flask import Flask, render_template, request, json, Response
import pandas as pd
from Headon import calc_average, calc_strikerate, get_battervbowler, headon
from utils import get_player_image, readrankcsv, df_filter, batter_dismissals_plotter, batter_runs_plotter

from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


ball_by_ball_url = r"https://docs.google.com/spreadsheets/d/e/2PACX-1vSJ6H1JLu_9hHOMxtu_yR5YewkfHSkSI5JjpLok_VXJ30fnhoDk1okZQfRPVnIZv9Aaq0twIMbPVs8V/pub?gid=398497076&single=true&output=csv"
names_url = r"https://docs.google.com/spreadsheets/d/e/2PACX-1vS67MDkgg0LCKSV4F6O1RITlV04Sd1FwnN0kKPd9PtGIYQ4qKCfEKMBHuWfvYAicBGd93agYrLRjth7/pub?gid=371327951&single=true&output=csv"
battingranks_url = r"https://docs.google.com/spreadsheets/d/e/2PACX-1vTRVj7q-XC41hchXVwG3tjS2dhfHT-FfhkIwEGXUDgXExqxTpiqG0XcaZIeXcdeSI8g_2DZXLc3tQ3n/pub?gid=907380851&single=true&output=csv"
bowlingranks_url = r"https://docs.google.com/spreadsheets/d/e/2PACX-1vR_6c_ELYFRbUsJfceJvv0TBQvRCB6gCwO3C47hvB7nPEXwmVj2tqP9UYM0wLyyLtlZWkYIXp0GDaIR/pub?gid=212076047&single=true&output=csv"

# urls = [ball_by_ball_url, battingranks_url, bowlingranks_url]
# contents = []
# for i in urls:
#     req = Request(i)
#     req.add_header(
#         'User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0')
#     contents.append(urlopen(req))


df = pd.read_csv(ball_by_ball_url)
batrank = readrankcsv(battingranks_url, "bat")
bowlrank = readrankcsv(bowlingranks_url, "bowl")

# Home page route


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")

# Head-to-Head analysis route


@app.route("/headon", methods=["POST"])
def headvhead():
    if request.method == "POST":

        print(request.args)
        # Get batter and bowler names from form
        batter = request.args["batter"]
        bowler = request.args["bowler"]
        # Get player images and colors
        batter_unique, batter_img, batter_color = get_player_image(batter)
        bowler_unique, bowler_img, bowler_color = get_player_image(bowler)
        # Perform head-to-head analysis
        runs, outs, balls, average, strike_rate, sixes, fours, dots = headon(
            df, batter_unique, bowler_unique)
        # Render template with results



        results = [{
            "batter_name": batter_unique,
            "batter_img": batter_img,
            "batter_color": batter_color,
            "bowler_name": bowler_unique,
            "bowler_img": bowler_img,
            "bowler_color": bowler_color,
            "runs": runs,
            "outs": outs,
            "balls": balls,
            "average": average,
            "strike_rate": strike_rate,
            "sixes": sixes,
            "fours": fours, "dots": dots}]
        
        print(results)
    response = Response(

        response=json.dumps(results , default = int),
        status=200,
        mimetype='application/json'
    )

    return response

globalplayer = "hi"

@app.route("/playersearch", methods=["POST", "GET"])
def playersearch():
    if request.method == "POST":
        player = request.args.get("player")
        player_unique, player_img, player_color = get_player_image(player)
        global globalplayer
        globalplayer = player_unique
        # Get and display batting and bowling statistics
        battingstats = [["year" , "inns" , "balls", "runs" , "HS" , "avg" , "sr" , "100s" , "50s" , "30s" , "outs" , "6s" , "4s" , "dots" , "bpb"  , "bp4" , "bp6" , "Rf4" , "Rf6" , "Rfb" , "Rpb" , "basra" , "db%"]]
        bowlingstats = [["year" , "inns" , "balls", "overs", "maidens", "runs" , "wkts" , "avg" , "eco", "sr" , "WpI" , "Wp4" , "0w" , "3w" , "4w" , "5w" , "Wides" , "nb"  ,"acc"]]
        # Append career statistics
        battingstats.append(("Career",) + display_batter_overall(df, player_unique))
        bowlingstats.append(("Career",) + display_bowler_overall(df, player_unique))
        # Append year-wise statistics
        battingstats.extend(get_batter_stats_by_year(df, player_unique))
        bowlingstats.extend(get_bowler_stats_by_year(df, player_unique))
        # Sort year-wise statistics
        battingstats[2:] = sorted(battingstats[2:], key=lambda t: (t[0]))
        bowlingstats[2:] = sorted(bowlingstats[2:], key=lambda t: (t[0]))
        # Perform dismissal analysis
        dismissal_dict, bdf = batterwickets(df, player_unique)
        howpie, scatter = batter_dismissals_plotter(bdf, dismissal_dict)
        # Render template with results
        results = {
            "batNest": battingstats,
            "bowlNest": bowlingstats,
            "player_img": player_img,
            "player_color": player_color,
            "player": player,
            # "graphJSON": scatter,
            # "pieJSON": howpie
        }

        response = Response(
        response=json.dumps(results , default = int),
        status=200,
        mimetype='application/json'
        )
        
        return response

# Callback route for dismissal analysis
@app.route('/callback', methods=['POST', 'GET'])
def cb():
    minballs = int(request.args.get('data'))
    dism_dict, bdf1 = batterwickets(df, globalplayer)
    howp, scatter = batter_dismissals_plotter(bdf1, dism_dict, minballs)
    return scatter

@app.route("/api/bat", methods=["GET", "POST"])
def batterrank():
    if request.method == "POST":
        args = json.loads(request.values.get("arguments"))
        inns, balls, runs = int(args[0]), int(args[1]), int(args[2])
        print(inns , balls , runs)
        rankjson = df_filter(batrank, balls, inns, runs).to_json(orient="records")
        
        response = Response(
        response= json.dumps(rankjson),
        status=200,
        mimetype='application/json'
        )
        
        return response
    
@app.route("/api/bowl", methods=["POST"])
def bowlerrank():
    if request.method == "POST":
        args = json.loads(request.values.get("arguments"))
        inns, balls, runs = int(args[0]), int(args[1]), int(args[2])
        rankjson = df_filter(bowlrank, balls, inns, runs).to_json(orient="records")
        
        response = Response(
        response= json.dumps(rankjson),
        status=200,
        mimetype='application/json'
        )
        
        return response


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
