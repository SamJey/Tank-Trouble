import pygame, math, random, pickle, os

BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,10,10)
L_RED = (210,0,0)
GREEN = (0,230,0)
BLUE = (0,0,255)
L_GRAY = (220,220,220)
D_GRAY = (105,105,105)

c1 = (2,89,60)
c1_= (245,205,3)
c2 = (87,35,10)
c2_=(209,190,19)
c3 = (109,143,255)
c3_=(255,0,0)
c4 = (255,157,0)
c4_ = (64,0,255)
c5=(35,255,86)
c5_=(61,35,255)
c6=(5,34,255)
c6_=(0,0,0)
c7=(255,0,0)
c7_=(0,0,0)
c8=(59,14,89)
c8_=(255,234,0)
c9=(255,234,0)
c9_=(59,14,89)

colour_dict = {c1:c1_,c2:c2_,c3:c3_,c4:c4_,c5:c5_,c6:c6_,c7:c7_,c8:c8_,c9:c9_}
def nearest(x):
    '''returns nearest integer of a float'''
    if x >= 0:
        if x%1>0.5:
            return int(x)+1
        return int(x)
    else:
        x *= -1
        if x%1>0.5:
            return -int(x)-1
        return -int(x)
 
def neighbour(point,grid):
    '''retruns negihbouring points in a grid'''
    a,b = point
    return [(x,y) for x,y in (a,b-1),(a,b+1),(a+1,b),(a-1,b) if (0<=b<17 and 0<=a<13 and grid[x][y]!=1)]

def is_connected(grid,start,stop):
    '''returns true if the tanks are connected by a path, false otherwise'''
    boundary = [start]
    came_from = {start:None}
    while boundary != []:
        current = boundary[0]
        del boundary[0]
        for Next in neighbour(current,grid):
            if Next == stop:
                return True
            if Next not in came_from:
                boundary.append(Next)
                came_from[Next] = current
    return False

        
def degree(angle):
    return (180.0*angle)/math.pi

def callback(sprite1,sprite2):
    return pygame.sprite.collide_circle(sprite1,sprite2)

class Shard(pygame.sprite.Sprite):
    def __init__(self,x,y,colour):
        self.size = 7
        super(Shard,self).__init__()
        self.image = pygame.Surface([self.size,self.size])
        self.pt1 = random.randint(0,self.size)
        self.pt2 = random.randint(0,self.size)
        self.image.set_colorkey(BLACK)
        pygame.draw.polygon(self.image,colour,((0,0),(self.size,self.pt1),(self.pt2,self.size)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.velocity = 5
        a=random.randint(0,360)
        self.angle = math.radians(a)

        self.change_x = self.velocity*math.sin(self.angle)
        self.change_y = self.velocity*math.cos(self.angle)

    def update(self):
        self.rect.x += int(nearest(self.change_x))
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        if len(wall_hit_list)>0:
            w = wall_hit_list[0]
            self.change_x = self.change_y = 0

        self.rect.y += int(nearest(self.change_y))
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        if len(wall_hit_list)>0:
            w = wall_hit_list[0]
            self.change_x = self.change_y = 0

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        super(Wall,self).__init__()
        self.image = pygame.Surface([width,height])
        self.image.fill(D_GRAY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
class Bullet(pygame.sprite.Sprite):
    def __init__(self,point,angle,shooter):
        super(Bullet,self).__init__()
        self.image=pygame.Surface([4,4])
        self.image.fill(WHITE)
        self.radius = 2
        pygame.draw.circle(self.image,BLACK,(2,2),self.radius)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = point

        self.velocity = 5
        self.angle = angle
        self.change_x = self.velocity*math.sin(self.angle)
        self.change_y = self.velocity*math.cos(self.angle)

        self.shooter = shooter
        self.life = 0

    def update(self):
        self.rect.x += int(nearest(self.change_x))
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        if len(wall_hit_list)>0:
            w = wall_hit_list[0]
            if self.change_x >0:
                self.rect.right = w.rect.left
            else:
                self.rect.left = w.rect.right
            self.change_x *= -1
            
        self.rect.y += int(nearest(self.change_y))
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        if len(wall_hit_list)>0:
            w = wall_hit_list[0]
            if self.change_y >0:
                self.rect.bottom = w.rect.top

            else:
                self.rect.top = w.rect.bottom

            self.change_y *= -1
        self.life += 1
           
class Tank(pygame.sprite.Sprite):
    #the tank has a line joining the center to a point on the circumference
    #this is just to see where the tank is pointing
    def __init__(self,c1,cen):
        super(Tank,self).__init__()
        self.c1 = c1
        self.c2 = colour_dict[c1]
        self.radius = 20
        self.diameter = 2*self.radius
        self.center = (self.radius,self.radius)
        self.angle = math.radians(random.randint(0,360))
        self.endpoint = ((1+math.sin(self.angle))*self.radius,(1+math.cos(self.angle))*self.radius)
        #endpoint is the point on the circumference connected to the center
        
        self.image = pygame.Surface((self.diameter,self.diameter))
        self.image.fill(WHITE)
        pygame.draw.circle(self.image,self.c1,self.center,self.radius)
        pygame.draw.aaline(self.image,self.c2,self.center,self.endpoint,2)
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = cen

        self.bullets_left = 5

        self.velocity = 0
        self.change_x = 0
        self.change_y = 0
        self.change_angle = 0

    def turn(self,amt):
        self.change_angle += amt

    def changespeed(self,amt):
        self.velocity += amt

    def update(self):
        #updating the angle and making sure its between -2 pi to 2 pi
        self.angle += self.change_angle
        if self.angle>2*math.pi:
            self.angle -= 2*math.pi
        elif self.angle<-2*math.pi:
            self.angle += 2*math.pi

        self.change_x = self.velocity * math.sin(self.angle)
        self.change_y = self.velocity * math.cos(self.angle)
        
        self.rect.x += int(nearest(self.change_x))
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        for w in wall_hit_list:
            if self.change_x >0:
                self.rect.right = w.rect.left
            else:
                self.rect.left = w.rect.right
        self.rect.y += int(nearest(self.change_y))
        wall_hit_list = pygame.sprite.spritecollide(self, wall_list, False)
        for w in wall_hit_list:
            if self.change_y >0:
                self.rect.bottom = w.rect.top
            else:
                self.rect.top = w.rect.bottom
                
        #this is to update the direction the tank points to(the line b/w centre and endpoint)
        self.endpoint = ((1+math.sin(self.angle))*self.radius,(1+math.cos(self.angle))*self.radius)
        self.image = pygame.Surface((self.diameter,self.diameter))
        self.image.fill(WHITE)
        pygame.draw.circle(self.image,self.c1,self.center,self.radius)
        pygame.draw.aaline(self.image,self.c2,self.center,self.endpoint,2)
        self.image.set_colorkey(WHITE)

#---------------------------------------------------------------------------------------------------------------------------------------------------------------------
letters = {pygame.K_a:'a',      
pygame.K_b:'b',      
pygame.K_c:'c',       
pygame.K_d:'d',      
pygame.K_e:'e',       
pygame.K_f:'f',       
pygame.K_g:'g',      
pygame.K_h:'h',       
pygame.K_i:'i',       
pygame.K_j:'j',       
pygame.K_k:'k',       
pygame.K_l:'l',       
pygame.K_m:'m',       
pygame.K_n:'n',       
pygame.K_o:'o',       
pygame.K_p:'p',     
pygame.K_q:'q',       
pygame.K_r:'r',       
pygame.K_s:'s',       
pygame.K_t:'t',       
pygame.K_u:'u',       
pygame.K_v:'v',       
pygame.K_w:'w',       
pygame.K_x:'x',       
pygame.K_y:'y',       
pygame.K_z:'z',
pygame.K_SPACE:' ',
pygame.K_0:'0',
pygame.K_1:'1',
pygame.K_2:'2',
pygame.K_3:'3',
pygame.K_4:'4',
pygame.K_5:'5',
pygame.K_6:'6',
pygame.K_7:'7',
pygame.K_8:'8',
pygame.K_9:'9'}

def display_periphals(score1,score2,name1,name2,colour1,colour2,colour1_,colour2_):
    '''Displays side panel details '''
    text1 = font.render(name1+' : ' + str(score1),True,colour1)
    text2 = font.render(name2+' : ' + str(score2),True,colour2)
    pygame.draw.line(screen,L_GRAY,(800,90),(990,90),50)
    pygame.draw.line(screen,L_GRAY,(800,160),(990,160),50)
    screen.blit(text1,(810,75))
    screen.blit(text2,(810,145))

def remove_last_line():
    '''Deletes last data entry in binary file '''
    stats = readfile()
    stats = stats[:-1]
    scores = open('Scores.dat','wb')
    for i in range(len(stats)):
        
        pickle.dump(stats[i],scores)

def save(name1,name2,score1,score2,colour1,colour2):
    '''Saves game data into a binary file '''
    scores = open('Scores.dat','ab+')
    l = [name1,name2,score1,score2,colour1,colour2]
    pickle.dump(l,scores)
    scores.close()
        
def readfile():
    '''Reads data from binary file '''
    if os.path.isfile('Scores.dat'):
        scores = open('Scores.dat','rb')
        stats = []
        try:
            while True:
                a=pickle.load(scores)
                stats.append(a)
        except EOFError:
            scores.close()
        return stats

def cleardata():
    '''Clears data from binary file '''
    if os.path.isfile('Scores.dat'):
        os.remove('Scores.dat')
        scores = open('Scores.dat','ab+')
        scores.close()
        
colours =[c1,c2,c3,c4,c5,c6,c7,c8]

def isdone(name1,name2,ind1,ind2):
    '''Returns true if all data has been entered, false otherewise'''
    if name1!=name2 and name1 and name2 and ind1!=ind2 and ind1!=None and ind2!=None:
        return True
    return False
def home():
    '''Displays home screen and sub-menus '''
    global done,really_done

    toplefts1 = [(300,350),(340,350),(380,350),(420,350),(460,350),(500,350),(540,350),(580,350)]
    colour_rect_list1 = [pygame.Rect(i[0],i[1],30,30) for i in toplefts1]
    toplefts2 = [(650,350),(690,350),(730,350),(770,350),(810,350),(850,350),(890,350),(930,350)]
    colour_rect_list2 = [pygame.Rect(i[0],i[1],30,30) for i in toplefts2]
    
    end = False
    #Creating surfaces for text
    text3 = font3.render('TANK TROUBLE',True,WHITE)
    text4 = font2.render('INSTRUCTIONS',True,WHITE)
    text5 = font2.render('Tank 1',True,WHITE)
    text6 = font2.render('Name :',True,WHITE)
    text7 = font2.render('Tank 2',True,WHITE)
    text8 = font2.render('Colour:',True,WHITE)

    b1 = font.render('W',True,BLACK)
    b2 = font.render('A',True,BLACK)
    b3 = font.render('S',True,BLACK)
    b4 = font.render('D',True,BLACK)
    b5 = font.render('Q',True,BLACK)
    b6 = font.render('^',True,BLACK)
    b7 = font.render('<',True,BLACK)
    b8 = font.render('>',True,BLACK)
    b9 = font.render('v',True,BLACK)
    b10 = font.render('M',True,BLACK)

    i1 = font4.render('Move Forward',True,WHITE)
    i2 = font4.render('Move Backward',True,WHITE)
    i3 = font4.render('Turn Anticlockwise',True,WHITE)
    i4 = font4.render('Turn Clockwise',True,WHITE)
    i5 = font4.render('Shoot',True,WHITE)
       
    playsurf = font.render(' PLAY ',True,RED)
    instrsurf = font.render(' INSTRUCTIONS',True,RED)
    homesurf = font.render('HOME',True,RED)
    highsurf = font.render('  ALL SCORES',True,RED)
    contsurf = font.render(' CONTINUE GAME',True,RED)
    newsurf = font.render(' NEW GAME',True,RED)
    donesurf = font.render(' DONE',True,RED)
    clearsurf = font.render( 'CLEAR DATA',True,RED)
    
    playrect = playsurf.get_rect(topleft = (460,400))
    instrrect = instrsurf.get_rect(topleft = (400,430))
    homerect = homesurf.get_rect(topleft = (470,500))
    highrect = highsurf.get_rect(topleft = (410,460))
    contrect = contsurf.get_rect(topleft = (390,400))
    newrect = newsurf.get_rect(topleft = (430,430))
    donerect = donesurf.get_rect(topleft = (590,500))
    clearrect = clearsurf.get_rect(topleft = (470,530))

    t1rect = pygame.Rect(300,200,310,100)
    t2rect = pygame.Rect(650,200,310,100)

    heading1 = font.render('Tank 1',True,WHITE)
    heading2 = font.render('Tank 2',True,WHITE)
    name1 = ''
    name2 = ''
    score1 = 0
    score2 = 0
                                 
    mode = 0
    ind1 = None
    ind2 = None
    colour1=None
    colour2=None
    selected = {1:WHITE,2:WHITE}
    empty = len(readfile())==0

    #MODES: 0-HOMESCREEN  1-INSTRUCTIONS  3-HIGHSCORES  4-NEW/OLD GAME  5-NEW GAME 
    while not end:

        mx,my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = True
                really_done  =True
                done = True
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mode == 0:#home
                    if playrect.collidepoint(mx,my):
                        mode = 4
                    elif instrrect.collidepoint(mx,my):
                        mode = 1
                    elif highrect.collidepoint(mx,my):
                        mode = 3
                        info = readfile()
                elif mode == 1:#instructions
                    if homerect.collidepoint(mx,my):
                        mode = 0
                elif mode == 3:#highscores
                    if clearrect.collidepoint(mx,my):
                        cleardata()
                        empty = True
                    elif homerect.collidepoint(mx,my):
                        mode = 0
                elif mode == 4:#new/continue
                    if homerect.collidepoint(mx,my):
                        mode = 0
                    if newrect.collidepoint(mx,my):
                        mode = 5
                    elif contrect.collidepoint(mx,my) and not empty:
                        name1,name2,score1,score2,colour1,colour2 = readfile()[-1]
                        remove_last_line()
                        end = True
                    
                elif mode == 5:#New game
                    if t1rect.collidepoint(mx,my):
                        selected[1] = L_RED
                        selected[2] = WHITE
                    elif t2rect.collidepoint(mx,my):
                        selected[2] = L_RED
                        selected[1] = WHITE
                    elif donerect.collidepoint(mx,my) and isdone(name1,name2,ind1,ind2):
                        end = True
                        pygame.mixer.music.stop()

                    else:
                        selected[1]=WHITE
                        selected[2]=WHITE
                        for i in range(len(colour_rect_list1)):
                            if colour_rect_list1[i].collidepoint(mx,my):
                                ind1 = i
                                colour1 = colours[i]
                        for i in range(len(colour_rect_list2)):
                            if colour_rect_list2[i].collidepoint(mx,my):
                                ind2 = i
                                colour2 = colours[i]
                                
            elif event.type == pygame.KEYDOWN:
                if mode == 5 and event.key in letters:
                    if selected[1] == L_RED and len(name1)<8:
                        name1 += letters[event.key]
                    elif selected[2] == L_RED and len(name2)<8:
                        name2 += letters[event.key]
                elif mode == 5 and event.key == pygame.K_BACKSPACE:
                    if selected[1] == L_RED:
                        name1 = name1[:-1]
                    elif selected[2] == L_RED:
                        name2 = name2[:-1]
                        
        screen.fill(BLACK)
        
        if mode == 0: #homescreen
            screen.blit(wp,(0,0))
            if playrect.collidepoint(mx,my):
                pygame.draw.line(screen,BLACK,(0,415),(1000,415),24)
                pygame.draw.line(screen,WHITE,(0,402),(1000,402),2)
                pygame.draw.line(screen,WHITE,(0,427),(1000,427),2)
            elif instrrect.collidepoint(mx,my):
                pygame.draw.line(screen,BLACK,(0,445),(1000,445),24)
                pygame.draw.line(screen,WHITE,(0,432),(1000,432),2)
                pygame.draw.line(screen,WHITE,(0,457),(1000,457),2)
            elif highrect.collidepoint(mx,my):
                pygame.draw.line(screen,BLACK,(0,475),(1000,475),24)
                pygame.draw.line(screen,WHITE,(0,462),(1000,462),2)
                pygame.draw.line(screen,WHITE,(0,487),(1000,487),2)
  
            screen.blit(text3,(200,100))
            pygame.draw.line(screen,WHITE,(0,90),(1000,90),2)
            pygame.draw.line(screen,WHITE,(0,180),(1000,180),2)
                             
            screen.blit(instrsurf,instrrect)
            screen.blit(playsurf,playrect)
            screen.blit(highsurf,highrect)
            
        elif mode == 1:#instructions
            if homerect.collidepoint(mx,my):
                pygame.draw.line(screen,WHITE,(0,515),(1000,515),2)
            screen.blit(text4,(300,20))
            screen.blit(homesurf,homerect)
            screen.blit(text7,(145,115))
            screen.blit(text5,(720,115))
            button.set_colorkey(WHITE)

            #tank 1
            screen.blit(button,(200,250))
            screen.blit(b1,(212,262)) 
            screen.blit(i1,(158,215))
            
            screen.blit(button,(150,300))
            screen.blit(b2,(165,310))
            screen.blit(i3,(10,260))
            
            screen.blit(button,(200,300))
            screen.blit(b3,(215,310))
            screen.blit(i2,(145,355))
            
            screen.blit(button,(250,300))
            screen.blit(b4,(265,310))
            screen.blit(i4,(255,260))

            screen.blit(button,(200,400))
            screen.blit(b5,(213,410))
            screen.blit(i5,(200,452))

            #tank2
            screen.blit(button,(775,250))
            screen.blit(b6,(793,262))
            screen.blit(i1,(732,215))
            
            screen.blit(button,(725,300))
            screen.blit(b7,(740,310))
            screen.blit(i3,(585,260))
            
            screen.blit(button,(775,300))
            screen.blit(b9,(793,310))
            screen.blit(i2,(720,355))
            
            screen.blit(button,(825,300))
            screen.blit(b8,(840,310))
            screen.blit(i4,(830,260))

            screen.blit(button,(775,400))
            screen.blit(b10,(788,410))
            screen.blit(i5,(775,452))

        elif mode == 3:#all scores
            info = readfile()
            if homerect.collidepoint(mx,my):
                pygame.draw.line(screen,WHITE,(0,515),(1000,515),2)
            elif clearrect.collidepoint(mx,my):
                pygame.draw.line(screen,WHITE,(0,545),(1000,545),2)
            
            screen.blit(font2.render('ALL SCORES:',True,WHITE),(310,25))
            screen.blit(heading1,(100,200))
            screen.blit(heading2,(400,200))
            screen.blit(clearsurf,clearrect)
            screen.blit(homesurf,homerect)
            y=240
            for i in info:
                t1 = font.render(i[0] + ' : ' + str(i[2]),True,WHITE)
                t2 = font.render(i[1] + ' : ' + str(i[3]),True,WHITE)
                screen.blit(t1,(100,y))
                screen.blit(t2,(400,y))
                y+=40
            
        elif mode == 4: #continue/new
            screen.blit(wp,(0,0))
            if homerect.collidepoint(mx,my):
                pygame.draw.line(screen,BLACK,(0,514),(1000,514),24)
                pygame.draw.line(screen,WHITE,(0,503),(1000,503),2)
                pygame.draw.line(screen,WHITE,(0,527),(1000,527),2)
                
            elif contrect.collidepoint(mx,my) and not empty:
                pygame.draw.line(screen,BLACK,(0,414),(1000,414),24)
                pygame.draw.line(screen,WHITE,(0,403),(1000,403),2)
                pygame.draw.line(screen,WHITE,(0,427),(1000,427),2)
            elif newrect.collidepoint(mx,my):
                pygame.draw.line(screen,BLACK,(0,444),(1000,444),24)
                pygame.draw.line(screen,WHITE,(0,433),(1000,433),2)
                pygame.draw.line(screen,WHITE,(0,457),(1000,457),2)
            if not empty: screen.blit(contsurf,contrect)
            screen.blit(newsurf,newrect)
            screen.blit(homesurf,homerect)
            
        elif mode == 5:#new game
            screen.fill((150,150,150))
            screen.blit(text5,(365,100))
            screen.blit(text7,(710,100))
            screen.blit(text6,(50,220))
            screen.blit(text8,(50,325))
            if isdone(name1,name2,ind1,ind2):
                screen.blit(donesurf,donerect)
                if donerect.collidepoint(mx,my):
                    pygame.draw.line(screen,WHITE,(0,515),(1000,515),2)
            pygame.draw.rect(screen,selected[1],t1rect)
            pygame.draw.rect(screen,selected[2],t2rect)

            for i in range(len(colour_rect_list1)):
                pygame.draw.rect(screen,colours[i],colour_rect_list1[i])
            if ind1 != None:
                pygame.draw.rect(screen,D_GRAY,colour_rect_list1[ind1],2)
            for i in range(len(colour_rect_list1)):
                if colour_rect_list1[i].collidepoint(mx,my):
                    pygame.draw.rect(screen,WHITE,colour_rect_list1[i],2)

            for i in range(len(colour_rect_list2)):
                pygame.draw.rect(screen,colours[i],colour_rect_list2[i])
            if ind2 != None:
                pygame.draw.rect(screen,D_GRAY,colour_rect_list2[ind2],2)
            for i in range(len(colour_rect_list2)):
                if colour_rect_list2[i].collidepoint(mx,my):
                    pygame.draw.rect(screen,WHITE,colour_rect_list2[i],2)

                    
            name1text = font.render(name1,True,BLACK)
            name2text = font.render(name2,True,BLACK)
            screen.blit(name1text,(310,220))
            screen.blit(name2text,(660,220))
            
        pygame.display.flip()
        clock.tick(59)

    return name1,name2,score1,score2,colour1,colour2
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------        
h = True

really_done = False
while not really_done:
    pygame.init()
    pygame.display.set_caption("                                                                                                                                                     ||TANK TROUBLE||")
    font = pygame.font.SysFont('TimesNewRoman',28)
    font2 = pygame.font.SysFont('TimesNewRoman',60)
    #font3 = pygame.font.SysFont('TimesNewRoman',80)
    font3 = pygame.font.Font('KITCHENPOLICE.ttf',80)
    font4 = pygame.font.SysFont('TimesNewRoman',24)
    screen = pygame.display.set_mode([1000,600])
    screen.fill(WHITE)
    clock = pygame.time.Clock() 
    wp = pygame.image.load('wp.jpg')
    wp.set_colorkey(BLACK)
    button = pygame.image.load('blank-button2.png')
    explosion = pygame.mixer.Sound('E0.wav')
    music = pygame.mixer.music.load('Music.mp3')

    done = False
    if h ==True:
        pygame.mixer.music.play(-1,0.0)
        name1,name2,score1,score2,colour1,colour2=home()
        colour1_=colour_dict[colour1]
        colour2_=colour_dict[colour2]
        h=False
        pygame.mixer.music.stop()
    grid = [[0 for row in range(17)] for col in range(13)]

    for i in range(13):
        grid[i][0] = 1
        grid[i][16] = 1
    for i in range(17):
        grid[0][i] = 1
        grid[12][i] = 1

    all_sprite_list = pygame.sprite.Group()
    tank_list = pygame.sprite.Group()
    wall_list = pygame.sprite.Group()
    bullet_list = pygame.sprite.Group()
    
    #creating walls
    for i in ([0,0,800,10],[0,10,10,590],[10,590,790,10],[790,10,10,580]):
        wall = Wall(i[0],i[1],i[2],i[3])
        wall_list.add(wall)
        all_sprite_list.add(wall)

    tl1 = []
    i = 0
    while i < 20:
        t1 = random.randint(1,7)*100
        t2 = random.randint(0,5)*100
        if [t1,t2] not in tl1:
            grid[t2/50][t1/50] = 1
            grid[t2/50+1][t1/50] = 1
            grid[t2/50+2][t1/50] = 1
            tl1.append([t1,t2])
            tl1.append([t1,t2+100])
            wall = Wall(t1,t2+10,10,90)
            wall_list.add(wall)
            all_sprite_list.add(wall)
            i += 1    
    tl2 = []
    i = 0
    while i < 20:
        t1 = random.randint(0,7)*100
        t2 = random.randint(1,5)*100
        if [t1,t2] not in tl2:
            grid[t2/50][t1/50] = 1
            grid[t2/50][t1/50+1] = 1
            grid[t2/50][t1/50+2] = 1
            tl2.append([t1,t2])
            tl2.append([t1+100,t2])
            wall = Wall(t1+10,t2,90,10)
            wall_list.add(wall)
            all_sprite_list.add(wall)
            i += 1
    common = []
    for i in tl1 + tl2:
        if i not in common:
            common.append(i)
    for i in common:
        wall = Wall(i[0],i[1],10,10)
        wall_list.add(wall)
        all_sprite_list.add(wall)

    #positioning tanks
    isokay = False
    while not(isokay):
        p1 = random.randint(0,6)*100+50
        p2 = random.randint(0,4)*100+50
        tank1 = Tank(colour1,(p1,p2))
        grid[p2/50][p1/50] = 2
        start = (p2/50,p1/50)
        p3 = random.randint(1,7)*100+50
        p4 = random.randint(1,5)*100+50
        tank2 = Tank(colour2,(p3,p4))
        grid[p4/50][p3/50] = 2
        stop = (p4/50,p3/50)
        isokay = is_connected(grid,start,stop)
        grid[p2/50][p1/50] = 0
        grid[p4/50][p3/50] = 0
    #grid now ready, 0 for blank, 1 for wall and 2 for tank

    all_sprite_list.add(tank1)
    tank_list.add(tank1)
    all_sprite_list.add(tank2)
    tank_list.add(tank2)

    vel_increment = 4
    angle_increment = math.radians(4)
    lag = lag2 = 0

    c1,c2 = 0,0
    clicked = False
    home_num = 0
    homesurf2 = font.render('HOME',True,BLACK)
    homerect2 = homesurf2.get_rect(topleft = (855,500))
    
    while not done:
        if len(tank_list) == 0:
            lag = 0
            lag2+=1
            if lag2>120:
                done = True
        elif lag > 180:
            if tank1 in tank_list:
                score1+=1
            elif tank2 in tank_list:
                score2+=1
            done = True
        if len(tank_list) != 2:
            lag += 1
            if tank2 not in tank_list:
                while c1 < 30:
                    c1 += 1
                    shard = Shard(tank2.rect.x+tank2.radius,tank2.rect.y+tank2.radius,colour2)
                    all_sprite_list.add(shard)
            if tank1 not in tank_list:
                while c2 < 30:
                    c2 += 1
                    shard = Shard(tank1.rect.x+tank1.radius,tank1.rect.y+tank1.radius,colour1)
                    all_sprite_list.add(shard)
                    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                really_done = True
                save(name1,name2,score1,score2,colour1,colour2)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                m_x,m_y = pygame.mouse.get_pos()
                if homerect2.collidepoint(m_x,m_y):
                    clicked = True
                    h = True
                    save(name1,name2,score1,score2,colour1,colour2)
                    
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    tank1.turn(angle_increment)
                elif event.key == pygame.K_RIGHT:
                    tank1.turn(-angle_increment)
                elif event.key == pygame.K_UP:
                    tank1.changespeed(vel_increment)
                elif event.key == pygame.K_DOWN:
                    tank1.changespeed(-vel_increment)
                if event.key == pygame.K_a:
                    tank2.turn(angle_increment)
                elif event.key == pygame.K_d:
                    tank2.turn(-angle_increment)
                elif event.key == pygame.K_w:
                    tank2.changespeed(vel_increment)
                elif event.key == pygame.K_s:
                    tank2.changespeed(-vel_increment)
                
                elif event.key == pygame.K_m:
                    if tank1.bullets_left and tank1 in tank_list:
                        p = math.sin(tank1.angle)*(tank1.radius+4) + tank1.rect.center[0]
                        q =math.cos(tank1.angle)*(tank1.radius+4) + tank1.rect.center[1]
                        b = Bullet((p,q),tank1.angle,1)
                        if pygame.sprite.spritecollide(b,wall_list,False):
                            del b
                            tank_list.remove(tank1)
                            all_sprite_list.remove(tank1)
                            explosion.play()
                        else:
                            bullet_list.add(b)
                            all_sprite_list.add(b)
                            tank1.bullets_left -= 1
                    
                elif event.key == pygame.K_q:
                    if tank2.bullets_left and tank2 in tank_list:
                        p = math.sin(tank2.angle)*(tank2.radius+4) + tank2.rect.center[0]
                        q =math.cos(tank2.angle)*(tank2.radius+4) + tank2.rect.center[1]
                        b = Bullet((p,q),tank2.angle,2)
                        if pygame.sprite.spritecollide(b,wall_list,False):
                            del b
                            tank_list.remove(tank2)
                            all_sprite_list.remove(tank2)
                            explosion.play()
                        else:
                            bullet_list.add(b)
                            all_sprite_list.add(b)
                            tank2.bullets_left -= 1
                    
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    tank1.turn(-angle_increment)
                elif event.key == pygame.K_RIGHT:
                    tank1.turn(angle_increment)
                elif event.key == pygame.K_UP:
                    tank1.changespeed(-vel_increment)
                elif event.key == pygame.K_DOWN:
                    tank1.changespeed(vel_increment)
                if event.key == pygame.K_a:
                    tank2.turn(-angle_increment)
                elif event.key == pygame.K_d:
                    tank2.turn(angle_increment)
                elif event.key == pygame.K_w:
                    tank2.changespeed(-vel_increment)
                elif event.key == pygame.K_s:
                    tank2.changespeed(vel_increment)
        
        screen.fill(L_GRAY)
        all_sprite_list.update()
         
        if len(bullet_list) != 0:
            for b in bullet_list:
                if b.life>300:
                    if b.shooter == 1:
                        tank1.bullets_left += 1
                    else:
                        tank2.bullets_left += 1
                    bullet_list.remove(b)
                    all_sprite_list.remove(b)

        d = pygame.sprite.groupcollide(tank_list,bullet_list,True,True,callback)
        if len(d)>=1:
            explosion.play()
        all_sprite_list.draw(screen)
        pygame.draw.rect(screen,D_GRAY,(800,0,200,600))
        if not clicked:
            mx,my = pygame.mouse.get_pos()
            if homerect2.collidepoint(mx,my):
                pygame.draw.line(screen,WHITE,(790,515),(1000,515),2)
            screen.blit(homesurf2,homerect2)
            
        elif clicked:
            home_num +=1
            home_num %= 80
            if 20<home_num<=40:
                pygame.draw.circle(screen,RED,(885,510),4)
            elif 40<home_num<=60:
                pygame.draw.circle(screen,RED,(885,510),4)
                pygame.draw.circle(screen,RED,(895,510),4)
            elif 60<home_num<=80:
                pygame.draw.circle(screen,RED,(885,510),4)
                pygame.draw.circle(screen,RED,(895,510),4)
                pygame.draw.circle(screen,RED,(905,510),4)
                
        display_periphals(score1,score2,name1,name2,colour1,colour2,colour1_,colour2_)
        pygame.display.flip()
        clock.tick(59)
     
    pygame.display.quit()
pygame.quit()
