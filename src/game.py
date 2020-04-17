#!/usr/bin/env python3
# coding: utf8
import os, enum, random, pyxel
from abc import ABCMeta, abstractmethod

class App:
    def __init__(self):
        self.__window = Window()
        globals()['Window'] = self.__window
        self.__scene = SceneManager()
        pyxel.run(self.update, self.draw)
    def update(self):
        self.__scene.update()
    def draw(self):
        self.__scene.draw()

class Window:
    def __init__(self):
        pyxel.init(self.Width, self.Height, border_width=self.BorderWidth, caption=self.Caption, fps=60)
    @property
    def Width(self): return 64
    @property
    def Height(self): return 96
    @property
    def Caption(self): return "Ping Pong"
    @property
    def BorderWidth(self): return 0
    def update(self): pass
    def draw(self): pyxel.cls(0)

class SceneType(enum.IntEnum):
    Start = 0
    Play  = 1
    Score = 2

class SceneManager:
    def __init__(self):
        self.__scenes = [StartScene(), PlayScene(), ScoreScene()]
        self.__now = SceneType.Start
    def init(self, *args, **kwargs):
        pass
    def update(self):
        next_scene = self.__scenes[self.__now].update()
        if isinstance(next_scene, SceneType):
            self.__now = next_scene
            self.__scenes[self.__now].init()
        elif isinstance(next_scene, tuple) and isinstance(next_scene[0], SceneType):
            self.__now = next_scene[0]
            if   2 <= len(next_scene): self.__scenes[self.__now].init(*next_scene[1])
            elif 3 <= len(next_scene): self.__scenes[self.__now].init(*next_scene[1], **next_scene[2])
            else:                      self.__scenes[self.__now].init()
    def draw(self):
        self.__scenes[self.__now].draw()

class Scene(metaclass=ABCMeta):
    @abstractmethod
    def init(self, *args, **kwargs): pass
    @abstractmethod
    def update(self): pass
    @abstractmethod
    def draw(self): pass

class StartScene(Scene):
    def __init__(self):
        self.__pc = PC()
    def init(self, *args, **kwargs): pass
    def update(self):
        if pyxel.btn(pyxel.KEY_SPACE):
            return SceneType.Play
    def draw(self):
        self.__pc.draw()
        pyxel.text(Window.Width // 2 - (4*16/2), Window.Height // 2 - (8*2), 'Push SPACE key !', 7)

class BestScore:
    def __init__(self):
        self.__file_name = 'BEST'
        self.__file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), self.__file_name)
        self.__load()
    @property
    def Score(self): return self.__score
    @Score.setter
    def Score(self, value):
        if self.__score < value:
            self.__score = value
            self.__save()
    def __load(self):
        if os.path.isfile(self.__file_path):
            with open(self.__file_path, 'r') as f:
                self.__score = int(f.read())
        else: self.__score = 0
    def __save(self):
        with open(self.__file_path, 'w') as f:
            f.write(str(self.__score))

class ScoreScene(Scene):
    def __init__(self):
        self.__best = BestScore()
        self.__pc = PC()
        self.__now = 0
    def init(self, *args, **kwargs):
        self.__now = args[0]
        self.__best.Score = self.__now
    def update(self):
        if pyxel.btn(pyxel.KEY_R):
            return SceneType.Play
    def draw(self):
        x = Window.Width // 2 - (4*16/2) + 2
        y = Window.Height // 2 - (8/2) - (8 * 4 / 2)
        pyxel.rect(x,         y,   Window.Width, 8 * 4 + 2, 4)
        pyxel.text(x+2,       y+2,   'SCORE', 7)
        pyxel.text(x+2+(6*4)+self.__right_align(), y+2,   str(self.__now), 7)
        pyxel.text(x+2,       y+2+8, 'BEST', 7)
        pyxel.text(x+2+(6*4), y+2+8, str(self.__best.Score), 7)
        pyxel.text(x+2,       y+2+24, 'Push R key', 7)
    def __right_align(self):
        return ( len(str(self.__best.Score)) - len(str(self.__now)) ) * 4

class PlayScene(Scene):
    def __init__(self):
        self.init()
    def init(self, *args, **kwargs):
        self.__pc = PC()
        self.__blocks = [Block(self.__pc.countup), Block(self.__pc.countup)]
        self.__blocks[1].X = self.__blocks[0].X + (Window.Width // 2) + (self.__blocks[0].W // 2)
        self.__is_gameover = False
    def update(self):
        if self.__is_gameover: return SceneType.Score, [self.__pc.Count]
        self.__detect_collision()
        self.__pc.update()
        for b in self.__blocks: b.update()
    def draw(self):
        pyxel.cls(0)
        for b in self.__blocks: b.draw()
        self.__pc.draw()
        pyxel.text(Window.Width // 2 - (len(str(self.__pc.Count)) * 4 // 2), 8, str(self.__pc.Count), 3)
        if self.__is_gameover:
            pyxel.text(Window.Width // 2 - (4*9/2), Window.Height // 2, 'Game Over', 7)
    def __detect_collision(self):
        self.__detect_collision_window()
        self.__detect_collision_block()
    def __detect_collision_window(self):
        if self.__pc.Y < 0 or Window.Height < self.__pc.Y:
            self.__is_gameover = True
    def __detect_collision_block(self):
        for b in self.__blocks:
            if (b.X <= self.__pc.X and \
                ((self.__pc.Y - self.__pc.R <= b.SafeY) or \
                 (b.SafeY + b.SafeH <= self.__pc.Y + self.__pc.R))):
                self.__is_gameover = True

class SizeObject:
    def __init__(self):
        self.__w = 8
        self.__h = 8
        self.__x = self.W // 2
        self.__y = Window.Height // 2
        self.__color = 7
    @property
    def X(self): return self.__x
    @property
    def Y(self): return self.__y
    @property
    def W(self): return self.__w
    @property
    def H(self): return self.__h
    @property
    def Color(self): return self.__color
    @X.setter
    def X(self, value): self.__x = value
    @Y.setter
    def Y(self, value): self.__y = value
    @W.setter
    def W(self, value): self.__w = value
    @H.setter
    def H(self, value): self.__h = value
    @Color.setter
    def Color(self, value):
        if -1 < value < 16: self.__color = value

class PC(SizeObject):
    JumpV = -4
    def __init__(self):
        super(self.__class__, self).__init__()
        self.W = 8
        self.H = 8
        self.X = self.W // 2
        self.Y = Window.Height // 2
        self.Color = 7
        self.__r = 4
        self.__vy = 0
        self.__junpping = False
        self.__count = -2
    @property
    def R(self): return self.__r
    @property
    def Count(self): return self.__count
    def update(self):
        self.__move()
    def __move(self):
        if 0 == pyxel.frame_count % 3:
            if pyxel.btn(pyxel.KEY_SPACE):
                self.__vy = self.__class__.JumpV
            self.__vy += 1
            self.Y = self.Y + self.__vy
    def draw(self):
        pyxel.circ(self.X, self.Y, self.R, self.Color)
    def countup(self): self.__count += 1

class Block(SizeObject):
    def __init__(self, on_next):
        super(self.__class__, self).__init__()
        self.W = 12
        self.H = Window.Height
        self.X = Window.Width
        self.Y = 0
        self.Color = 10
        self.__on_next = on_next
        self.__next()
    @property
    def SafeH(self): return self.__safe_h
    @property
    def SafeY(self): return self.__safe_y
    def update(self):
        if 0 == pyxel.frame_count % 3:
            self.X = self.X - 1
        if self.X + self.W <= 0:
            self.__next()
    def __next(self):
        self.__on_next()
        self.X = Window.Width
        self.__safe_h = random.randint(0, abs(PC.JumpV) // 2) + abs(PC.JumpV*6)
        self.__safe_y = random.randint(0, (Window.Height - self.__safe_h))
    def draw(self):
        pyxel.rect(self.X, self.Y, self.W, self.H, self.Color)
        pyxel.rect(self.X, self.__safe_y, self.W, self.__safe_h, 0)
    def set_event_on_next(self, func):
        self.__on_next = func
        

App()
