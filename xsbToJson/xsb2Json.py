import json
import re
import os
chart = [
    " ",
    ".",
    "#",
    "$",
    "*",
    "@",
    "+"
]
stages = []
# code(XSB) :
# 0(-) : 空位 (floor)
# 1(.) : 目標點 (goal)
# 2(#) : 圍牆 (wall)
# 3($) : 箱子 (box)
# 4(*) : 箱子在目標點 (box on goal)
# 5(@) : 人 (man)
# 6(+) : 人在目標點 (man on goal)
import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
# options = {
#     'title': ,
#     '': os.getcwd()
# }
xsbDirectory = filedialog.askdirectory(title = "選擇xsb檔所在資料夾", initialdir = os.getcwd())
jsonDirectory = os.getcwd()
if xsbDirectory:
    filenames = [filename for filename in os.listdir(xsbDirectory) if filename.endswith('.xsb')]
    fileCount = len(filenames)
    fileCountLen = len(str(fileCount))
    diagonalOffset = [
        (-1, -1),
        (1, -1),
        (-1, 1),
        (1, 1)
    ]
    aroundOffset = [
        (0, -1),
        (0, 1),
        (-1, 0),
        (1, 0)
    ]
    for index, filename in enumerate(filenames):
        if filename.endswith('.xsb'):
            print(f"\r[ {index + 1:0{fileCountLen}}/{fileCount} ] {filename}", end = "")
            stage = [[]]
            end = False
            with open(os.path.join(xsbDirectory, filename), 'r', encoding='UTF-8') as file:
                # width = 0
                for lineIndex, line in enumerate(file):
                    for char in line:
                        if (not end) and char in chart:
                            n = chart.index(char)
                            stage[-1].append(n)
                        elif char == '\n':
                            if stage[-1] != []:
                                stage[-1] += [stage[-1][-1] for i in range(len(stage[0]) - len(stage[-1]))]
                                if len(stage[-1]) > len(stage[0]):
                                    print(f"\rfile: {filename}:{lineIndex} error: check every line length!!")
                                    stage[-1] = stage[-1][:len(stage[0])] # 假設多的是誤植
                                stage.append([])
                        else:
                            end = True
            if stage[-1] == []:
                stage.pop()

            # 圍牆美化
            tempStage =  list(stage)
            for y, raw in enumerate(stage):
                for x, cell in enumerate(raw):
                    if cell == 2:
                        wall = False
                        for offsetX, offsetY in diagonalOffset + aroundOffset:
                            if (x + offsetX) in range(len(raw)) and (y + offsetY) in range(len(tempStage)):
                                if tempStage[y + offsetY][x + offsetX] != 2:
                                    wall = True
                        stage[y] = stage[y][:x] + [2 if wall else 0] + stage[y][x + 1:]
                stage[y] = [0] + stage[y] + [0]
            stage = [[0] * len(stage[0])] + stage + [[0] * len(stage[0])]
            del(tempStage)

            found = False
            while not found: # 去頭(重複)
                if stage[0] == stage[1]:
                    stage.pop(0)
                else:
                    found = True
            found = False
            while not found: # 去尾(重複)
                if stage[-1] == stage[-2]:
                    stage.pop(-1)
                else:
                    found = True
            found = False
            while not found: # 去頭(重複)
                if [raw[0] for raw in stage] == [raw[1] for raw in stage]:
                    for raw in stage:
                        raw.pop(0)
                else:
                    found = True
            found = False
            while not found: # 去尾(重複)
                if [raw[-1] for raw in stage] == [raw[-2] for raw in stage]:
                    for raw in stage:
                        raw.pop(-1)
                else:
                    found = True
            found = False

            stages.append(
                {
                    "map" : [json.dumps(raw) for raw in stage],
                    "size" : json.dumps(
                        [
                            len(stage[0]),
                            len(stage)
                        ]
                    )
                }
            )
            # print()
    with open(os.path.join(jsonDirectory, "output.json"), 'w', encoding='UTF-8') as file:
        file.writelines(
            re.sub(
                r'(?!\w)(]*)\"(\[*)(?![\w:])',
                r"\g<1>\g<2>",
                json.dumps(
                    stages,
                    indent = 4,
                    ensure_ascii = False
                )
            )
        )


# self.myMovie = pygame.movie.Movie(self.fullfilename)   #Load video file
# self.resolution = self.myMovie.get_size()              #Get it's dimensions
# self.movie_length = self.myMovie.get_length()          #Get it's play length
# self.image_surface = pygame.Surface(self.resolution)   #Create surface for the video
# self.image_surface.fill([0,0,0])                       #Fill surface black
# self.myMovie.set_display(self.image_surface)           #Assign video stream to the surface
# self.myMovie.play()                                    #Start video stream
# self.start_time = time.time()                          #Get time the stream was started