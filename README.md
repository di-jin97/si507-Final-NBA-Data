# si507-Final-NBA-Data
SI 507 Final Project Readme
Di Jin

# Project Summary
An interactive program that lets user choose any NBA player or NBA team and get their data presented in a infographic manner.

Data Source:
BasketBall-Reference: https://www.basketball-reference.com/

Presentation Package:
Plotly: https://plot.ly/

Cache File:
Google Drive: https://drive.google.com/file/d/1M-G1CJCZWHb5AdKAHCd53ozbmga-oy3s/view?usp=sharing

(Because the limit of file size on Github, I put cahce file link here and it would sacve time to tun the program)

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
      This command enables user to see the map of the 30 NBA Arenas in North America.
  
  
  b. "Players in {team parameter}":
      Eg: "Players in NYK"
      This command could show the players table including their position and average points from a team.
      
      Team parameter could be the following NBA nameabbr (3 Capital characters).
      ATL -	Atlanta Hawks             BKN	- Brooklyn Nets           BOS	- Boston Celtics            
      CHA	- Charlotte Hornets         CHI	- Chicago Bulls           CLE	- Cleveland Cavaliers
      DAL	- Dallas Mavericks          DEN	- Denver Nuggets          DET	- Detroit Pistons
      GSW	- Golden State Warriors     HOU	- Houston Rockets         IND	- Indiana Pacers
      LAC	- Los Angeles Clippers      LAL	- Los Angeles Lakers      MEM	- Memphis Grizzlies
      MIA	- Miami Heat                MIL	- Milwaukee Bucks         MIN	- Minnesota Timberwolves
      NOP	- New Orleans Pelicans      NYK	- New York Knicks         OKC	- Oklahoma City Thunder
      ORL	- Orlando Magic             PHI	- Philadelphia 76ers      PHX	- Phoenix Suns
      POR	- Portland Trail Blazers    SAC	- Sacramento Kings        SAS	- San Antonio Spurs
      TOR	- Toronto Raptors           UTA	- Utah Jazz               WAS	- Washington Wizards
      
  
  
  c. "Compare {team parameter} {team parameter}":
      
      Eg: "Compare ATL DEN"
      
  This Command would enable user to compare the stats between two teams. It shows a bar chart which includes wins,          
  PTS/G(Points Per Game), average assistants, average rebounds and average 3 points field goals from two teams.
      
      
  d. "Players {stats parameter} {stats parameter}":
      
      Eg: "Players 2point assist"
      stats parameter includes: 'experience','experience','age','gameplayed', '2point','3point','assist' ,'rebound'
      ,'points'.
      
  This command enables user to see the realation between two parameter. It will use the two parameter data to draw a        
  scatter plot for all NBA players, and also draw a linear regression line for the two data. 
      
      

