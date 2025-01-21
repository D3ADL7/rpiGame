### IMPORTS ############################################################################
import guizero as gz
from guizero import PushButton as btn
from guizero import TextBox as txt
from guizero import Box as Box
from guizero import Text as TxT
import threading
import time
import random
from multiprocessing import Pool as p
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import pyodbc
from datetime import datetime
import uuid as guid

dn = 'SQL SERVER'
sn = 'sepdegraaffserver.database.windows.net'
db = 'Thema10'
username = 'sepdegraaff'  # Replace with your Azure SQL username
password = 'P@ssword'  # Replace with your Azure SQL password

cs = f"""
    DRIVER={{{dn}}};
    SERVER={sn};
    DATABASE={db};
    UID={username};
    PWD={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
"""

class UserScore:
    def __init__(self, username: str, date: str, time_score: str):
        self.username = username
        
        # Validate and set the date
        try:
            self.date = datetime.strptime(date, "%d/%m/%Y").strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError("Date must be in dd/mm/yyyy format.")
        
        # Validate and set the time score
        if not self._validate_time_score(time_score):
            raise ValueError("TimeScore must be in minutes:seconds:milliseconds format.")
        self.time_score = time_score

    @staticmethod
    def _validate_time_score(time_score: str) -> bool:
        parts = time_score.split(":")
        if len(parts) != 3:
            return False
        try:
            minutes = int(parts[0])
            seconds = int(parts[1])
            milliseconds = int(parts[2])
            return 0 <= seconds < 60 and 0 <= milliseconds < 1000
        except ValueError:
            return False

    def __str__(self):
        return f"Username: {self.username}, Date: {self.date}, TimeScore: {self.time_score}"



########################################################################################

#Make window login #####################################################################
login = gz.App(layout="grid", width=200, height=100, title="Login")
lb_login = TxT(login, text="Uw studentnummer", grid=[0, 0], width=20)
txt_login = txt(login, text="", grid=[0, 1], width=20)
btn_login = btn(login, text="Ga veder", grid=[0,2], width=10, command=login.destroy)
login.display()

#Save student numb
student = txt_login.value if hasattr(txt_login, 'value') else txt_login.get()

# window finish & FunctionButtons #######################################################
def closeGame():
    myapp.destroy()
    finishwindow.destroy()

def SetDatOnline():
    global student
    global length
    global cs
    today = datetime.today()
    formatted_date = today.strftime("%d/%m/%Y")
    minutes = int(length // 60)
    seconds = int(length % 60)
    milliseconds = int((length % 1) * 1000)

    formatted_time = f"{minutes}:{seconds:02}:{milliseconds:03}"
    user = UserScore(student,formatted_date,formatted_time)
    c = pyodbc.connect(cs)
    cur = c.cursor()
    insert_data(user.username,user.date,user.time_score)
    closeGame()
    
def insert_data(s,d,t):
    global cs
    c = pyodbc.connect(cs)
    insert_query = """
    INSERT INTO PlayerScores (Player, Score, Date)
    VALUES (?, ?, ?)
    """
    c.execute(insert_query, (s, t, d))
    print("succes")
    c.commit()
    c.close()





#Make window game
myapp = gz.App(layout="grid", width=590, height=250, title="Escape the Test-Lab")

# 2D MAP class + Fuctions ##############################################################
class TwoDArray:
    def __init__(self, rows, cols, initial_value=0):
        self.rows = rows
        self.cols = cols
        self.array = [[{'value': initial_value, 'explored': False} for _ in range(cols)] for _ in range(rows)]
    #Make xy
    def get_element(self, row, col):
        return self.array[row][col]['value']
    
    #Set element manually
    def set_element(self, row, col, value):
        self.array[row][col]['value'] = value
    
    #Set x or y is explored
    def set_explored(self, row, col, explored=True):
        self.array[row][col]['explored'] = explored
    
    #Set x or y has already been explored
    def is_explored(self, row, col):
        return self.array[row][col]['explored']
    
    #Display player as 1 on the map
    def display(self):
        for row in self.array:
            print([cell['value'] for cell in row])
            
    def RandomMap(self, min_value=0, max_value=10):
        for i in range(self.rows):
            for j in range(self.cols):
                self.array[i][j]['value'] = random.randint(min_value, max_value)
                
    def count_value(self, value):
        count = 0
        for row in self.array:
            for cell in row:
                if cell['value'] == value:
                    count += 1
        return count            
                
#Render table/map ########################################## ADD ENTITIES HERE ##########
                #CELL VALUE PROCESSOR
w = 0
def process_row(row_data, r, results):
    global w
    global myint
    global myinttwo
    global myintthree
    global myintfour
    global myintfive
    row_result = []
    for c, cell in enumerate(row_data):
        if cell['explored']:
            text = str(cell['value'])
            cell_color = "blue"
            if cell['value'] == 7:  # Zombie
                death()
                cell_color = "red"
            elif cell['value'] == myint: ##### ADD IF ELSE 'elif'
                cell_color = "green"
            elif cell['value'] == myinttwo: ##### ADD IF ELSE 'elif'
                cell_color = "yellow"
            elif cell['value'] == myintthree: ##### ADD IF ELSE 'elif'
                cell_color = "orange"
            elif cell['value'] == myintfour: ##### ADD IF ELSE 'elif'
                cell_color = "purple"
            elif cell['value'] == myintfive: ##### ADD IF ELSE 'elif'
                cell_color = "brown"
        else:
            text = str(cell['value'])
            cell_color = "white"
        row_result.append((c, r, text, cell_color))
    results[r] = row_result
    myresults = results
    myr = r
    mydata = row_data

#DISPLAY OF THE MAP ###########
def render_map():
    results = [None] * map_2d.rows  # Shared list to store results from threads

    # Use a ThreadPoolExecutor to limit the number of threads
    with ThreadPoolExecutor(max_workers=4) as executor:
        for r in range(map_2d.rows):
            row_data = map_2d.array[r]
            executor.submit(process_row, row_data, r, results)
            
    draw = True
    if draw:
        drawMap(draw,results)
        draw = False #END FUNCTION
    
# List to keep track of the current map elements
current_map_elements = []

def drawMap(draw, results):
    global current_map_elements
    
    #CLREAR OLD MAP
    for element in current_map_elements:
        element.destroy() #ERASE FROM MEMEORY
    current_map_elements = []

    #DRAW NEW MAP
    if draw:
        for row_result in results:
            for c, r, text, cell_color in row_result:
                box = Box(myapp, width=30, height=30, grid=[c, r], border=True) #CELLS SIZE AND STYLE
                box.bg = cell_color
                current_map_elements.append(box) #ADD NEW BOXES
                label = TxT(box, text=text, color="black", size=10)
                current_map_elements.append(label) #ADD NEW LABELS
                #END FUNCTION

## EVENT UPON DEATH ##
def death():
    global org_player_pos
    global player_pos
    for r in range(map_2d.rows):
        for c in range(map_2d.cols):
            cell = map_2d.array[r][c]
            cell['explored'] = False #RESET PATH
    # RESET CURRENT PLAYER POS TO ORIGINAL PLAYER POS.
    player_pos[0] = org_player_pos
    player_pos[1] = org_player_pos_
    #END FUNCTION

attempts = 1
#Key listener for movement within the map.
def handle_keypress(event):
        if event.tk_event.keysym == "Up":
            move_player(-1, 0)
        elif event.tk_event.keysym == "Down":
            move_player(1, 0)
        elif event.tk_event.keysym == "Left":
            move_player(0, -1)
        elif event.tk_event.keysym == "Right":
            move_player(0, 1)
        elif event.tk_event.keysym == "Return":
            winlose()
            #END FUNCTION
        

def displayFinihWindow():
########################################################################################
    finishwindow = gz.App(layout="grid", width=300, height=100, title="Result")
    lb_login = TxT(finishwindow, text="JIJ HEBT GEWONNEN", grid=[0, 0], width=20)
    btn_finishOk = btn(finishwindow, text="Set Online", grid=[1, 1], width=10, command=SetDatOnline)
    btn_finishNo = btn(finishwindow, text="Cancel", grid=[0, 1], width=10, command=closeGame)


###################### WIN LOSE FUNCTION
length = time.time()
won = False
start = time.time()
def winlose():
    global attempts
    global solution
    global solved
    global txt_pnc
    global start
    global length
    global won
    mytext = ""
    user_input = txt_pnc.value if hasattr(txt_pnc, 'value') else txt_attempt.get()
    print("the solution = " + user_input)
    if str(user_input) == str(solution):
        solved = True
    
    if solved == False and attempts < 5:
        mytext = "FAIL"
    elif solved == False and attempts > 5:
        mytext = "YOU LOST"
        myapp.destroy()
    elif solved == True:
        mytext = "YOU WON"

    if user_input.isdigit() and int(user_input) == solution:
        mytext = "YOU WON"
        solved = True
        end = time.time()
        length = end - start
        won = solved
        print(length)
        displayFinihWindow();
        
    txt_attempt = TxT(myapp, text=mytext, grid=[64,attempts])    
    upAttempts = attempts + 1
    attempts = upAttempts
    
#Render movement on the map
def move_player(dx, dy):
    global player_pos
    global myresults
    new_x, new_y = player_pos[0] + dx, player_pos[1] + dy

    if 0 <= new_x < map_2d.rows and 0 <= new_y < map_2d.cols:
        map_2d.set_explored(player_pos[0], player_pos[1])#SET OLD POS EXPLORED
        player_pos[0], player_pos[1] = new_x, new_y #CHANGE TO NEW POS
        map_2d.set_explored(player_pos[0], player_pos[1]) #SET NEW POS EXPLORED
        
        render_map()
        print(str(player_pos))
        print(str(w))
        #END FUNCTION
        
###################################################################################################################

#Set up 2d map
map_2d = TwoDArray(8, 8, initial_value=0)

#Set up random player position on the map
player_pos = [random.randint(0,8), random.randint(0,8)]
org_player_pos = player_pos[0]
org_player_pos_ = player_pos[1]
#Generate random map
map_2d.RandomMap(2,9)

#Place player on the map.
map_2d.set_element(player_pos[0], player_pos[1], 1)

#Pin code input 
txt_pnc = txt(myapp, text="", grid=[64, 0], width=20)

#Render map
render_map()

#What to do if a key has been clicked
myapp.when_key_pressed = handle_keypress

#Calculate Solution code
solution = []
myint = map_2d.count_value(random.randint(2,4)) #green
myinttwo = map_2d.count_value(random.randint(4,6)) #yellow
myintthree = map_2d.count_value(random.randint(8,9)) #orange
myintfour = map_2d.count_value(random.randint(2,4)) #purple
myintfive = map_2d.count_value(random.randint(1,6)) #brown
solution = myint * myinttwo * myintthree + myintfour + myintfive

solved = False

txt_solution = TxT(myapp, text=f"Solution = count green cells", grid=[65,0])
txt_solution = TxT(myapp, text="count yellow cells", grid=[65,1])
txt_solution = TxT(myapp, text="count orange cells", grid=[65,2])
txt_solution = TxT(myapp, text="count purple cells", grid=[65,3])
txt_solution = TxT(myapp, text="count pink cells", grid=[65,4])
txt_solution = TxT(myapp, text="g * y * o + p + b", grid=[65,5])

print(solution)
print(myint)
print(myinttwo)
print(myintthree)
print(myintfour)
print(myintfive)
#Show window
myapp.display()





