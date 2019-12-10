#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 10 01:56:56 2019

@author: di
"""
import requests
import json
import sqlite3
import plotly.graph_objs as go
import numpy as np
import plotly.express as px
from secrets import google_places_key 
from secrets import mapbox_access_token 


#google_places_key = 'AIzaSyA7SpYbjtVmddhKpJXvgZ32W2uCkAxPI4E'
#mapbox_access_token = "pk.eyJ1IjoicHJpbmNpcGxleiIsImEiOiJjam1taTE3dGowamRjM3FqcG50MGp0anEwIn0.XuaFZy4Tff6aTfjiQUdd9Q"

DBNAME = 'nba.db'
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
        #print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        #print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url,params)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        return CACHE_DICTION[unique_ident]



def load_help_text():
    with open('help.txt') as f:
        return f.read()           
            
def interactive_prompt():
    
    help_text = load_help_text()
    response = ''
    while response != 'exit':
        response = input('Enter a command: ')
        if len(response) > 0 and response != 'help' and response != 'exit':
            process_command(response)
        if response == 'help':
            print(help_text)
            continue
    print('bye')


    
def process_command(command):
    command = command.lower()
    list1 = ['experience','age','gameplayed','2point','3point','assist','rebound','points']
    list2 = ['LAL','LAC','DAL','HOU','DEN','UTA','OKC','PHO','MIN','SAC','SAS','POR','MEM',
             'NOP','GSW','MIL','BOS','MIA','PHI','TOR','IND','BRK','ORL','DET','CHO','CHI','WAS','ATL','CLE','NYK']
    each_command = command.split()
    if each_command[0] == 'arena' and each_command[1] == 'location':
        showarena()
    if each_command[0] == 'players' and each_command[1] == 'in':
        showplayers(each_command[2])
    if each_command[0] == 'players' and each_command[1] in list1 and each_command[2] in list1:
        showrelation(each_command)
    if each_command[0] == 'compare' and each_command[1].upper() in list2 and each_command[2].upper() in list2: 
        compare(each_command[1].upper(),each_command[2].upper())
 

def compare(team1,team2):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    state = f'SELECT win, "PTS/G" From teams WHERE nameabbr = "{team1}"'
    cur.execute(state)
    for row in cur:
        t1win = row[0]
        t1p = row[1]
    conn.commit()
    
    state = f'SELECT win, "PTS/G" From teams WHERE nameabbr = "{team2}"'
    cur.execute(state)
    for row in cur:
        t2win = row[0]
        t2p = row[1]
    conn.commit()
    
    state = f'SELECT assists,rebounds,"3 Point Field Goals" From Players2019\
                where team="{team1}"'
    cur.execute(state)
    t1a = []
    t1r = []
    t13 = []
    for row in cur:
        t1a.append(row[0])
        t1r.append(row[1])
        t13.append(row[2])
    conn.commit()
    state = f'SELECT assists,rebounds,"3 Point Field Goals" From Players2019\
                where team="{team2}"'
    cur.execute(state)
    t2a = []
    t2r = []
    t23 = []
    for row in cur:
        t2a.append(row[0])
        t2r.append(row[1])
        t23.append(row[2])
    conn.commit()
    
    stats = ['Win', 'PTS/G', 'Assists','Rebounds','3Points']
    fig = go.Figure(data=[
            go.Bar(name=team1, x=stats, y=[t1win,t1p,np.sum(t1a),np.sum(t1r),np.sum(t13)]),
            go.Bar(name=team2, x=stats, y=[t2win,t2p,np.sum(t2a),np.sum(t2r),np.sum(t23)])
                ])

    fig.update_layout(barmode='group')
    fig.show()
    conn.close()
    


      
def showarena():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    
    statement = '''
        SELECT arena FROM teams
    '''
    cur.execute(statement)
    result =[]
    eachlocation = []
    for row in cur:
        result.append(row)
    for each in result:
        if each[0] != 'N/A':
            eachlocation.append(each[0].rstrip())
    conn.commit()
    conn.close
    lat = []
    lng = []
    arenaname = []
    for each in eachlocation:
        arenaname.append(each)
        queryurl = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        param = {'query':each+ ' '+'basketball','key':google_places_key}
        #print(param)
        page_text = make_request_using_cache(queryurl,param)
        page_text = json.loads(page_text)
        #print(page_text)
        result = page_text['results'][0]['geometry']['location']
        lat.append(result['lat'])
        lng.append(result['lng'])


    data = [
        go.Scattermapbox(
            lat=lat,
            lon=lng,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=9
            ),
            text=arenaname,
        )
    ]
    
    layout = go.Layout(
        autosize=True,
        hovermode='closest',
        mapbox=go.layout.Mapbox(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=np.mean(lat),
                lon=np.mean(lng)
            ),
            pitch=0,
            zoom=3
        ),
    )

    fig = go.Figure(data=data, layout=layout)
    fig.show()
    
    
    
    
    
def showplayers(teamname):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    teamname = teamname.upper()
    statement = '''
        SELECT name,position,"Total Points"
        FROM Players2019
    '''
    statement += f'where team = "{teamname}" '
    cur.execute(statement)
    result = []
    pos = []
    point = []
    for row in cur:
        result.append(row[0])
        pos.append(row[1])
        point.append(row[2])
    conn.commit()
    fig = go.Figure(data=[go.Table(header=dict(values=[f"Player Name","Position","Ave Points"]),
                 cells=dict(values=[result,pos,point]))
                     ])
    fig.update_layout(
            title={'text':teamname,'y':0.9,'x':0.5,'xanchor':'center','yanchor': 'top'}
            )
    fig.show()
    conn.close
    
    
def showrelation(command):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    dic1 = {"experience":"experience",
            "age":"Age",
            "gameplayed":"Games Played",
            "2point" : "Field Goals",
            "3point" : "3 point field goals",
            "assist" : "Assists",
            "rebound" : "Rebounds",
            "points" : "Total Points"
            }
    first = dic1.get(command[1])
    second = dic1.get(command[2])
    state = f'Select "{first}","{second}"'
    state += 'from players JOIN Players2019 on Players2019.Name= Players.name'
    cur.execute(state)
    l1 = []
    l2 = []
    for row in cur:
        if row[0] != '' and row[1] != '':
            l1.append(row[0])
            l2.append(row[1])
    conn.commit()
    conn.close()
    fig = px.scatter(x=l1, y=l2,trendline="ols",labels={'x':first, 'y':second})
    fig.show()
    
if __name__=="__main__":
    interactive_prompt()