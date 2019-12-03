# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 21:33:59 2019

@author: 14847
"""

import requests
import json
from bs4 import BeautifulSoup
import sqlite3


DBNAME = 'nba.db'

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
                'ID' INTEGER PRIMARY KEY AUTOINCREMENT,
                'Name' TEXT NOT NULL,
                'Nickname' TEXT,
                'Position' TEXT,
                'Height' TEXT,
                'Weight(lb)' INTEGER,
                'Team' TEXT,
                'Born' REAL
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
                'Total Points' FLOAT
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


init_db()



CACHE_FNAME = 'cache.json'
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


def get_unique_key(url):
  return url
  

def make_request_using_cache(url):
    unique_ident = get_unique_key(url)
    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]




def get_nba_players():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    baseurl = 'https://www.basketball-reference.com/leagues/NBA_2020_per_game.html'
    page_text = make_request_using_cache(baseurl)
    page_soup = BeautifulSoup(page_text, 'html.parser')
    #print(page_soup)
    player_content = page_soup.find_all(class_="full_table")
    for each in player_content:
        left = each.find_all(class_ = 'left')
        playername = left[0].text
        playerteam = left[1].text
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
        state = [playername,playerteam,position,games,games_started,minutes,field_goals,field_goals_rate,three_point,three_point_rate,assist,rebound,totalpoint]
        cur.execute("INSERT INTO Players2019 (Name,Team,Position,'Games Played','Games Started',\
                                                          'Minutes Played','Field Goals','Field Goals Percentage',\
                                                          '3 Point Field Goals','3 Point Field Goals Percentage',\
                                                          Assists,Rebounds,'Total Points') \
                                                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?);", state)
        conn.commit()

    conn.close()
    
    



   
def get_team():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    baseurl = 'https://www.basketball-reference.com'
    leagues = '/leagues/NBA_2020_standings.html'
    #page_text = make_request_using_cache(baseurl + leagues)
    #page_soup = BeautifulSoup(page_text, 'html.parser')
    regionlist = ['all_confs_standings_W','all_confs_standings_E']
    for r in regionlist:
        page_text = make_request_using_cache(baseurl + leagues)
        page_soup = BeautifulSoup(page_text, 'html.parser')
        bothteam = page_soup.find(id=r)
        teams = bothteam.find_all(class_='left')
        for each in teams:
            for team in each.find_all('a',href=True, text=True):
                teamname = team.text
                teamurl = baseurl + team['href']
                nameabbr = team['href'].split('/')[2]
                page_text = make_request_using_cache(teamurl)
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
                #print(pts)
                
                state = [teamname,nameabbr,record,win,loss,coachname,executivename,arenaname,region,pts,nextinfo]
                cur.execute("INSERT INTO Teams ('Name', Nameabbr, Record, Win, Loss, Coach,Executive,Arena,'W/E','PTS/G','Next Game') VALUES (?,?,?,?,?,?,?,?,?,?,?);", state)
                conn.commit()
                #print(state)

    
    
#get_nba_players() 
init_db()
get_nba_players()
get_team()