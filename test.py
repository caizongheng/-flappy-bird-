import random
import math


def sigmod(x):
    if x <= -700:
        return 0.0
    elif x >= 50:
        return 1.0
    y = 1 / (1 + math.exp(-x))
    return y


def random_weight():
    return random.random() * 2 - 1


class NeuralErr(Exception):
    pass


class Neuron(object):
    def __init__(self, pre_neuron_num):
        # 根据上一层神经元的数量来初始化weights
        # 初始化的weights应该选择这什么值？
        # 选择标准是权值*输入数据的结果的累计和尽量处于活跃状态(-5,5)
        # 这里我们就讲权值设定在（-1，1）
        self.weights = [random_weight() for _ in range(pre_neuron_num)]
        self.value = 0

    def cal_result(self, inputs):
        if not len(inputs) == len(self.weights):
            raise NeuralErr("输入数据的个数不正确")
        sum = 0
        for i in range(len(inputs)):
            sum += inputs[i] * self.weights[i]
        self.value = sigmod(sum)
        return self.value


class Layer(object):
    def __init__(self, neuron_num, pre_neuron_num):
        self.neurons = [Neuron(pre_neuron_num) for i in range(neuron_num)]

    def __iter__(self):
        for n in self.neurons:
            yield n

def add_genome(num):
    for temp in num_list:
        if num>temp:
            index = num_list.index(temp)
            num_list.insert(index,num)
            return
    num_list.append(num)
num_list=[]
if __name__ == '__main__':
    # for _ in range(5):
    #     input_num=int(input("请输入添加的数值"))
    #     add_genome(input_num)
    #     print(num_list)
    #     print("="*50)
    a = [1,2,3,4,5,6,7]
    del a[:-2]
    print(a)