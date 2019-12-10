import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import sys
import plotly.graph_objs as go
from time import strptime
import datetime
import numpy as np
import plotly.express as px
#import plotly.plotly as py
#from plotly.subplots import make_subplots



google_places_key = 'AIzaSyA7SpYbjtVmddhKpJXvgZ32W2uCkAxPI4E'
mapbox_access_token = "pk.eyJ1IjoicHJpbmNpcGxleiIsImEiOiJjam1taTE3dGowamRjM3FqcG50MGp0anEwIn0.XuaFZy4Tff6aTfjiQUdd9Q"

DBNAME = 'nba.db'
CACHE_FNAME = 'cache.json'

def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    
    statement = '''
        DROP TABLE IF EXISTS 'Players';
    '''
    cur.execute(statement)
    conn.commit()
    
    statement = '''
        DROP TABLE IF EXISTS 'Players2019';
    '''
    cur.execute(statement)
    conn.commit()
    
    statement = '''
        DROP TABLE IF EXISTS 'Teams';
    '''
    cur.execute(statement)
    conn.commit()
    
    statement = '''
        CREATE TABLE 'Players' (
                'Name' TEXT NOT NULL,
                'Age' INTEGER,
                'Position' TEXT,
                'Height' TEXT,
                'Weight' INTEGER,
                'Shoot' TEXT,
                'Born' TEXT,
                'Experience' INTEGER,
                'NBA Debut' TEXT,
                 FOREIGN KEY ('Name')
                 REFERENCES 'Players2019' ('Name')
                 ON UPDATE CASCADE ON DELETE CASCADE
        );
    '''
    cur.execute(statement)
    conn.commit()
    
    statement = '''
        CREATE TABLE 'Players2019' (
                'Name' TEXT NOT NULL,
                'Team' TEXT,
                'Position' TEXT,
                'Games Played' INTEGER,
                'Games Started' INTEGER,
                'Minutes Played' FLOAT,
                'Field Goals' FLOAT,
                'Field Goals Percentage' FLOAT,
                '3 Point Field Goals' FLOAT,
                '3 Point Field Goals Percentage' FLOAT,
                'Assists' FLOAT,
                'Rebounds' FLOAT,
                'Total Points' FLOAT,
                 FOREIGN KEY ('Team')
                 REFERENCES 'Teams' ('Nameabbr')
                 ON UPDATE CASCADE ON DELETE CASCADE
                
        );
    '''
    cur.execute(statement)
    conn.commit()
    
    statement = '''
        CREATE TABLE 'Teams' (
                'Name' TEXT NOT NULL,
                'Nameabbr' TEXT NOT NULL,
                'Record' TEXT,
                'Win' INTEGER,
                'Loss' INTEGER,
                'Coach' TEXT,
                'Executive' TEXT,
                'Arena' TEXT,
                'W/E' TEXT,
                'PTS/G' FLOAT,
                'Next Game' TEXT
        );
    '''
    cur.execute(statement)
    conn.commit()
    
    conn.close()



try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}

# A helper function that accepts 2 parameters
# and returns a string that uniquely represents the request
# that could be made with this info (url + params)


def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_" + "_".join(res)
  

def make_request_using_cache(url,params):
    unique_ident = params_unique_combination(url,params)
    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url,params)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]




def get_2019nba_players():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    baseurl = 'https://www.basketball-reference.com/leagues/NBA_2020_per_game.html'
    params = {}
    page_text = make_request_using_cache(baseurl,params)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    player_content = page_soup.find_all(class_="full_table")
    namelist = []
    playerlist = []
    for each in player_content:
        left = each.find_all(class_ = 'left')
        playername = left[0].text
        playerteam = left[1].text
        playerlist.append(playername)
        namelist.append(playername)
        position = each.find(class_='center').text
        other = each.find_all(class_='right')
        games = other[2].text
        games_started = other[3].text
        minutes = other[4].text
        field_goals = other[5].text
        field_goals_rate = other[7].text
        three_point = other[8].text
        three_point_rate = other[10].text
        assist = other[21].text
        rebound = other[20].text
        totalpoint = other[26].text
        state = [playername,playerteam,position,games,games_started,minutes,field_goals,\
                 field_goals_rate,three_point,three_point_rate,assist,rebound,totalpoint]
        cur.execute("INSERT INTO Players2019 (Name,Team,Position,'Games Played','Games Started',\
                                                          'Minutes Played','Field Goals','Field Goals Percentage',\
                                                          '3 Point Field Goals','3 Point Field Goals Percentage',\
                                                          Assists,Rebounds,'Total Points') \
                                                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);", state)
        conn.commit()

    conn.close()
    return namelist
    

def get_player():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    baseurl = 'https://www.basketball-reference.com/leagues/NBA_2020_per_game.html'
    url = 'https://www.basketball-reference.com'
    params = {}
    page_text = make_request_using_cache(baseurl,params)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    player_content = page_soup.find_all(class_="full_table")
    for each in player_content:
        left = each.find(class_ = 'left')
        i=1
        for a in left.find_all('a',href=True):
            playerurl = url + a['href']
            page_text = make_request_using_cache(playerurl,params)
            page_soup = BeautifulSoup(page_text, 'html.parser')
            meta = page_soup.find(id="meta")
            name = meta.find('h1').text
            #print(name)
            info = meta.find_all('p')
            position = ''
            teamname = ''
            height = ''
            weight = ''
            age = ''
            dob = ''
            if info[3].text.split()[0] == 'Position:':
                pands = info[3].text.split()
                for i in range(len(pands)):
                    if pands[i] == '▪':
                        index = i
                temp = ''
                for j in pands[1:index]:
                    temp = temp + j + ' '
                    position = temp
                shoot = pands[-1]
                height = info[4].text.split()[0].replace(',','')
                weight = info[4].text.split()[1].replace('lb','')
                team = info[5].text.split()[1:]
                teamname = ''
                for each in team:
                    teamname = teamname + each+' '
                birth = info[6].text.split()
                month = birth[1]
                date = birth[2].replace(',','')
                year = birth[3]
                month_number = strptime(month[0:3], '%b').tm_mon
                if month_number < 10:
                    month_number = str(month_number).zfill(2)
                if int(date) < 10:
                    date = str(date).zfill(2)
                dob = year + '-' + str(month_number) + '-' + date
                now = datetime.datetime.now()
                age = now.year - int(year)
                #print(teamname)
                
                
            elif info[1].text.split()[0] == 'Position:':
                pands = info[1].text.split()
                for i in range(len(pands)):
                    if pands[i] == '▪':
                        index = i
                temp = ''
                for j in pands[1:index]:
                    temp = temp + j + ' '
                    position = temp
                shoot = pands[-1]
                height = info[2].text.split()[0].replace(',','')
                weight = info[2].text.split()[1].replace('lb','')
                #print(height)
                if info[3].text.split()[0] == 'Team:':
                    team = info[3].text.split()[1:]
                    teamname = ''
                    for each in team:
                        teamname = teamname + each+' '
                    birth = info[4].text.split()
                    month = birth[1]
                    date = birth[2].replace(',','')
                    year = birth[3]
                    month_number = strptime(month[0:3], '%b').tm_mon
                    if month_number < 10:
                        month_number = str(month_number).zfill(2)
                    if int(date) < 10:
                        date = str(date).zfill(2)
                    dob = year + '-' + str(month_number) + '-' + date
                    now = datetime.datetime.now()
                    age = now.year - int(year)
                    #print(teamname)
                    
                    
                    
                    
            elif info[4].text.split()[0] == 'Position:':
                pands = info[4].text.split()
                for i in range(len(pands)):
                    if pands[i] == '▪':
                        index = i
                temp = ''
                for j in pands[1:index]:
                    temp = temp + j + ' '
                    position = temp
                shoot = pands[-1]
                height = info[5].text.split()[0].replace(',','')
                weight = info[5].text.split()[1].replace('lb','')
                #print(height)
                if info[6].text.split()[0] == 'Team:':
                    team = info[6].text.split()[1:]
                    teamname = ''
                    for each in team:
                        teamname = teamname + each+' '
                    birth = info[7].text.split()
                    month = birth[1]
                    date = birth[2].replace(',','')
                    year = birth[3]
                    month_number = strptime(month[0:3], '%b').tm_mon
                    if month_number < 10:
                        month_number = str(month_number).zfill(2)
                    if int(date) < 10:
                        date = str(date).zfill(2)
                    dob = year + '-' + str(month_number) + '-' + date
                    now = datetime.datetime.now()
                    age = now.year - int(year)
                    #print(teamname)
                
            else:   
                pands = info[2].text.split()
                for i in range(len(pands)):
                    if pands[i] == '▪':
                        index = i
                temp = ''
                for j in pands[1:index]:
                    temp = temp + j + ' '
                    position = temp
                shoot = pands[-1]
                height = info[3].text.split()[0].replace(',','')
                weight = info[3].text.split()[1].replace('lb','')
                team = info[4].text.split()[1:]
                teamname = ''
                for each in team:
                    teamname = teamname + each+' '
                birth = info[5].text.split()
                month = birth[1]
                date = birth[2].replace(',','')
                year = birth[3]
                month_number = strptime(month[0:3], '%b').tm_mon
                if month_number < 10:
                    month_number = str(month_number).zfill(2)
                if int(date) < 10:
                    date = str(date).zfill(2)
                dob = year + '-' + str(month_number) + '-' + date
                now = datetime.datetime.now()
                age = now.year - int(year) 
               
                
            experience = info[-1].text.split()
            exyear = experience[1]
            if exyear == 'Rookie':
                exyear = 0
            else:
                exyear = int(experience[1])
            nbadebut = info[-2].text.split()
            nbamonth = strptime(nbadebut[2][0:3], '%b').tm_mon
            nbayear = nbadebut[4]
            nbadate = nbadebut[3].replace(',','')
            if nbamonth < 10:
                nbamonth = str(nbamonth).zfill(2)
            if int(nbadate) < 10:
                nbadate = str(nbadate).zfill(2)
            debutdate = nbayear + '-' + str(nbamonth) +'-' + nbadate
            state = [name,age,position,height,weight,shoot,dob,exyear,debutdate]
            cur.execute("INSERT INTO Players (Name,Age,Position,Height,Weight,Shoot,Born,Experience,'NBA Debut') \
                        VALUES (?,?,?,?,?,?,?,?,?);", state)
            conn.commit()
    conn.close()


   
def get_team():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    params = {}
    baseurl = 'https://www.basketball-reference.com'
    leagues = '/leagues/NBA_2020_standings.html'
    regionlist = ['all_confs_standings_W','all_confs_standings_E']
    for r in regionlist:
        page_text = make_request_using_cache(baseurl + leagues,params)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        bothteam = page_soup.find(id=r)
        teams = bothteam.find_all(class_='left')
        for each in teams:
            for team in each.find_all('a',href=True, text=True):
                teamname = team.text
                teamurl = baseurl + team['href']
                nameabbr = team['href'].split('/')[2]
                page_text = make_request_using_cache(teamurl,params)
                page_soup = BeautifulSoup(page_text, 'html.parser')
                teaminfo = page_soup.find(id = "meta")
                info = teaminfo.find_all('p')
                arena = info[12].text.split()
                record = info[2].text.split()[1].replace(',','')
                win = record.split('-')[0]
                loss = record.split('-')[1]
                coach = info[5].text.split()
                coachname = coach[1] +' '+coach[2]
                pts = info[7].text.split()[1]
                executive = info[6].text.split()
                executivename = executive[1] +' '+executive[2]
                if r == 'all_confs_standings_E':
                    region = 'East'
                else:
                    region = 'West'
                nextgame = info[4].text.split()[2:]
                temp = ''
                for i in nextgame:
                    temp = temp + i + ' '
                nextinfo = temp
                temp = ''
                if arena[0] == 'Arena:':
                    for i in range(len(arena)):
                        if arena[i] == 'Attendance:':
                            end = i
                    for j in arena[1:end]:
                        temp = temp + j + ' '
                    arenaname = temp
                else: 
                    arenaname = 'N/A'
                           
                state = [teamname,nameabbr,record,win,loss,coachname,executivename,arenaname,region,pts,nextinfo]
                cur.execute("INSERT INTO Teams ('Name', Nameabbr, Record, Win, Loss, Coach,Executive,Arena,'W/E','PTS/G','Next Game') VALUES (?,?,?,?,?,?,?,?,?,?,?);", state)
                conn.commit()
 


    
if __name__=="__main__":
    init_db()
    get_2019nba_players()
    get_team()
    get_player()

'''init_db()
get_2019nba_players()
get_team()
get_player()'''