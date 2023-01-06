# coding=utf-8
import time
import random
import pygame
from pygame.locals import *


class Base(object):
    def __init__(self, screen, name):
        self.name = name
        # 设置要显示内容的窗口
        self.screen = screen


class Plane(Base):
    def __init__(self, screen, name):
        super().__init__(screen, name)
        self.image = pygame.image.load(self.imageName).convert()
        # 用来存储英雄飞机发射的所有子弹
        self.bulletList = []

    def display(self):
        # 更新飞机的位置
        self.screen.blit(self.image, (self.x, self.y))
        # 判断一下子弹的位置是否越界，如果是，那么就要删除这颗子弹
        #
        # 这种方法会漏掉很多需要删除的数据
        # for i in self.bulletList:
        #     if i.y<0:
        #         self.bulletList.remove(i)
        # 存放需要删除的对象信息
        needDelItemList = []
        for i in self.bulletList:
            if i.judge():
                needDelItemList.append(i)
        for i in needDelItemList:
            self.bulletList.remove(i)
        # del needDelItemList
        # 更新及这架飞机发射出的所有子弹的位置
        for bullet in self.bulletList:
            bullet.display()
            bullet.move()

        # 修改所有子弹的位置
        # for bullet in self.bulletList:
        #     bullet.y -= 2

    def sheBullet(self):
        newBullet = PublicBullet(self.x, self.y, self.screen, self.name)
        self.bulletList.append(newBullet)


class HeroPlane(Plane):

    def __init__(self, screen, name):

        # 设置飞机默认的位置
        self.x = 230
        self.y = 600
        self.imageName = "./img/my_airplane.png"
        super().__init__(screen, name)

    def moveLeft(self):
        self.x -= 10

    def moveRight(self):
        self.x += 10


class EnemyPlane(Plane):
    # 重写父类的__init_-方法
    def __init__(self, screen, name):

        # 设置飞机默认的位置
        self.x = 0
        self.y = 0
        self.imageName = "./img/enemy_airplane.png"

        # 调用父类的__init__方法
        super().__init__(screen, name)

        self.direction = "right"

    def move(self):
        # 如果碰到了右边的边界，那么就往左走，如果碰到了左边的边界，那么就往右走
        if self.direction == "right":
            self.x += 2
        elif self.direction == "left":
            self.x -= 2

        if self.x > 480 - 50:
            self.direction = "left"
        elif self.x < 0:
            self.direction = "right"

    def sheBullet(self):
        num = random.randint(1, 100)
        if num == 88:
            super().sheBullet()


class PublicBullet(Base):
    def __init__(self, x, y, screen, planeName):

        super().__init__(screen, planeName)

        if self.name == "hero":
            self.x = x + 40
            self.y = y - 20
            imageName = "./img/my_bullet.png"

        elif self.name == "enemy":
            self.x = x + 30
            self.y = y + 30
            imageName = "./img/enemy_bullet.png"
        self.image = pygame.image.load(imageName).convert()

    def move(self):
        if self.name == "hero":
            self.y -= 2
        elif self.name == "enemy":
            self.y += 2

    def display(self):
        self.screen.blit(self.image, (self.x, self.y))

    def judge(self):
        if self.y > 890 or self.y < 0:
            return True
        else:
            return False


if __name__ == "__main__":

    # 1. 创建一个窗口，用来显示内容
    screen = pygame.display.set_mode((480, 750), 0, 32)

    # 2. 创建一个和窗口大小的图片，用来充当背景
    background = pygame.image.load("./img/bk.png").convert()

    # 3. 创建一个飞机对象
    heroPlane = HeroPlane(screen, "hero")

    # 4. 创建一个敌人飞机
    enemyPlane = EnemyPlane(screen, "enemy")

    # 3. 把背景图片放到窗口中显示
    while True:
        screen.blit(background, (0, 0))

        heroPlane.display()

        enemyPlane.move()
        enemyPlane.sheBullet()
        enemyPlane.display()

        # 判断是否是点击了退出按钮
        for event in pygame.event.get():
            # print(event.type)
            if event.type == QUIT:
                print("exit")
                exit()
            elif event.type == KEYDOWN:
                if event.key == K_a or event.key == K_LEFT:
                    print('left')
                    heroPlane.moveLeft()
                    # 控制飞机让其向左移动
                elif event.key == K_d or event.key == K_RIGHT:
                    print('right')
                    heroPlane.moveRight()
                elif event.key == K_SPACE:
                    print("space")
                    heroPlane.sheBullet()

        time.sleep(0.01)

        pygame.display.update()