# -*- coding: utf-8 -*-
import pygame
import json
class Color:
    black = (0, 0, 0)
    white = (255, 255, 255)
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    yellow = (255, 255, 0)
    def __init__(self, r, g, b):
        self.rgb = (r, g, b)
class Sokoban():
    """倉庫番"""
    InitMode = 0
    PlayingMode = 1
    RecodeMode = 2
    CopyCatMode = 3
    DevelopMode = 4
    AroundOffset = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    def __init__(self, level = 0):
        pygame.init()
        pygame.display.set_caption('倉庫番')
        pygame.mixer.music.load("musics/0.mp3") # 背景音樂
        pygame.mixer.music.play(-1, 0.0) # 重複播放
        self.gameDisplay = pygame.display.set_mode((420, 420))
        self.clock = pygame.time.Clock()
        self.fonts = [
            pygame.font.Font("fonts/1.ttc", 30),
            pygame.font.Font("fonts/0.ttc", 30),
            pygame.font.Font("fonts/0.ttc", 14),
            pygame.font.Font("fonts/0.ttc", 12)
        ]
        self.colors = [
            Color(231, 219, 195),
            Color(96, 68, 57)
        ]
        self.image = None # 主題圖片
        self.theme = 0 # 主題代號
        self.username = "" # 使用者名稱
        self.mode = Sokoban.InitMode # 遊戲模式
        self.level = level # 關卡等級
        self.stage = None # 關卡地圖
        self.size = (0, 0)
        self.display_width = self.size[0] * 30
        self.display_height = self.size[1] * 30
        self.steps = [] # 移動步驟
        self.rank = None
        self.breakOff = False # 成功破關
        self.position = (0, 0) # 主角位置
        self.recode = None # 高分紀錄
        self.startTime = 0 # 遊戲開始時間
        self.copycatTimer = 0
        self.copycatCycleTime = 500
        self.blinkCycleTime = (300, 800) # 300 / 800
        self.running = True # 遊戲進行中
        self.developPassword = "dev" # 進入開發模式密碼(雞肋功能)
        self.password = "" # 目前輸入密碼
        self.path = [] # 滑鼠點擊最短路徑
        self.lurd = "" # 移動文字記錄
        self.copycatName = "" # 紀錄持有人
        self.confirm = {
            "message" : "是否重新開始？",
            "options" : [
                {
                    "text": "是",
                    "callback" : self.loadStage
                },
                {
                    "text": "否",
                    "callback" : None
                }
            ],
            "select" : 0,
            "show" : False
        }
        self.loadTheme()
        self.loadRecode()
        self.loadStage()
        while self.running:
            self.hander()
            self.draw()
        self.quit()
    def addRecode(self):
        for rank in range(len(self.recode[self.level]) - 1, self.rank, -1):
            self.recode[self.level][rank] = self.recode[self.level][rank - 1]
        self.recode[self.level][self.rank] = {
            "lurd": self.lurd,
            "name" : self.username,
            "move" : len(self.steps)
        }
        with open('data.json', 'w') as output_file:
            json.dump(self.recode, output_file, sort_keys = True, indent = 4, ensure_ascii = False)
    def loadRecode(self):
        with open('data.json') as json_data:
            self.recode = json.load(json_data)
    def loadStage(self):
        with open('sokoban.json') as json_data:
            stage_data = json.load(json_data)
            if len(stage_data) <= self.level:
                self.level = 0
            elif self.level  < 0:
                self.level = len(stage_data) - 1
            stage_data = stage_data[self.level]
            self.stage = stage_data["map"]
            self.size = stage_data["size"]
            self.display_width = self.size[0] * 30
            self.display_height = self.size[1] * 30
        self.steps = []
        self.rank = None
        self.breakOff = False
        self.lurd = ""
        self.path = []
        for y, Raw in enumerate(self.stage):
            for x, Cell in enumerate(Raw):
                if Cell in range(5, 7):
                    self.position = (x, y)
        self.startTime = pygame.time.get_ticks()
    def loadTheme(self):
        self.image = pygame.image.load("images/" + str(self.theme) + ".png")
    def previous(self):
        if len(self.steps) > 0:
            if self.mode == Sokoban.PlayingMode:
                self.lurd = self.lurd[:-1]
                # 假如要記錄復原，這裡就要改
            self.path = []
            step = self.steps.pop()
            self.position = step["position"]
            self.stage[self.position[1]][self.position[0]] += 5
            for x, y, offset in step["change"]:
                self.stage[self.position[1] + y][self.position[0] + x] -= offset
    def next(self, ticks): # CopyCatMode
        if len(self.steps) < len(self.lurd):
            self.copycatTimer = ticks
            x, y = Sokoban.AroundOffset[["u", "d", "l", "r"].index(self.lurd[len(self.steps)].lower())]
            self.move(x, y)
    def draw(self):
        ticks = pygame.time.get_ticks()
        if self.mode == Sokoban.InitMode:
            if pygame.display.get_surface().get_size() != (420, 400):
                self.gameDisplay = pygame.display.set_mode((420, 400))
            self.gameDisplay.fill(self.colors[0].rgb)
            # self.gameDisplay.blit(pygame.image.load("images/background.png"), (0, 0))
            # background.png
            self.gameDisplay.blit(self.fonts[1].render("倉庫番 Sokoban", 1, self.colors[1].rgb), (110, 0))
            self.gameDisplay.blit(self.fonts[2].render("請輸入名字：%s" % (self.username), 1, self.colors[1].rgb), (10, 50))
            self.gameDisplay.blit(self.fonts[3].render("（請輸入20字以內，由英數組成的名字）", 1, Color.red), (0, 64))
            self.gameDisplay.blit(self.fonts[2].render("向上移動：↑ / W" , 1, self.colors[1].rgb), (10, 100))
            self.gameDisplay.blit(self.fonts[2].render("向下移動：↓ / S" , 1, self.colors[1].rgb), (10, 120))
            self.gameDisplay.blit(self.fonts[2].render("向左移動：← / A" , 1, self.colors[1].rgb), (10, 140))
            self.gameDisplay.blit(self.fonts[2].render("向右移動：→ / D" , 1, self.colors[1].rgb), (10, 160))
            self.gameDisplay.blit(self.fonts[2].render("重新開始：F2" , 1, self.colors[1].rgb), (10, 180))
            self.gameDisplay.blit(self.fonts[2].render("上一步：F3" , 1, self.colors[1].rgb), (10, 200))
            self.gameDisplay.blit(self.fonts[2].render("榮譽榜：F4" , 1, self.colors[1].rgb), (10, 220))
            self.gameDisplay.blit(self.fonts[2].render("確認：Enter" , 1, self.colors[1].rgb), (10, 240))
            self.gameDisplay.blit(self.fonts[2].render("取消：Esc" , 1, self.colors[1].rgb), (10, 260))
            self.gameDisplay.blit(self.fonts[2].render("（點擊榮譽榜可看紀錄）" , 1, self.colors[1].rgb), (10, 280))
            # self.gameDisplay.blit(self.fonts[2].render("主題：《 %d 》" % (self.theme) , 1, self.colors[1].rgb), (10, 280))
            if ticks % self.blinkCycleTime[1] > self.blinkCycleTime[0]:
                self.gameDisplay.blit(self.fonts[2].render("歡迎來到倉庫番的世界!!" , 1, self.colors[1].rgb), (120, 380))

        elif self.mode in [Sokoban.PlayingMode, Sokoban.CopyCatMode]:
            if ticks - self.copycatTimer > self.copycatCycleTime:
                self.next(ticks)
            windowSize = pygame.display.get_surface().get_size()
            if windowSize != (self.display_width, self.display_height + (30 if self.mode == Sokoban.CopyCatMode else 0)):
                self.gameDisplay = pygame.display.set_mode((self.display_width, self.display_height + (30 if self.mode == Sokoban.CopyCatMode else 0)))
                windowSize = pygame.display.get_surface().get_size()
            self.gameDisplay.fill(self.colors[0].rgb)

            for y, Raw in enumerate(self.stage):
                for x, Cell in enumerate(Raw):
                    self.gameDisplay.blit(self.image.subsurface((Cell if Cell < 6 else 5) * 30, 0, 30, 30), (x * 30, y * 30))
                    # self.gameDisplay.blit(self.fonts[0].render(str(Cell), 1, self.colors[1].rgb), (x * 30, y * 30))
            if len(self.steps) == 0:

                self.startTime = ticks
            level = "level: %d" % (self.level + 1)
            best = "best: " + str(self.recode[self.level][0]["move"] if type(self.recode[self.level][0]["move"]) is int else "X")
            step = "step: %d / %d" % (len(self.steps), len(self.lurd)) if self.mode == Sokoban.CopyCatMode else "step: %d" % (len(self.steps))
            second = (ticks - self.startTime) // 1000
            time = ""
            if second < 60:
                time = "time: %d" % (second)
            elif second < 3600:
                minute = second // 60
                second = second % 60
                time = "time: %d:%02d" % (minute, second)
            else: # second < 86400:
                hour = second // 3600
                minute = second // 60 % 60
                second = second % 60
                time = "time: %d:%02d:%02d" % (hour, minute, second)
            self.gameDisplay.blit(self.fonts[3].render(level + " " + best, 1, self.colors[1].rgb), (0, 0))
            self.gameDisplay.blit(self.fonts[3].render(step, 1, self.colors[1].rgb), (0, 10))
            self.gameDisplay.blit(self.fonts[3].render(time, 1, self.colors[1].rgb), (0, 20))
            if self.mode == Sokoban.CopyCatMode:
                self.gameDisplay.blit(self.fonts[2].render("name: %s" % (self.copycatName) , 1, self.colors[1].rgb), (0, windowSize[1] - 20))
            if len(self.path) > 0:
                x, y = self.position
                pathColor = Color.blue if self.stage[y + self.path[0][1]][x + self.path[0][0]] in range(2) else Color.green
                for step, offset in enumerate(self.path):
                    pygame.draw.circle(self.gameDisplay, pathColor, ((x + offset[0]) * 30 + 15 - 10 * offset[0], (y + offset[1]) * 30 + 15 - 10 * offset[1]), 3, 0)
                    pygame.draw.circle(self.gameDisplay, pathColor, ((x + offset[0]) * 30 + 15, (y + offset[1]) * 30 + 15), 5 if len(self.path) - 1 == step else 4, 0)
                    if len(self.path) - 1 > step:
                        pygame.draw.circle(self.gameDisplay, pathColor, ((x + offset[0]) * 30 + 15 + 10 * self.path[step + 1][0], (y + offset[1]) * 30 + 15 + 10 * self.path[step + 1][1]), 3, 0)
                    x += offset[0]
                    y += offset[1]
            if self.confirm["show"]:
                pygame.draw.rect(self.gameDisplay, (255, 255, 255), (10, 100, windowSize[0] - 20, 60))
                self.gameDisplay.blit(self.fonts[2].render(self.confirm["message"], 1, self.colors[1].rgb), (20, 110))
                text = " ".join([("●" if index == self.confirm["select"] else "○") + option["text"] for index, option in enumerate(self.confirm["options"])])
                self.gameDisplay.blit(self.fonts[2].render(text, 1, self.colors[1].rgb), (20, 130))

        elif self.mode == Sokoban.RecodeMode:
            windowSize = pygame.display.get_surface().get_size()
            if windowSize != (380, 420):
                self.gameDisplay = pygame.display.set_mode((380, 420))
                windowSize = pygame.display.get_surface().get_size()
            self.gameDisplay.fill(self.colors[0].rgb)
            self.gameDisplay.blit(self.fonts[1].render("第%d關 榮譽榜" % (self.level + 1), 1, self.colors[1].rgb), (190 - 80, 0))
            row = (pygame.mouse.get_pos()[1] - 60) // 30
            if not self.rank is None:
                pygame.draw.rect(self.gameDisplay, (150, 255, 150), (0, 30 * self.rank + 60, windowSize[0], 30))
            for rank, recode in enumerate(self.recode[self.level]):
                name = recode["name"] if type(recode["move"]) is int else "Nope"
                move = str(recode["move"] if type(recode["move"]) is int else "X")
                self.gameDisplay.blit(self.fonts[1].render("%2d." % (rank + 1,), 1, self.colors[1].rgb), (0, 30 * rank + 60))
                self.fonts[1].set_underline(row == rank and type(recode["move"]) is int)
                self.gameDisplay.blit(self.fonts[1].render(name, 1, self.colors[1].rgb), (50, 30 * rank + 60))
                self.gameDisplay.blit(self.fonts[1].render(move, 1, self.colors[1].rgb), (380 - 20 * len(move), 30 * rank + 60))
                self.fonts[1].set_underline(False)
            if ticks % self.blinkCycleTime[1] > self.blinkCycleTime[0]:
                self.gameDisplay.blit(self.fonts[2].render("按Enter%s..." % ("進入下一關" if self.breakOff else "開始挑戰"), 1, self.colors[1].rgb), (190 - 80, 400))
        elif self.mode == Sokoban.DevelopMode:
            if pygame.display.get_surface().get_size() != (380, 420):
                self.gameDisplay = pygame.display.set_mode((380, 420))
            self.gameDisplay.fill(Color.white)
        fps = "fps: %d" % (self.clock.get_fps())
        self.gameDisplay.blit(self.fonts[3].render(fps, 1, self.colors[1].rgb), (pygame.display.get_surface().get_size()[0] - len(fps) * 7, 0))
        pygame.display.set_caption('倉庫番 第%d關' % (self.level + 1))
        pygame.display.update()
        self.clock.tick(30)
    def hander(self):
        events = pygame.event.get()
        mouse_position = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F4 and bool(event.mod & pygame.KMOD_ALT) or event.type == pygame.QUIT:
                self.running = False
            elif self.confirm["show"]:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        if not self.confirm["options"][self.confirm["select"]]["callback"] is None:
                            self.confirm["options"][self.confirm["select"]]["callback"]()
                        self.confirm["show"] = False
                    elif event.key == pygame.K_ESCAPE:
                        self.confirm["show"] = False
                    elif event.key == pygame.K_LEFT:
                        self.confirm["select"] = (self.confirm["select"] - 1 + len(self.confirm["options"])) % len(self.confirm["options"])
                    elif event.key == pygame.K_RIGHT:
                        self.confirm["select"] = (self.confirm["select"] + 1) % len(self.confirm["options"])
            elif self.mode == Sokoban.InitMode:
                if event.type == pygame.KEYDOWN:
                    # if event.key == pygame.K_LEFT:
                    #     self.theme = self.theme - 1
                    #     self.loadTheme()
                    # elif event.key == pygame.K_RIGHT:
                    #     self.theme = self.theme + 1
                    #     self.loadTheme()
                    # elif event.key == pygame.K_BACKSPACE:
                    if event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        self.username = ""
                    elif (event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]) and self.username != "":
                        self.mode = Sokoban.PlayingMode
                    else:
                        if len(self.username) <= 20:
                            if event.key in range(48, 58): # 0~9
                                self.username += chr(event.key)
                            elif event.key == ord(" ") and len(self.username) > 0:
                                self.username += chr(event.key)
                            elif event.key in range(ord('a'), ord('z') + 1) or event.key in range(ord('A'), ord('Z') + 1): # a~z A~Z
                                if pygame.key.get_mods() & pygame.KMOD_CAPS:
                                    self.username += chr(event.key - ord('a') + ord('A'))
                                else:
                                    self.username += chr(event.key)
                            elif event.key in range(256, 266): # 0~9
                                self.username += chr(event.key - 208)
                            # else:
                            #     print(event.key)
            elif self.mode == Sokoban.PlayingMode:
                x, y = mouse_position[0] // 30, mouse_position[1] // 30
                if y in range(self.size[1]):
                    if x in range(self.size[0]):
                        if self.stage[y][x] in range(2):
                            cellCount = self.size[0] * self.size[1]
                            distance = [[cellCount if cell in range(2) else -1 for cell in row] for row in self.stage]
                            distance[self.position[1]][self.position[0]] = 0
                            for i in range(1, cellCount):
                                if True in [i - 1 in row for row in distance]:
                                    for y2, row in enumerate(distance):
                                        for x2, cell in enumerate(row):
                                            if cell == i - 1:
                                                for offset in Sokoban.AroundOffset:
                                                    if y2 + offset[1] in range(self.size[1]):
                                                        if x2 + offset[0] in range(self.size[0]):
                                                            if distance[y2 + offset[1]][x2 + offset[0]] > i:
                                                                distance[y2 + offset[1]][x2 + offset[0]] = i
                                else:
                                    break

                            for y2, row in enumerate(distance):
                                for x2, cell in enumerate(row):
                                    if cell == cellCount:
                                        distance[y2][x2] = -1
                            if distance[y][x] > 0:
                                self.path = []
                                # print("兩點距離%d步" % (distance[y][x]))
                                for i in range(distance[y][x], 0, -1):
                                    for offset in Sokoban.AroundOffset:
                                        if y + offset[1] in range(self.size[1]):
                                            if x + offset[0] in range(self.size[0]):
                                                if distance[y + offset[1]][x + offset[0]] == i - 1:
                                                    self.path = [(-offset[0], -offset[1])] + self.path
                                                    x = x + offset[0]
                                                    y = y + offset[1]
                                                    break
                            else:
                                self.path = []
                        elif self.stage[y][x] in range(3, 5):
                            if pow(x - self.position[0], 2) + pow(y - self.position[1], 2) == 1:
                                self.path = [(x - self.position[0], y - self.position[1])]
                            else:
                                self.path = []
                        else:
                            self.path = []
                        if pygame.mouse.get_pressed()[0]:
                            for xOffset, yOffset in self.path:
                                self.move(xOffset, yOffset)
                            self.path = []
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.path = []
                        self.move(-1, 0)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.path = []
                        self.move(1, 0)
                    elif event.key in [pygame.K_UP, pygame.K_w]:
                        self.path = []
                        self.move(0, -1)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.path = []
                        self.move(0, 1)
                    elif event.key == pygame.K_F2:
                        self.confirm = {
                            "message" : "是否重新開始？",
                            "options" : [
                                {
                                    "text": "是",
                                    "callback" : self.loadStage
                                },
                                {
                                    "text": "否",
                                    "callback" : None
                                }
                            ],
                            "select" : 0,
                            "show" : len(self.steps) > 0
                        }
                    elif event.key == pygame.K_F3:
                        self.previous()
                    if event.key in range(48, 58): # 0~9
                        self.password += chr(event.key)
                    elif event.key == ord(" "):
                        self.password += chr(event.key)
                    elif event.key in range(ord('a'), ord('z') + 1) or event.key in range(ord('A'), ord('Z') + 1): # A~Za~z
                        self.password += chr(event.key)
                    elif event.key in range(256, 266): # 0~9
                        self.password += chr(event.key - 208)
                    if self.developPassword in self.password:
                        self.mode = Sokoban.DevelopMode
                        self.password = ""

                    elif event.key == pygame.K_F4:
                        self.mode = Sokoban.RecodeMode
                    # elif event.key == pygame.K_F5:
                    #     self.level += 1
                    #     self.loadStage()
            elif self.mode == Sokoban.RecodeMode:
                if pygame.mouse.get_pressed()[0]:
                    row = (mouse_position[1] - 60) // 30
                    if row in range(len(self.recode[self.level])):
                        recode = self.recode[self.level][row]
                        if type(recode["move"]) is int:
                            self.loadStage()
                            self.mode = Sokoban.CopyCatMode
                            self.lurd = recode["lurd"]
                            self.copycatName = recode["name"]
                            self.copycatTimer = pygame.time.get_ticks()
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                        if self.breakOff:
                            self.level += 1
                            self.loadStage()
                        self.mode = Sokoban.PlayingMode
                    elif event.key == pygame.K_F2:
                        self.loadStage()
                        self.mode = Sokoban.PlayingMode
            elif self.mode == Sokoban.CopyCatMode:
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.previous()
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.next(pygame.time.get_ticks())
            elif self.mode == Sokoban.DevelopMode:
                if event.type == pygame.KEYDOWN:
                    if event.key in range(48, 58): # 0~9
                        self.password += chr(event.key)
                    elif event.key == ord(" "):
                        self.password += chr(event.key)
                    elif event.key in range(ord('a'), ord('z') + 1) or event.key in range(ord('A'), ord('Z') + 1): # A~Za~z
                        self.password += chr(event.key)
                    elif event.key in range(256, 266): # 0~9
                        self.password += chr(event.key - 208)
                    if self.developPassword in self.password:
                        self.mode = Sokoban.PlayingMode
                        self.password = ""

    def move(self, x, y):
        if self.position[1] + y in range(len(self.stage)):
            if self.position[0] + x in range(len(self.stage[0])):
                if self.stage[self.position[1] + y][self.position[0] + x] in range(0, 2):
                    print("向(%d, %d)移動" % (x, y))
                    if self.mode == Sokoban.PlayingMode:
                        self.lurd += ["u", "d", "l", "r"][Sokoban.AroundOffset.index((x, y))]
                    self.steps.append(
                        {
                            "change" : [[x, y, 5]],
                            "position" : self.position[:]
                        }
                    )
                    self.stage[self.position[1]][self.position[0]] -= 5
                    self.stage[self.position[1] + y][self.position[0] + x] += 5
                    self.position = (self.position[0] + x, self.position[1] + y)
                elif self.stage[self.position[1] + y][self.position[0] + x] in range(3, 5):
                    if self.position[1] + 2 * y in range(len(self.stage)):
                        if self.position[0] + 2 * x in range(len(self.stage[0])):
                            if self.stage[self.position[1] + 2 * y][self.position[0] + 2 * x] in range(0, 2):
                                print("向(%d, %d)推動" % (x, y))
                                if self.mode == Sokoban.PlayingMode:
                                    self.lurd += ["U", "D", "L", "R"][Sokoban.AroundOffset.index((x, y))]
                                self.steps.append(
                                    {
                                        "change" : [[x, y, 2], [x * 2, y * 2, 3]],
                                        "position" : self.position[:]
                                    }
                                )
                                self.stage[self.position[1]][self.position[0]] -= 5
                                self.stage[self.position[1] + y][self.position[0] + x] += 2
                                self.stage[self.position[1] + 2 * y][self.position[0] + 2 * x] += 3
                                self.position = (self.position[0] + x, self.position[1] + y)
        if not True in [3 in y for y in self.stage]: # win!!
            if self.mode == Sokoban.PlayingMode:
                self.breakOff = True
                for rank, recode in enumerate(self.recode[self.level]):
                    if type(recode["move"]) is int:
                        if recode["move"] > len(self.steps):
                            self.rank = rank
                            self.addRecode()
                            break
                    else:
                        self.rank = rank
                        self.addRecode()
                        break
            else:
                self.loadStage()
            self.mode = Sokoban.RecodeMode
    def quit(self):
        pygame.quit()
        quit()
# [
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 2, 0, 0, 0, 0],
#     [0, 0, 0, 0, 2, 2, 2, 3, 3, 0, 0, 2, 2, 0, 0, 0],
#     [0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2, 2, 0, 0],
#     [0, 0, 0, 0, 2, 0, 3, 0, 0, 0, 2, 0, 0, 2, 2, 0],
#     [0, 2, 2, 2, 2, 2, 2, 0, 2, 0, 2, 2, 0, 0, 2, 0],
#     [0, 2, 1, 1, 0, 0, 2, 0, 3, 0, 3, 0, 0, 0, 2, 0],
#     [0, 2, 1, 1, 0, 0, 3, 0, 0, 0, 2, 2, 2, 2, 2, 0],
#     [0, 2, 6, 1, 0, 0, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0],
#     [0, 2, 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
# ]
# code(XSB) :
# 0(-) : 空位 (floor)
# 1(.) : 目標點 (goal)
# 2(#) : 圍牆 (wall)
# 3($) : 箱子 (box)
# 4(*) : 箱子在目標點 (box on goal)
# 5(@) : 人 (man)
# 6(+) : 人在目標點 (man on goal)
# lurd
# L: 左
# U: 上
# R: 右
# D: 下
# (已中止)!: 復原

if __name__ == '__main__':
    Sokoban()