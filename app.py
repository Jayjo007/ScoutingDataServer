from flask import Flask, request, render_template, send_file, jsonify
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, validators, ValidationError
from dotenv import load_dotenv
import json, urllib, os, csv
import requests, datetime

load_dotenv()

API_KEY = os.getenv("TBA_API_KEY") #fill in

ALL_TEAMS_URL = "https://www.thebluealliance.com/api/v3/teams/{page_num}/simple"
MATCH_SCHEDULE_URL = "https://www.thebluealliance.com/api/v3/event/{event_key}/matches/simple"
EVENT_TEAMS_URL = "https://www.thebluealliance.com/api/v3/event/{event_key}/teams/simple"
PING_URL = "https://www.thebluealliance.com/api/v3/status"

#CHANGE THIS IN 2025 WHEN 5 DIGIT TEAM NUMBERS EXIST
MAX_TEAM_NUMBER_LENGTH=4 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URI")
app.app_context().push()
db = SQLAlchemy(app)

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
            db.session.add(MatchData(json_object))
            db.session.commit()
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
    return render_template("settings.html", eventKey=getActiveEventKey(), ping=ping(), eventLevel=getCurrentMatchLevel())

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
    red2Matches = MatchData.query.filter_by(teamNumber=match.red2, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    red3Matches = MatchData.query.filter_by(teamNumber=match.red3, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    blue1Matches = MatchData.query.filter_by(teamNumber=match.blue1, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    blue2Matches = MatchData.query.filter_by(teamNumber=match.blue2, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
    blue3Matches = MatchData.query.filter_by(teamNumber=match.blue3, eventKey=getActiveEventKey()).order_by(MatchData.matchNumber)
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
    sortedAmp = sorted(teams, key=lambda x: x.getAmpAutoAverages(), reverse=True)
    sortedCenter = sorted(teams, key=lambda x: x.getCenterAutoAverages(), reverse=True)
    sortedSource = sorted(teams, key=lambda x: x.getSourceAutoAverages(), reverse=True)
    return render_template("autonomous_analysis.html", ampTeams=sortedAmp, centerTeams=sortedCenter, sourceTeams=sortedSource, eventKey=getActiveEventKey())

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
        return render_template("match_preview.html", match=match, red1=red1Match, red2=red2Match, red3=red3Match, blue1=blue1Match, blue2=blue2Match, blue3=blue3Match, tn=tn)
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

@app.route("/exportEventData")
def exportEventDataToCSV():
    # with open("outputs/Adjacency.csv") as fp:
    #     csv = fp.read()
    with open('outputs/dataDump.csv', 'w', encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Event Key", 
                         "Match Level", 
                         "Match #", 
                         "Team #", 
                         "Auto Speaker", 
                         "Auto Amp", 
                         "Teleop Speaker", 
                         "Teleop Amp", 
                         "Trap", 
                         "Climb", 
                         "Defense", 
                         "Auto Leave"])
        scoutingData = MatchData.query.filter_by(eventKey=getActiveEventKey())
        for match in scoutingData:
            writer.writerow([match.eventKey, match.matchLevel, match.matchNumber, match.teamNumber, match.auto_speaker, match.auto_amp, match.tele_speaker, match.tele_amp, match.trap, match.climb, match.defense, match.auto_leave])
    return send_file(
        'outputs/dataDump.csv',
        mimetype="text/csv",
        download_name=getActiveEventKey()+"DataDump.csv",
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
        csvreader = csv.reader(csvfile, delimiter=',')
        for row in csvreader:
            print("length:" + str(len(row)))
            if (len(row) >= 12 and row[1] == getActiveEventKey() and row[0] != "team_number"):
                data = dict()
                data["teamNumber"] = row[0]
                data["event"] = row[1]
                data["matchNumber"] = row[2]
                data["matchLevel"] = getCurrentMatchLevel()
                data["autoSpeaker"] = row[3]
                data["autoAmp"] = row[4]
                data["autoLeave"] = row[5]
                data["teleSpeaker"] = row[6]
                data["teleAmp"] = row[7]
                data["trap"] = row[8]
                data["climbStatus"] = row[9]
                data["defense"] = row[10]
                data["tablet"] = row[11]
                data["scouter"] = row[12]
                matchData = MatchData(data)
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
    return render_template("super_scout.html", match=matchRecord, custom=custom, alliance=alliance)

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

def processSuperScout(request, dsN):
    teamNumber = request.form.get(dsN+"TeamNumber")
    record = SuperScoutRecord(teamNumber, getActiveEventKey(), request.form.get("matchNumber"))
    record.matchLevel = getCurrentMatchLevel()
    record.startPosition = request.form.get(dsN+"Position")
    record.midlineGrab = request.form.get(dsN+"Midline")
    record.scoreLevel = None
    record.intake = request.form.get(dsN+"Intake")
    broken = request.form.get(dsN+"Broken")
    if (broken=="true"):
        record.broken = 1
    else:
        record.broken = 0
    record.tippy = request.form.get(dsN+"Tippy")
    record.pushable = request.form.get(dsN+"Pushable")
    record.notes = request.form.get(dsN+"Notes")
    record.overall = request.form.get(dsN+"Overall")
    db.session.add(record)
    db.session.commit()
    

def validate_preview(form, field):
    if int(field.data) not in getEventTeams():
        raise ValidationError("Team not at active event")
        
def validate_matchNumber(form, field):
    if int(field.data) not in getMatchNumbers():
        raise ValidationError("Match Number Out Of Bounds")
    
def addAllianceAverages(team1, team2, team3):
    totalAverages = MatchAverages(None)
    totalAverages.auto_speaker = team1.auto_speaker + team2.auto_speaker + team3.auto_speaker
    totalAverages.auto_amp = team1.auto_amp + team2.auto_amp + team3.auto_amp
    totalAverages.tele_speaker = team1.tele_speaker + team2.tele_speaker + team3.tele_speaker
    totalAverages.tele_amp = team1.tele_amp + team2.tele_amp + team3.tele_amp
    totalAverages.trap = team1.tele_amp + team2.tele_amp + team3.tele_amp
    if (totalAverages.trap > 3):
        totalAverages.trap = 3
    totalAverages.climb = (team1.climb + team2.climb + team3.climb) / 100
    totalAverages.auto_leave = (team1.auto_leave + team2.auto_leave + team3.auto_leave) / 100
    return totalAverages


class CustomMatchForm(Form):
    red1 = StringField('Red 1', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    red2 = StringField('Red 2', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    red3 = StringField('Red 3', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    blue1 = StringField('Blue 1', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    blue2 = StringField('Blue 2', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])
    blue3 = StringField('Blue 3', [validators.Length(max=MAX_TEAM_NUMBER_LENGTH), validators.DataRequired(), validate_preview])

    
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

class PitScoutRecord(db.Model):
    __tablename__ = 'pitdata'
    teamNumber = db.Column(db.String(50), primary_key=True)
    eventKey = db.Column(db.String(50), primary_key=True)
    programmingLanguage = db.Column(db.String(50))
    drivetrain = db.Column(db.String(50))
    driveteam = db.Column(db.Integer())
    def __init__(self, data):
        self.teamNumber = data["teamNumber"]
        self.eventKey = data["event"]
        self.programmingLanguage = data["programmingLanguage"]
        self.drivetrain = data["drivetrainType"]
        self.driveteam = data["driveteam"]

    def __str__(self):
        return self.teamNumber

class SuperScoutRecord(db.Model):
    __tablename__ = 'superscoutdata'
    teamNumber = db.Column(db.String(50), primary_key=True)
    eventKey = db.Column(db.String(50), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(5))
    startPosition = db.Column(db.String(10))
    midlineGrab = db.Column(db.String(10))
    scoreLevel = db.Column(db.String(10))
    intake = db.Column(db.String(10))
    broken = db.Column(db.Integer())
    tippy = db.Column(db.String(15))
    pushable = db.Column(db.String(15))
    notes = db.Column(db.String(255))
    overall = db.Column(db.String(10))
    def __init__(self, teamNumber, eventKey, matchNumber): 
        self.teamNumber = teamNumber
        self.eventKey = eventKey
        self.matchNumber = matchNumber

    def __str__(self):
        return self.teamNumber


class MatchData(db.Model):
    __tablename__ = 'match_data'
    teamNumber = db.Column(db.String(10), primary_key=True)
    eventKey = db.Column(db.String(15), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(50), primary_key=True)
    auto_speaker = db.Column(db.Integer())
    auto_amp = db.Column(db.Integer())
    tele_speaker = db.Column(db.Integer())
    tele_amp = db.Column(db.Integer())
    trap = db.Column(db.Integer())
    climb = db.Column(db.Integer())
    defense = db.Column(db.Integer())
    auto_leave = db.Column(db.Integer())
    tablet = db.Column(db.String(3))
    scouter = db.Column(db.String(50))
    timestamp = db.Column(db.String(50))

    def __init__(self, data):
        self.teamNumber = data["teamNumber"]
        self.eventKey = data["event"]
        self.matchNumber = data["matchNumber"]
        self.matchLevel = getCurrentMatchLevel()
        self.auto_speaker = data["autoSpeaker"]
        self.auto_amp = data["autoAmp"]
        self.tele_speaker = data["teleSpeaker"]
        self.tele_amp = data["teleAmp"]
        self.trap = data["trap"]
        self.climb = data["climbStatus"]
        self.defense = data["defense"]
        self.auto_leave = data["autoLeave"]
        self.tablet = data["tablet"]
        self.scouter = data["scouter"]
        self.timestamp = datetime.datetime.now()

    def __str__(self):
        return self.teamNumber
    
    def renderEventLevel(self):
        if (self.matchLevel=='qm'):
            return "Qualification Match"
        elif (self.matchLevel=='f'):
            return "Finals Match"
        elif (self.matchLevel=="sf"):
            return "Playoff Match"
        else:
            return "Custom Match"
    
class TeamRecord(db.Model):
    __tablename__ = 'teams'
    teamNumber = db.Column(db.String(50), primary_key = True)
    teamName = db.Column(db.String(255))
    def __init__(self, teamNumber, teamName):
        self.teamNumber = teamNumber
        self.teamName = teamName
    def hasPitScoutData(self):
        return PitScoutRecord.query.filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber).count() > 0
    def hasSuperScoutData(self):
        return SuperScoutRecord.query.filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber).count() > 0
    def getMatchesPlayed(self):
        return MatchData.query.filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber).count()
    def getSuperScoutMatchesPlayed(self):
        return SuperScoutRecord.query.filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber).count()
    def getMatchesToPlay(self):
        count = 0
        count += MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='qm', red1=self.teamNumber).count()
        count += MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='qm', red2=self.teamNumber).count()
        count += MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='qm', red3=self.teamNumber).count()
        count += MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='qm', blue1=self.teamNumber).count()
        count += MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='qm', blue2=self.teamNumber).count()
        count += MatchSchedule.query.filter_by(eventKey=getActiveEventKey(), matchLevel='qm', blue3=self.teamNumber).count()
        return count
    def allMatchesScouted(self):
        if self.getMatchesToPlay() == 0:
            return False
        else:
            return self.getMatchesPlayed() == self.getMatchesToPlay()
    def allMatchesSuperScouted(self):
        if self.getMatchesToPlay() == 0:
            return False
        else:
            return self.getSuperScoutMatchesPlayed() == self.getMatchesToPlay()
    def getPitScoutData(self):
        if (self.hasPitScoutData()):
            return PitScoutRecord.query.filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber).first()
        else:
            return None
    def getAverages(self):
        averages = MatchAverages(self.teamNumber)
        if MatchData.query.filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber).count() > 0:
            for match in MatchData.query.filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber).all():
                averages.addAverage(match)
            averages.climb*=100
            #averages.climb = str(averages.climb)+"%"
            averages.auto_leave*=100
            #averages.auto_leave = str(averages.auto_leave)+"%"
            return averages
        else:
            return None
    def getAmpAutoAverages(self):
        q = MatchData.query.join(SuperScoutRecord, db.and_(MatchData.matchNumber==SuperScoutRecord.matchNumber, MatchData.teamNumber==SuperScoutRecord.teamNumber)).filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber, startPosition="AMP")
        if q.count() > 0:
            count = 0
            sum = 0
            for match in q:
                count+=1
                sum+=match.auto_speaker
            return sum/count
        else:
            return 0
    
    def getAmpAutoCount(self):
        return MatchData.query.join(SuperScoutRecord, db.and_(MatchData.matchNumber==SuperScoutRecord.matchNumber, MatchData.teamNumber==SuperScoutRecord.teamNumber)).filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber, startPosition="AMP").count()
    
    def getCenterAutoCount(self):
        return MatchData.query.join(SuperScoutRecord, db.and_(MatchData.matchNumber==SuperScoutRecord.matchNumber, MatchData.teamNumber==SuperScoutRecord.teamNumber)).filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber, startPosition="CENTER").count()

    def getSourceAutoCount(self):
        return MatchData.query.join(SuperScoutRecord, db.and_(MatchData.matchNumber==SuperScoutRecord.matchNumber, MatchData.teamNumber==SuperScoutRecord.teamNumber)).filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber, startPosition="SOURCE").count()

    def getCenterAutoAverages(self):
        q = MatchData.query.join(SuperScoutRecord, db.and_(MatchData.matchNumber==SuperScoutRecord.matchNumber, MatchData.teamNumber==SuperScoutRecord.teamNumber)).filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber, startPosition="CENTER")
        if q.count() > 0:
            count = 0
            sum = 0
            for match in q:
                count+=1
                sum+=match.auto_speaker
            return sum/count
        else:
            return 0
    def getSourceAutoAverages(self):
        q = MatchData.query.join(SuperScoutRecord, db.and_(MatchData.matchNumber==SuperScoutRecord.matchNumber, MatchData.teamNumber==SuperScoutRecord.teamNumber)).filter_by(eventKey=getActiveEventKey(), teamNumber=self.teamNumber, startPosition="SOURCE")
        if q.count() > 0:
            count = 0
            sum = 0
            for match in q:
                count+=1
                sum+=match.auto_speaker
            return sum/count
        else:
            return 0


class ActiveEventKey(db.Model):
    __tablename__ = 'activeeventkey'
    index = db.Column(db.Integer(), primary_key = True)
    activeEventKey = db.Column(db.String(50))

    def __init__(self, activeEventKey):
        self.index = 1
        self.activeEventKey = activeEventKey

class MatchSchedule(db.Model):
    __tablename__ = 'match_schedule'
    eventKey = db.Column(db.String(50), primary_key = True)
    matchNumber = db.Column(db.Integer(), primary_key = True)
    matchLevel = db.Column(db.String(50), primary_key = True)
    red1 = db.Column(db.String(50))
    red2 = db.Column(db.String(50))
    red3 = db.Column(db.String(50))
    blue1 = db.Column(db.String(50))
    blue2 = db.Column(db.String(50))
    blue3 = db.Column(db.String(50))

    def __init__(self, eventKey, matchNumber, matchLevel, red1, red2, red3, blue1, blue2, blue3):
        self.eventKey = eventKey
        self.matchNumber = matchNumber
        self.matchLevel = matchLevel
        self.red1 = red1
        self.red2 = red2
        self.red3 = red3
        self.blue1 = blue1
        self.blue2 = blue2
        self.blue3 = blue3

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def checkIsScouted(self):
        if MatchData.query.filter_by(eventKey=self.eventKey, matchNumber=self.matchNumber, matchLevel=self.matchLevel).count() > 0:
            return True
        else:
            return False
    def checkIfTeamScouted(self, team):
        if MatchData.query.filter_by(eventKey=self.eventKey, matchNumber=self.matchNumber, matchLevel=self.matchLevel, teamNumber=team).count() > 0:
            return True
        else:
            return False
    def checkIfTeamHasPlayedMatch(self, team):
        if MatchData.query.filter_by(eventKey=self.eventKey, teamNumber=team).count() > 0:
            return True
        else:
            return False
    def checkIfCanBePreviewed(self):
        if self.checkIfTeamHasPlayedMatch(self.red1):
            return True
        if self.checkIfTeamHasPlayedMatch(self.red2):
            return True
        if self.checkIfTeamHasPlayedMatch(self.red3):
            return True
        if self.checkIfTeamHasPlayedMatch(self.blue1):
            return True
        if self.checkIfTeamHasPlayedMatch(self.blue2):
            return True
        if self.checkIfTeamHasPlayedMatch(self.blue3):
            return True     
        return False  
    def renderEventLevel(self):
        if (self.matchLevel=='qm'):
            return "Qualification Match"
        elif (self.matchLevel=='f'):
            return "Finals Match"
        else:
            return "Playoff Match"
    
class TeamAtEvent(db.Model):
    __tablename__ = 'teamatevent'
    eventKey = db.Column(db.String(50), primary_key = True)
    teamNumber = db.Column(db.Integer(), primary_key = True)
    def __init__(self, teamNumber, eventKey):
        self.teamNumber = teamNumber
        self.eventKey = eventKey

class DataValidation(db.Model):
    __tablename__ = 'data_validation'
    eventKey = db.Column(db.String(15), primary_key=True)
    matchNumber = db.Column(db.Integer(), primary_key=True)
    matchLevel = db.Column(db.String(50), primary_key=True)
    alliance = db.Column(db.Integer(), primary_key=True)
    auto_speaker = db.Column(db.Integer())
    auto_amp = db.Column(db.Integer())
    tele_speaker = db.Column(db.Integer())
    tele_amp = db.Column(db.Integer())
    trap = db.Column(db.Integer())
    climb = db.Column(db.Integer())
    defense = db.Column(db.Integer())
    auto_leave = db.Column(db.Integer())

class MatchAverages():
    def __init__(self, teamNumber):
        self.teamNumber = teamNumber
        self.auto_speaker = 0.0
        self.auto_amp = 0.0
        self.tele_speaker = 0.0
        self.tele_amp = 0.0
        self.trap = 0
        self.climb = 0.00
        self.defense = "N/A"
        self.auto_leave = 0.00
        self.count = 0
        self.climbAttempts = 0
    def addAverage(self, matchData):
        self.auto_speaker=(self.auto_speaker*self.count+matchData.auto_speaker)/(self.count+1)
        self.auto_amp=(self.auto_amp*self.count+matchData.auto_amp)/(self.count+1)
        self.tele_speaker=(self.tele_speaker*self.count+matchData.tele_speaker)/(self.count+1)
        self.tele_amp=(self.tele_amp*self.count+matchData.tele_amp)/(self.count+1)
        self.trap=(self.trap*self.count+matchData.trap)/(self.count+1)
        if (matchData.climb > 0):
            self.climb=(self.climb*self.climbAttempts+1)/(self.climbAttempts+1)
            self.climbAttempts+=1
        elif (matchData.climb == -1):
            self.climb=(self.climb*self.climbAttempts)/(self.climbAttempts+1)
            self.climbAttempts+=1
        if (matchData.auto_leave != 0):
            self.auto_leave=(self.auto_leave*self.count+1)/(self.count+1)
        else:
            self.auto_leave=(self.auto_leave*self.count)/(self.count+1)
        self.count += 1
    def scoreMatch(self):
        score = 0
        score += self.auto_speaker * 5
        score += self.auto_amp * 2
        score += self.tele_speaker * 2
        score += self.auto_amp
        score += self.trap * 5
        score += self.climb * 3
        score += self.auto_leave * 2
        return score

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