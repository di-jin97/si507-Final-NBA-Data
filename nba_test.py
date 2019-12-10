import unittest
from nba import *
from nba_plot import *

class TestDatabase(unittest.TestCase):

    def test_player_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Players'
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertIn(('J.J. Barea',), result_list)
        self.assertIn(('Chris Paul',), result_list)
        self.assertEqual(len(result_list), 465)

        sql = '''
            SELECT Name, age, Weight, height
            FROM Players
            WHERE age < 21
            ORDER BY Weight DESC
        '''    
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 37)
        self.assertEqual(result_list[0][3], '6-9')
        self.assertEqual(result_list[8][1], 19)
        conn.close()
        
        
    def test_team_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Teams'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Utah Jazz',), result_list)
        self.assertEqual(len(result_list), 30)
        sql = '''
            SELECT Name,Arena,win,coach
            FROM Teams
            WHERE win>15
            ORDER BY  win
        ''' 

        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 7)
        self.assertEqual(result_list[2][3], 'Doc Rivers')
        conn.close()
        
    def test_Players2019(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT name FROM players2019'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Charlie Brown',), result_list)
        self.assertEqual(len(result_list), 465)
        sql = '''
            SELECT Name, position, Assists, "Total points", Team, "Games played"
            FROM Players2019
            WHERE team = "DET"
			ORDER BY "Games played" DESC
        '''    
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertEqual(len(result_list), 16)
        self.assertEqual(result_list[0][1], 'SG')
        conn.close()
        
    
class TestMapping(unittest.TestCase):
    # can't test to see if the maps are correct, but we can test that
    # the functions don't return an error!
    def test_compare(self):
        try:
            compare('LAC','LAL')
        except:
            self.fail()

    def test_show_arena(self):
        try:
            showarena()
        except:
            self.fail()
    def test_show_players(self):
        try:
            showplayers('DET')
        except:
            self.fail()
    def test_show_relation(self):
        try:
            showrelation(['null','assist','2point'])
        except:
            self.fail()


        
unittest.main()