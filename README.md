# si507-Final-NBA-Data
SI 507 Final Project Readme
Di Jin

# Project Summary
An interactive program that lets user choose any NBA player or NBA team and get their data presented in a infographic manner.

Data Source:
BasketBall-Reference: https://www.basketball-reference.com/

Presentation Package:
Plotly: https://plot.ly/

# Instructions

0) The program will utilize the online Plotly Website, please see this page if you do not have a plotly account set up. (https://plot.ly/python/getting-started/)

1) Run nba.py to get the most recent data and then write the data to SQL databse using json file
(This might take up to 15 minutes if no cache is available because there are more than 450 currently active nba players and 30 NBA teams)
2) Run nba_plot.py to have fun!

Optional: nba_test.py is the unittest file for this project

# How it works

1) The program scrapes NBA Player data from Basketball Reference, caches the html, and stores the useful data into a json file 
2) The data from json file is used to create a sqlite database.
3) There are four plot options, the user could type the following four command to draw the graph.
  a. "Arena location":
      This command

