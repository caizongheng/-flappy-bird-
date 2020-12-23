import pygame
import pygame.locals as locals
import random
import numpy as np
import neural_network
import aigame_config as config
import evolution
# import numpy as np
import os

pygame.init()


class Pipe(object):
    # 图片
    BTM_IMG = pygame.image.load("./res/pipe.png")
    TOP_IMG = pygame.transform.rotate(BTM_IMG, 180)
    min_visual_value = 80
    WIDTH = BTM_IMG.get_width()
    HEIGHT = BTM_IMG.get_height()

    def __init__(self):
        self.x = Game.SIZE[0]
        # 上下管道的管口Y坐标
        self.top_y = random.randint(Pipe.min_visual_value, Game.SIZE[1] - Game.PIPE_GAP_SIZE - Pipe.min_visual_value)
        self.btm_y = self.top_y + Game.PIPE_GAP_SIZE
        self.alive = True
        self.score = 1

    def draw(self, surface):
        surface.blit(Pipe.TOP_IMG, (self.x, self.top_y - Pipe.HEIGHT))
        surface.blit(Pipe.BTM_IMG, (self.x, self.btm_y))

    def update(self):
        self.x -= 5
        if self.x < -Pipe.WIDTH:
            self.alive = False


class PipeManager(object):
    def __init__(self, score):
        self.pipes = [Pipe()]
        self.count = 0
        self.create_times = random.randint(45, 55)

    def drawPipes(self, surface):
        for pipe in self.pipes:
            pipe.draw(surface)

    def updatePipes(self):
        self.createPipe()
        index = len(self.pipes) - 1
        while index >= 0:
            pipe = self.pipes[index]
            if pipe.alive:
                pipe.update()
            else:
                self.pipes.remove(pipe)
                pass
            index -= 1

    def createPipe(self):
        self.count += 1
        if self.count % self.create_times == 0:
            self.pipes.append(Pipe())
            self.count = 0
            self.create_times = random.randint(45, 55)


class Bird(object):
    IMG = pygame.image.load("./res/bird.png")
    WIDTH = IMG.get_width()
    HEIGHT = IMG.get_height()

    def __init__(self, netwoek):
        self.x = 50
        self.y = 200
        self.speed = 0
        self.fly_speed = -8
        self.max_speed = 8
        self.alive = True
        self.neural_netwoek = netwoek

    def draw(self, surface):
        surface.blit(Bird.IMG, (self.x, self.y))

    def update(self):
        self.y += self.speed
        self.speed += 1
        if self.speed >= self.max_speed:
            self.speed = self.max_speed
        if self.y <= 0 or self.y + Bird.HEIGHT >= Game.SIZE[1]:
            self.alive = False

    def fly(self):
        self.speed = self.fly_speed

    def collision(self, pipes):
        for pipe in pipes:
            # 判断当前管道是否被小鸟飞跃（没有飞跃）
            if self.x < pipe.x + Pipe.WIDTH:
                if self.x + Bird.WIDTH > pipe.x and self.x < pipe.x + Pipe.WIDTH:
                    if self.y < pipe.top_y or self.y + Bird.HEIGHT > pipe.btm_y:
                        self.alive = False
                        return True
                return False

    def get_inputs(self, pipes):
        pipe = None
        for p in pipes:
            if self.x < p.x + Pipe.WIDTH:
                pipe = p
                break
        inputs = []
        for _ in range(config.network[0]):
            inputs.append(0.0)
        inputs[0] = self.y / Game.SIZE[1]
        if pipe:
            inputs[1] = (self.x + Bird.WIDTH) - pipe.x
            inputs[2] = self.x - (pipe.x + Pipe.WIDTH)
            inputs[3] = self.y - pipe.top_y
            inputs[4] = (self.y + Bird.HEIGHT) - pipe.btm_y
        return inputs


class BirdManager(object):
    def __init__(self, ai):
        self.birds = []
        self.ai = ai
        network_data_list = self.ai.manager.create_generation()
        for network_data in network_data_list:
            network = neural_network.NeuralNetwork(config.network[0], config.network[1], config.network[2])
            network.setNetwork(network_data)
            bird = Bird(network)
            self.birds.append(bird)

    def drawBirds(self, surface):
        for bird in self.birds:
            bird.draw(surface)

    def updateBirds(self, pipes, score):
        index = len(self.birds) - 1
        while index >= 0:
            bird = self.birds[index]
            if bird.alive:
                inputs = bird.get_inputs(pipes)
                ret = bird.neural_netwoek.getResult(inputs)
                if ret[0] > 0.5:
                    bird.fly()
                bird.update()
            else:
                self.ai.collect_score(bird.neural_netwoek, score)
                self.birds.remove(bird)
            index -= 1

    def collision(self, pipes):
        for bird in self.birds:
            bird.collision(pipes)

    def is_all_died(self):
        if len(self.birds) == 0:
            return True
        return False


class Score(object):
    def __init__(self):
        self.score = 0
        self.all_imgs = []
        for i in range(10):
            img = pygame.image.load("./res/" + str(i) + ".png")
            self.all_imgs.append(img)
        self.x = 0
        self.y = 30
        self.imgs = []  # 需要绘制的图片

    def draw(self, surface):
        pre_width = 0
        for img in self.imgs:
            surface.blit(img, (self.x + pre_width, self.y))
            self.x = self.x + pre_width
            pre_width = img.get_width()

    def update(self):
        self.imgs.clear()
        # 设计一个函数，将一个数字的各个位进行拆分，以元祖的形式返回
        indexs = self.splitScore()
        for i in indexs:
            self.imgs.append(self.all_imgs[i])
        width = 0
        for img in self.imgs:
            width += img.get_width()
        self.x = Game.SIZE[0] / 2 - width / 2

    def splitScore(self):
        index_list = []
        i = 1
        score = self.score
        while True:
            ret = score % 10
            index_list.insert(0, ret)
            score = int(self.score / 10 ** i)
            if score == 0:
                break
            i += 1
        return tuple(index_list)


class Evolution_ANN_AI(object):
    def __init__(self):
        self.manager = evolution.GenerationManager()

    def collect_score(self, network, score):
        genome = evolution.Genome(network.getNetwork(), score)
        self.manager.add_genome(genome)


class Game(object):
    SIZE = (360, 420)
    FPS = 500
    PIPE_GAP_SIZE = 80

    def __init__(self):
        self.surface = pygame.display.set_mode(Game.SIZE)
        self.clock = pygame.time.Clock()
        self.ai = Evolution_ANN_AI()
        self.generation_num = 0
        self.game_init()

    def game_init(self):
        self.time = 0
        self.score = 0
        self.gameRunning = True
        self.birdManger = BirdManager(self.ai)
        self.pipeManager = PipeManager(self.score)
        self.generation_num += 1

    def start(self):
        while self.gameRunning:
            self.control()
            self.update()
            self.draw()
            pygame.display.update()  # 提交绘制内容
            print("世代：", self.generation_num, "存活数量：", len(self.birdManger.birds), "分数：", self.score)
            if self.score >= 5000 and not os.path.exists("my_modle.csv"):
                data = self.birdManger.birds[0].neural_netwoek.getNetwork()
                weight_array = np.array(data['weights'])
                np.savetxt("./res/my_modle.csv", weight_array, delimiter=',')
                break
            self.time += self.clock.tick(Game.FPS)
        # print(self.time)

    def draw(self):
        # 绘制背景
        self.surface.fill((160, 160, 160))
        self.pipeManager.drawPipes(self.surface)
        self.birdManger.drawBirds(self.surface)
        # self.score.draw(self.surface)

    def update(self):
        if self.birdManger.is_all_died():
            self.restart()
            return
        self.birdManger.collision(self.pipeManager.pipes)
        self.pipeManager.updatePipes()
        self.birdManger.updateBirds(self.pipeManager.pipes, self.score)
        # self.score.update()
        self.score += 1

    def control(self):
        # pygame.mouse.get_pos()#获取鼠标的坐标（当前窗口内的相对坐标）
        # pygame.mouse.get_pressed()#鼠标的点击状态（0，0，0）
        for event in pygame.event.get():
            if event.type == locals.QUIT:
                self.stop()

    def stop(self):
        self.gameRunning = False

    def restart(self):
        self.game_init()


if __name__ == '__main__':
    game = Game()
    game.start()
