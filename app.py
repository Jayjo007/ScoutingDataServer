from flask import Flask, request, render_template, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, validators, ValidationError, BooleanField
from dotenv import load_dotenv
import json, urllib, os, csv
import requests


load_dotenv()

API_KEY = os.getenv("TBA_API_KEY") #fill in

ALL_TEAMS_URL = "https://www.thebluealliance.com/api/v3/teams/{page_num}/simple"
MATCH_SCHEDULE_URL = "https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple"
EVENT_TEAMS_URL = "https://www.thebluealliance.com/api/v3/event/{event_key}/teams/simple"
PING_URL = "https://www.thebluealliance.com/api/v3/status"

MAX_TEAM_NUMBER_LENGTH=5 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")
app.app_context().push()
db = SQLAlchemy(app)
db.metadata.create_all()

def ping():
    try:
        response = requests.get(url=PING_URL, headers={'X-TBA-Auth-Key':API_KEY, 'accept': 'application/json'})
        return not response.json()["is_datafeed_down"]
    except:
        return False

@app.route("/")
def index():
    return render_template("main_screen.html")

@app.route("/submitMatch", methods=['GET', 'POST'])
def submitMatch():
    if request.method == 'POST':
        payload = urllib.parse.unquote(request.get_data())
        if (payload[0] == 'm'):
            json_object = json.loads(payload[10:])
            teamNumber = json_object["teamNumber"]
            eventKey = json_object["event"]
            matchNumber = json_object["matchNumber"]
            matchLevel = getCurrentMatchLevel()
            if (MatchData.query.filter_by(teamNumber=teamNumber, eventKey=eventKey, matchNumber=matchNumber, matchLevel=matchLevel).count() < 1):
                db.session.add(MatchData(json_object))
                db.session.commit()
            else:
                print("duplicate match")
        return render_template("match_data_import.html")
    else:
        return render_template("match_data_import.html")

@app.route("/submitPitScout", methods=['GET', 'POST'])
def submitPitScout():
    if request.method == 'POST':
        payload = urllib.parse.unquote(request.get_data())
        #json_object = request.get_json()
        if (payload[0] == 'p'):
            json_object = json.loads(payload[8:])
            db.session.add(PitScoutRecord(json_object))
            db.session.commit()
        return render_template("pit_data_import.html")
    else:
        return render_template("pit_data_import.html")

@app.route("/importTeams", methods=["GET"])
def importTeams():
    importTeamNames()

@app.route("/settings")
def openSettings():
    return render_template("settings.html", eventKey=getActiveEventKey(), ping=ping(), eventLevel=getCurrentMatchLevel(), fieldSide=getSideOfField())

@app.route("/changeActiveEventKey", methods=["POST"])
def submitNewEventKey():
    if request.method == 'POST':
        newEventKey = urllib.parse.unquote(request.get_data()).split("=")[-1]
        setActiveEventKey(newEventKey)
    return render_template("redirect_settings.html")

@app.route("/changeActiveEventLevel", methods=["POST"])
def submitNewEventLevel():
    if request.method == 'POST':
        newEventKey = urllib.parse.unquote(request.get_data()).split("=")[-1]
        setActiveEventLevel(newEventKey)
    return render_template("redirect_settings.html")

@app.route("/changeCurrentSide", methods=["POST"])
def submitNewFieldSide():
    if request.method == 'POST':
        newEventKey = urllib.parse.unquote(request.get_data()).split("=")[-1]
        setFieldSide(newEventKey)
    return render_template("redirect_settings.html")

@app.route("/downloadMatchSchedule", methods=["GET"])
def getMatchScheduleRoute():
    getMatchSchedule()
    return "Nothing"

@app.route("/matchDataInspector")
def matchDataInspector():
    matches = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='qm').order_by(MatchSchedule.matchNumber) 
    elimMatches = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='sf').order_by(MatchSchedule.matchNumber)
    finalsMatches = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='f').order_by(MatchSchedule.matchNumber)
    return render_template("data_inspector.html", eventKey=getActiveEventKey(), matches=matches, semimatches=elimMatches, finalsmatches=finalsMatches)

@app.route("/teamBreakdown/<team>")
def getTeamBreakdown(team):
    currentEventTeamMatches = MatchData.query.filter_by(eventKey=getActiveEventKey(), teamNumber=team).order_by(MatchData.matchNumber)
    teamrecord = TeamRecord.query.filter_by(teamNumber=team).first()
    teamPitInfo = PitScoutRecord.query.filter_by(teamNumber=team, eventKey=getActiveEventKey()).first()
    teamSuperScoutInfo = SuperScoutRecord.query.filter_by(teamNumber = team, eventKey = getActiveEventKey())
    return render_template("team_breakdown.html", team=teamrecord, currentEventMatches=currentEventTeamMatches, pitInfo=teamPitInfo, currentEventSuperScout=teamSuperScoutInfo)

@app.route("/matchPreview/<matchNo>/<matchLevel>/detailed")
def getMatchPreviewDetailed(matchNo, matchLevel):
    match = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchNumber=matchNo, matchLevel=matchLevel).first_or_404()
    red1Matches = MatchData.query.filter_by(teamNumber=match.red1, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    if (red1Matches.count() < 5):
        red1Matches = MatchData.query.filter_by(teamNumber=match.red1).filter(MatchData.eventKey.in_((getActiveEventKey(), "prescout"))).order_by(MatchData.timestamp)
    red2Matches = MatchData.query.filter_by(teamNumber=match.red2, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    if (red2Matches.count() < 5):
        red2Matches = MatchData.query.filter_by(teamNumber=match.red2).filter(MatchData.eventKey.in_((getActiveEventKey(), "prescout"))).order_by(MatchData.timestamp)
    red3Matches = MatchData.query.filter_by(teamNumber=match.red3, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    if (red3Matches.count() < 5):
        red3Matches = MatchData.query.filter_by(teamNumber=match.red3).filter(MatchData.eventKey.in_((getActiveEventKey(), "prescout"))).order_by(MatchData.timestamp)
    blue1Matches = MatchData.query.filter_by(teamNumber=match.blue1, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    if (blue1Matches.count() < 5):
        blue1Matches = MatchData.query.filter_by(teamNumber=match.blue1).filter(MatchData.eventKey.in_((getActiveEventKey(), "prescout"))).order_by(MatchData.timestamp)
    blue2Matches = MatchData.query.filter_by(teamNumber=match.blue2, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    if (blue2Matches.count() < 5):
        blue2Matches = MatchData.query.filter_by(teamNumber=match.blue2).filter(MatchData.eventKey.in_((getActiveEventKey(), "prescout"))).order_by(MatchData.timestamp)
    blue3Matches = MatchData.query.filter_by(teamNumber=match.blue3, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    if (blue3Matches.count() < 5):
        blue3Matches = MatchData.query.filter_by(teamNumber=match.blue3).filter(MatchData.eventKey.in_((getActiveEventKey(), "prescout"))).order_by(MatchData.timestamp)
    red1record = TeamRecord.query.filter_by(teamNumber=match.red1).first()
    red2record = TeamRecord.query.filter_by(teamNumber=match.red2).first()
    red3record = TeamRecord.query.filter_by(teamNumber=match.red3).first()
    blue1record = TeamRecord.query.filter_by(teamNumber=match.blue1).first()
    blue2record = TeamRecord.query.filter_by(teamNumber=match.blue2).first()
    blue3record = TeamRecord.query.filter_by(teamNumber=match.blue3).first()
    tn = TeamNames(red1record, red2record, red3record, blue1record, blue2record, blue3record)
    return render_template("match_preview.html", match=match, red1=red1Matches, red2=red2Matches, red3=red3Matches, blue1=blue1Matches, blue2=blue2Matches, blue3=blue3Matches, tn=tn, simple = False)

@app.route("/matchPreview/<matchNo>/<matchLevel>/simple")
def getMatchPreviewSimple(matchNo, matchLevel):
    match = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchNumber=matchNo, matchLevel=matchLevel).first_or_404()
    red1record = TeamRecord.query.filter_by(teamNumber=match.red1).first()
    red2record = TeamRecord.query.filter_by(teamNumber=match.red2).first()
    red3record = TeamRecord.query.filter_by(teamNumber=match.red3).first()
    blue1record = TeamRecord.query.filter_by(teamNumber=match.blue1).first()
    blue2record = TeamRecord.query.filter_by(teamNumber=match.blue2).first()
    blue3record = TeamRecord.query.filter_by(teamNumber=match.blue3).first()
    tn = TeamNames(red1record, red2record, red3record, blue1record, blue2record, blue3record)
    return render_template("match_preview_simple.html", match=match, red1=[], red2=[], red3=[], blue1=[], blue2=[], blue3=[], tn=tn, simple = True)


@app.route("/matchBreakdown/<matchNo>/<matchLevel>")
def getMatchBreakdown(matchNo, matchLevel):
    match = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchNumber=matchNo, matchLevel=matchLevel).first_or_404()
    red1Match = MatchData.query.filter_by(teamNumber=match.red1, eventKey=getActiveEventKey(), matchNumber=matchNo).first()
    red2Match = MatchData.query.filter_by(teamNumber=match.red2, eventKey=getActiveEventKey(), matchNumber=matchNo).first()
    red3Match = MatchData.query.filter_by(teamNumber=match.red3, eventKey=getActiveEventKey(), matchNumber=matchNo).first()
    blue1Match = MatchData.query.filter_by(teamNumber=match.blue1, eventKey=getActiveEventKey(), matchNumber=matchNo).first()
    blue2Match = MatchData.query.filter_by(teamNumber=match.blue2, eventKey=getActiveEventKey(), matchNumber=matchNo).first()
    blue3Match = MatchData.query.filter_by(teamNumber=match.blue3, eventKey=getActiveEventKey(), matchNumber=matchNo).first()
    red1record = TeamRecord.query.filter_by(teamNumber=match.red1).first()
    red2record = TeamRecord.query.filter_by(teamNumber=match.red2).first()
    red3record = TeamRecord.query.filter_by(teamNumber=match.red3).first()
    blue1record = TeamRecord.query.filter_by(teamNumber=match.blue1).first()
    blue2record = TeamRecord.query.filter_by(teamNumber=match.blue2).first()
    blue3record = TeamRecord.query.filter_by(teamNumber=match.blue3).first()
    tn = TeamNames(red1record, red2record, red3record, blue1record, blue2record, blue3record)
    return render_template("match_breakdown.html", match=match, red1=red1Match, red2=red2Match, red3=red3Match, blue1=blue1Match, blue2=blue2Match, blue3=blue3Match, tn=tn)

@app.route("/teamMatchBreakdown/<team>/<eventKey>/<matchNo>/<eventLevel>")
def getTeamMatchBreakdown(team, matchNo, eventKey, eventLevel):
    matchRecord = MatchData.query.filter_by(eventKey=eventKey, teamNumber=team, matchNumber=matchNo, matchLevel=eventLevel).first_or_404()
    teamrecord = TeamRecord.query.filter_by(teamNumber=team).first()
    superscoutRecord = SuperScoutRecord.query.filter_by(eventKey=eventKey, teamNumber=team, matchNumber=matchNo, matchLevel=eventLevel)
    return render_template("team_match_breakdown.html", team=teamrecord, match=matchRecord, eventKey=eventKey, superScout=superscoutRecord)
    
@app.route("/downloadTeamList")
def downloadTeamList():
    eventKey = getActiveEventKey()
    TeamAtEvent.query.filter_by(eventKey=eventKey).delete()
    db.session.commit()
    response = requests.get(url=EVENT_TEAMS_URL.format(event_key = str(eventKey)), headers={'X-TBA-Auth-Key':API_KEY, 'accept': 'application/json'})
    teamListJson = response.json()
    for team in teamListJson:
        teamNo = team["team_number"]
        teamAtEventRecord = TeamAtEvent(teamNo, eventKey)
        db.session.add(teamAtEventRecord)
    db.session.commit()
    return "Nothing"

@app.route("/teamDataInspector")
def displayTeamList():
    teamsAtEvent = TeamAtEvent.query.filter_by(eventKey=getActiveEventKey()).order_by(TeamAtEvent.teamNumber)
    teams = []
    for team in teamsAtEvent:
        teams.append(TeamRecord.query.filter_by(teamNumber=team.teamNumber).first())
    return render_template("team_data_lookup.html", teams=teams, eventKey=getActiveEventKey())

@app.route("/autonomousAnalysis")
def displayAutonomousAnalysis():
    teamsAtEvent = TeamAtEvent.query.filter_by(eventKey=getActiveEventKey()).order_by(TeamAtEvent.teamNumber)
    teams = []
    for team in teamsAtEvent:
        teams.append(TeamRecord.query.filter_by(teamNumber=team.teamNumber).first())
    """
    sortedAmp = sorted(teams, key=lambda x: x.getAmpAutoAverages(), reverse=True)
    sortedCenter = sorted(teams, key=lambda x: x.getCenterAutoAverages(), reverse=True)
    sortedSource = sorted(teams, key=lambda x: x.getSourceAutoAverages(), reverse=True)
    return render_template("autonomous_analysis.html", ampTeams=sortedAmp, centerTeams=sortedCenter, sourceTeams=sortedSource, eventKey=getActiveEventKey())
    """
    return "Auto Analysis Placeholder"

@app.route("/customMatchPreview", methods=["GET", "POST"])
def customMatchPreviewLanding():
    form = CustomMatchForm(request.form)
    teamsAtEvent = TeamAtEvent.query.filter_by(eventKey=getActiveEventKey()).order_by(TeamAtEvent.teamNumber)
    teams = []
    for team in teamsAtEvent:
        teams.append(TeamRecord.query.filter_by(teamNumber=team.teamNumber).first())
    if request.method == 'POST' and form.validate():
        match = MatchSchedule(getActiveEventKey(),-1,"Custom", form.red1.data, form.red2.data, form.red3.data, form.blue1.data, form.blue2.data, form.blue3.data)
        red1Match = MatchData.query.filter_by(teamNumber=match.red1, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
        red2Match = MatchData.query.filter_by(teamNumber=match.red2, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
        red3Match = MatchData.query.filter_by(teamNumber=match.red3, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
        blue1Match = MatchData.query.filter_by(teamNumber=match.blue1, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
        blue2Match = MatchData.query.filter_by(teamNumber=match.blue2, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
        blue3Match = MatchData.query.filter_by(teamNumber=match.blue3, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
        red1record = TeamRecord.query.filter_by(teamNumber=match.red1).first()
        red2record = TeamRecord.query.filter_by(teamNumber=match.red2).first()
        red3record = TeamRecord.query.filter_by(teamNumber=match.red3).first()
        blue1record = TeamRecord.query.filter_by(teamNumber=match.blue1).first()
        blue2record = TeamRecord.query.filter_by(teamNumber=match.blue2).first()
        blue3record = TeamRecord.query.filter_by(teamNumber=match.blue3).first()
        tn = TeamNames(red1record, red2record, red3record, blue1record, blue2record, blue3record)
        if (form.simple.data):
            return render_template("match_preview_simple.html", match=match, red1=[], red2=[], red3=[], blue1=[], blue2=[], blue3=[], tn=tn, simple = True)
        else:
            return render_template("match_preview.html", match=match, red1=red1Match, red2=red2Match, red3=red3Match, blue1=blue1Match, blue2=blue2Match, blue3=blue3Match, tn=tn, simple = False)
    else:
        return render_template("custom_match_select.html", eventKey=getActiveEventKey(), form=form, teams=teams)
    
@app.route("/admin")
def getAdminScreen():
    return render_template("admin.html")

@app.route("/clearEventData", methods=["GET"])
def clearEventData():
    TeamAtEvent.query.filter_by(eventKey=getActiveEventKey()).delete()
    MatchSchedule.query.filter_by(eventKey=getActiveEventKey()).delete()
    db.session.commit()
    return "None"

@app.route("/exportEventData") #TODO: Update this in 2025
def exportEventDataToCSV():
    with open('outputs/dataDump.csv', 'w', encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Event Key", 
                         "Match Level", 
                         "Match #", 
                         "Team #", 
                         #TODO: insert here
                         "Defense",])
        scoutingData = MatchData.query.filter_by(eventKey=getActiveEventKey())
        for match in scoutingData:
            writer.writerow([match.eventKey, match.matchLevel, match.matchNumber, match.teamNumber,\
                             #TODO: insert game specific here
                             match.defense])
    return send_file(
        'outputs/dataDump.csv',
        mimetype="text/csv",
        download_name=getActiveEventKey()+"DataDump.csv",
        as_attachment=True)

@app.route("/exportQualitativeEventData")
def exportSuperScoutDataToCSV(): #TODO: Update this in 2025
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    with open('outputs/qualitativeDataDump.csv', 'w', encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Event Key", 
                         "Match Level", 
                         "Match #", 
                         "Team #", 
                         "Broken", 
                         "Notes", 
                         "Overall"])
        scoutingData = SuperScoutRecord.query.filter_by(eventKey=getActiveEventKey())
        for match in scoutingData:
            writer.writerow([match.eventKey, match.matchLevel, match.matchNumber, match.teamNumber,\
                              match.broken, match.notes, match.overall])
    return send_file(
        'outputs/qualitativeDataDump.csv',
        mimetype="text/csv",
        download_name=getActiveEventKey()+"SuperScoutDataDump.csv",
        as_attachment=True)

@app.route("/exportAutonomousEventData")
def exportAutonomousDataToCSV():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    with open('outputs/autonomousDataDump.csv', 'w', encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Event Key", 
                         "Match Level", 
                         "Match #" #TODO: insert gamespecific auto data here
                         ])
        scoutingData = AutonomousData.query.filter_by(eventKey=getActiveEventKey())
        for match in scoutingData:
            writer.writerow([match.eventKey, match.matchLevel, match.matchNumber, match.teamNumber, match.note_1, match.note_2, match.note_3, match.note_4, match.note_5, match.note_6, match.note_7, match.note_8])
    return send_file(
        'outputs/autonomousDataDump.csv',
        mimetype="text/csv",
        download_name=getActiveEventKey()+"AutonomousDataDump.csv",
        as_attachment=True)

@app.route("/exportMatchSchedule")
def exportMatchScheduleToCSV():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    with open('outputs/matchSchedule.csv', 'w', encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        scoutingData = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel=getCurrentMatchLevel())
        for match in scoutingData:
            writer.writerow([match.eventKey, match.matchNumber, match.red1, match.red2, match.red3, match.blue1, match.blue2, match.blue3])
    return send_file(
        'outputs/MatchSchedule.csv',
        mimetype="text/csv",
        download_name=getActiveEventKey()+"MatchSchedule.csv",
        as_attachment=True)

@app.route("/importTabletData")
def importTabletData():
    with open('imports/app_database-TeamMatchScout.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=';')
        for row in csvreader:
            print(str(len(row)))
            print(row[1] + ": " + getActiveEventKey())
            print(row[0])
            if (len(row) >= 12 and row[1] == getActiveEventKey() and row[0] != "team_number"):
                print("Processing")
                data = dict()
                data["teamNumber"] = row[0]
                data["event"] = row[1]
                data["matchNumber"] = row[2]
                data["matchLevel"] = getCurrentMatchLevel()
                """ TODO: update with 2025 game
                data["autoSpeaker"] = row[3]
                data["autoAmp"] = row[4]
                data["teleSpeaker"] = row[5]
                data["teleAmp"] = row[6]
                data["trap"] = row[7]
                data["climbStatus"] = row[8]
                data["pass"] = row[10]
                """
                data["defense"] = row[9]
                data["tablet"] = row[11]
                data["scouter"] = row[12]
                matchData = MatchData(data)
                db.session.add(matchData)
                db.session.commit()
    return "None"

@app.route("/importMatchData")
def importMatchDataFromOtherServer():
    with open('imports/matchData/matchData.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            print(str(len(row)))
            print(row[1] + ": " + getActiveEventKey())
            print(row[0])
            if (len(row) >= 12 and row[0] == getActiveEventKey() and row[0] != "Event Key"):
                print("Processing")
                data = dict()
                data["event"] = row[0]
                data["matchLevel"] = row[1]
                data["matchNumber"] = row[2]
                data["teamNumber"] = row[3]
                """ TODO: 2025 game data
                data["autoSpeaker"] = row[4]
                data["autoAmp"] = row[5]
                data["teleSpeaker"] = row[6]
                data["teleAmp"] = row[7]
                if (len(row) == 13):
                    data["teleMiss"] = row[8]
                    data["trap"] = row[9]
                    data["climbStatus"] = row[10]
                    data["defense"] = row[11]
                    data["pass"] = row[12]
                else:
                    data["trap"] = row[8]
                    data["climbStatus"] = row[9]
                    data["defense"] = row[10]
                    data["pass"] = row[11]
                """
                matchData = MatchData(data)
                db.session.add(matchData)
                db.session.commit()
    return "None"

@app.route("/importSuperScoutData")
def importSuperScoutDataFromOtherServer():
    with open('imports/superScoutData/superScoutData.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            print(str(len(row)))
            print(row[1] + ": " + getActiveEventKey())
            print(row[0])
            if (len(row) >= 8 and row[0] == getActiveEventKey() and row[0] != "Event Key"):
                print("Processing")
                matchData = SuperScoutRecord(row[3], row[0], row[2])
                matchData.matchLevel = row[1]
                #matchData.startPosition = row[4] TODO: update
                matchData.broken = row[5]
                matchData.notes = row[6]
                matchData.overall = row[7]
                db.session.add(matchData)
                db.session.commit()
    return "None"

@app.route("/importAutonomousData")
def importAutonomousDataFromOtherServer():
    with open('imports/autonomousData/autonomousData.csv', newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            print(str(len(row)))
            print(row[1] + ": " + row[0])
            if (len(row) >= 12 and row[0] == getActiveEventKey() and row[0] != "Event Key"):
                print("Processing")
                matchData = AutonomousData(row[3], row[2], row[0], row[1])
                """TODO: 2025 Game Specific
                matchData.note_1 = row[4]
                matchData.note_2 = row[5]
                matchData.note_3 = row[6]
                matchData.note_4 = row[7]
                matchData.note_5 = row[8]
                matchData.note_6 = row[9]
                matchData.note_7 = row[10]
                matchData.note_8 = row[11]
                """
                db.session.add(matchData)
                db.session.commit()
    return "None"

@app.route("/superScout")
def superScoutLanding():
    form = SelectSuperScoutForm()
    return render_template("super_scout_landing.html", form=form, matchNumbers=getMatchNumbers())

@app.route("/superScout/scout", methods=["GET", "POST"])
def superScouting():
    matchNumber = request.args.get("matchNumber")
    custom = request.args.get("custom")
    alliance = request.args.get("alliance")
    matchRecord = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel=getCurrentMatchLevel(), matchNumber=matchNumber).first()
    return render_template("super_scout.html", match=matchRecord, custom=custom, alliance=alliance, scoringTable=getSideOfField())

@app.route("/superScout/submit", methods=["POST"])
def submitSuperScout():
    if request.method == 'POST':
        #payload = request.get_data()
        if request.form.get("alliance") != "2":
            processSuperScout(request, "red1")
            processSuperScout(request, "red2")
            processSuperScout(request, "red3")
        if request.form.get("alliance") != "1":
            processSuperScout(request, "blue1")
            processSuperScout(request, "blue2")
            processSuperScout(request, "blue3")
        if (int(request.form.get("matchNumber")) < MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel=getCurrentMatchLevel()).count()):
            return render_template("redirect_superscout.html", matchNumber=int(request.form.get("matchNumber"))+1, alliance=request.form.get("alliance"))
        return render_template("main_screen.html")


@app.route("/superScout/scout/custom", methods=["GET"])
def superScoutingCustom():
    custom = True
    matchRecord = MatchSchedule(getActiveEventKey(), "Custom", getCurrentMatchLevel(), -1, -1, -1, -1, -1, -1)
    return render_template("super_scout.html", match=matchRecord, custom=custom)

@app.route("/settings/downloadMatchBreakdowns")
def downloadMatchBreakdowns():
    print("Downloading match breakdowns for event " + getActiveEventKey())
    return "None"

@app.route("/app/downloadActiveMatchSchedule")
def downloadMatchScheduleToApp():
    matches = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel=getCurrentMatchLevel()).all()
    data = [ row.as_dict() for row in matches ]
    return jsonify(response = data, status=200, mimetype="application/json")

@app.route("/app/uploadMatches")
def uploadMatches(methods = ["POST"]):
    if(request.method == "POST"):
        payload = urllib.parse.unquote(request.get_data())
        json_object = json.loads(payload)
        db.session.add(MatchData(json_object))
        db.session.commit()
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'} 
    
@app.route("/admin/generateMatchesInDatabase/<matches>")
def generateMatchesInDatabase(matches):
    for k in range(int(matches)):
        newMatch = MatchSchedule(getActiveEventKey(), k+1, getCurrentMatchLevel(), -1, -1, -1, -1, -1, -1)
        db.session.add(newMatch)
    db.session.commit()
    return "Done"

@app.route("/settings/processMatchScheduleCsv")
def processMatchSchedule():
    with open("matchScheduleImport.csv") as csvFile:
        csvReader = csv.reader(csvFile, delimiter=",")
        for row in csvReader:
            matchNumber = row[1]
            red1 = row[2]
            red2 = row[3]
            red3 = row[4]
            blue1 = row[5]
            blue2 = row[6]
            blue3 = row[7]
            match = MatchSchedule(getActiveEventKey(), matchNumber, getCurrentMatchLevel(), red1, red2, red3, blue1, blue2, blue3)
            if (MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel=getCurrentMatchLevel(), matchNumber=matchNumber).count() < 1):
                db.session.add(match)
    db.session.commit()
    return "Done"


def processSuperScout(request, dsN):
    teamNumber = request.form.get(dsN+"TeamNumber")
    record = SuperScoutRecord(teamNumber, getActiveEventKey(), request.form.get("matchNumber"))
    record.matchLevel = getCurrentMatchLevel()
    #TODO: 2025 specific
    broken = request.form.get(dsN+"Broken")
    if (broken=="true"):
        record.broken = 1
    else:
        record.broken = 0
    record.notes = request.form.get(dsN+"Notes")
    record.overall = request.form.get(dsN+"Overall")
    db.session.add(record)
    db.session.commit()
    autoData = AutonomousData(teamNumber, request.form.get("matchNumber"), getActiveEventKey(), getCurrentMatchLevel())
    """TODO: 2025 specific
    if (request.form.get("note1") == teamNumber):
        autoData.note_1 = 1
    else:
        autoData.note_1 = 0
    if (request.form.get("note2") == teamNumber):
        autoData.note_2 = 1
    else:
        autoData.note_2 = 0
    if (request.form.get("note3") == teamNumber):
        autoData.note_3 = 1
    else:
        autoData.note_3 = 0
    if (request.form.get("note4") == teamNumber):
        autoData.note_4 = 1
    else:
        autoData.note_4 = 0
    if (request.form.get("note5") == teamNumber):
        autoData.note_5 = 1
    else:
        autoData.note_5 = 0
    if (request.form.get("note6") == teamNumber):
        autoData.note_6 = 1
    else:
        autoData.note_6 = 0
    if (request.form.get("note7") == teamNumber):
        autoData.note_7 = 1
    else:
        autoData.note_7 = 0
    if (request.form.get("note8") == teamNumber):
        autoData.note_8 = 1
    else:
        autoData.note_8 = 0
    """
    db.session.add(autoData)
    db.session.commit()   

def validate_preview(form, field):
    if int(field.data) not in getEventTeams():
        raise ValidationError("Team not at active event")
        
def validate_matchNumber(form, field):
    if int(field.data) not in getMatchNumbers():
        raise ValidationError("Match Number Out Of Bounds")
    
def addAllianceAverages(team1, team2, team3):
    totalAverages = MatchAverages(None)
    """TODO: 2025 specific
    totalAverages.auto_speaker = team1.auto_speaker + team2.auto_speaker + team3.auto_speaker
    totalAverages.auto_amp = team1.auto_amp + team2.auto_amp + team3.auto_amp
    totalAverages.tele_speaker = team1.tele_speaker + team2.tele_speaker + team3.tele_speaker
    totalAverages.tele_amp = team1.tele_amp + team2.tele_amp + team3.tele_amp
    totalAverages.trap = team1.tele_amp + team2.tele_amp + team3.tele_amp
    if (totalAverages.trap > 3):
        totalAverages.trap = 3
    totalAverages.climb = (team1.climb + team2.climb + team3.climb) / 100
    totalAverages.passing = team1.passing + team2.passing + team3.passing
    """
    return totalAverages


class CustomMatchForm(Form):
    red1 = StringField('Red 1', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    red2 = StringField('Red 2', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    red3 = StringField('Red 3', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    blue1 = StringField('Blue 1', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    blue2 = StringField('Blue 2', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    blue3 = StringField('Blue 3', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    simple = BooleanField('Simple?')
   
class SelectSuperScoutForm(Form):
    matchNumber = StringField('Match Number', [validators.Length(max=3), validators.DataRequired(), validate_matchNumber])
    
class TeamNames():
    def __init__(self, red1, red2, red3, blue1, blue2, blue3):
        self.red1 = red1
        self.red2 = red2
        self.red3 = red3
        self.blue1 = blue1
        self.blue2 = blue2
        self.blue3 = blue3
    def getRedAllianceAverage(self):
        red1Averages = self.red1.getAverages()
        if (red1Averages == None):
            red1Averages = MatchAverages(self.red1.teamNumber)
        red2Averages = self.red2.getAverages()
        if (red2Averages == None):
            red2Averages = MatchAverages(self.red2.teamNumber)
        red3Averages = self.red3.getAverages()
        if (red3Averages == None):
            red3Averages = MatchAverages(self.red3.teamNumber)
        #todo: this i dont feel like doing rn
        return addAllianceAverages(red1Averages, red2Averages, red3Averages)
    def getBlueAllianceAverage(self):
        blue1Averages = self.blue1.getAverages()
        if (blue1Averages == None):
            blue1Averages = MatchAverages(self.blue1.teamNumber)
        blue2Averages = self.blue2.getAverages()
        if (blue2Averages == None):
            blue2Averages = MatchAverages(self.blue2.teamNumber)
        blue3Averages = self.blue3.getAverages()
        if (blue3Averages == None):
            blue3Averages = MatchAverages(self.blue3.teamNumber)
        #todo: this i dont feel like doing rn
        return addAllianceAverages(blue1Averages, blue2Averages, blue3Averages)
    

def getEventTeams():
    teams = set()
    teamListing = TeamAtEvent.query.filter_by(eventKey=getActiveEventKey())
    for team in teamListing:
        teams.add(team.teamNumber)
    return teams

def getMatchNumbers():
    matchNumbers = set()
    matchListing = MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel=getCurrentMatchLevel())
    for match in matchListing:
        matchNumbers.add(int(match.matchNumber))
    return matchNumbers

def importTeamNames():
    pagenum = 0
    while(True):
        response = requests.get(url=ALL_TEAMS_URL.format(page_num = str(pagenum)), headers={'X-TBA-Auth-Key':API_KEY, 'accept': 'application/json'})
        teamPage = response.json()
        if len(teamPage) > 0:
            for team in teamPage:
                newTeam = TeamRecord(team["team_number"], team["nickname"])
                results = TeamRecord.query.filter_by(teamNumber=newTeam.teamNumber)
                if (results.count() > 0):
                    if not results.first().teamName == newTeam.teamName:
                        results.first().teamName = newTeam.teamName
                        db.session.commit()
                else:
                    db.session.add(newTeam)
                    db.session.commit()
            pagenum+=1
        else:
            break
    return ""

def getTeamNum(key):
    return key[3:]

def getMatchSchedule():
    eventKey = getActiveEventKey()
    MatchSchedule.query.filter_by(eventKey=eventKey).delete()
    db.session.commit()
    response = requests.get(url=MATCH_SCHEDULE_URL.format(event_key = str(eventKey)), headers={'X-TBA-Auth-Key':API_KEY, 'accept': 'application/json'})
    matchScheduleJson = response.json()
    for match in matchScheduleJson:
        alliances = match["alliances"]
        if (match["comp_level"] == 'sf'):
            matchNumber = match["set_number"]            
        else:
            matchNumber = match["match_number"]
        redteams = alliances["red"]["team_keys"]
        blueteams = alliances["blue"]["team_keys"]
        red1 = getTeamNum(redteams[0])
        red2 = getTeamNum(redteams[1])
        red3 = getTeamNum(redteams[2])
        blue1 = getTeamNum(blueteams[0])
        blue2 = getTeamNum(blueteams[1])
        blue3 = getTeamNum(blueteams[2])
        matchRecord = MatchSchedule(eventKey, str(matchNumber), match["comp_level"], red1, red2, red3, blue1, blue2, blue3)
        db.session.add(matchRecord)   
    db.session.commit()
    
def getActiveEventKey():
    if (not ActiveEventKey.query.first() == None):
        return ActiveEventKey.query.first().activeEventKey
    return "Undefined"

def getCurrentMatchLevel():
    if (not ActiveEventKey.query.filter_by(index=2).first() == None):
        return ActiveEventKey.query.filter_by(index=2).first().activeEventKey
    return "qm"

def getSideOfField():
    if (not ActiveEventKey.query.filter_by(index=3).first() == None):
        return ActiveEventKey.query.filter_by(index=3).first().activeEventKey
    return "1"

def setActiveEventKey(newEventKey):
    if (not ActiveEventKey.query.first() == None):
        ActiveEventKey.query.first().activeEventKey = newEventKey
    else:
        db.session.add(ActiveEventKey(newEventKey))
    db.session.commit()

def setActiveEventLevel(newEventLevel):
    if (not ActiveEventKey.query.filter_by(index="2").first() == None):
        ActiveEventKey.query.filter_by(index="2").first().activeEventKey = newEventLevel
    else:
        newLevel = ActiveEventKey(newEventLevel)
        newLevel.index = 2
        db.session.add(newLevel)
    db.session.commit()

def setFieldSide(newEventLevel):
    if (not ActiveEventKey.query.filter_by(index="3").first() == None):
        ActiveEventKey.query.filter_by(index="3").first().activeEventKey = newEventLevel
    else:
        newLevel = ActiveEventKey(newEventLevel)
        newLevel.index = 3
        db.session.add(newLevel)
    db.session.commit()


from models import ActiveEventKey, MatchSchedule, TeamAtEvent, AutonomousData, SuperScoutRecord
from models import MatchData, PitScoutRecord, TeamRecord
from models.match_averages import MatchAverages