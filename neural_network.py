import random
import math
import aigame_config as config

# sigmod函数定义
def sigmod(x):
    if x <= -700:
        return 0.0
    elif x >= 50:
        return 1.0
    y = 1 / (1 + math.exp(-x))
    return y

#随机化权重，（-1，1）之间
def random_weight():
    return random.random() * 2 - 1

# 异常函数
class NeuralErr(Exception):
    pass

# 神经元
class Neuron(object):
    def __init__(self, pre_neuron_num):
        # 根据上一层神经元的数量来初始化weights
        # 初始化的weights应该选择这什么值？
        # 选择标准是权值*输入数据的结果的累计和尽量处于活跃状态(-5,5)
        # 这里我们就讲权值设定在（-1，1）
        self.weights = [random_weight() for _ in range(pre_neuron_num)]
        # 随机生成[pre_neuron_num,1]的权重
        self.value = 0

    def cal_result(self, inputs):
        #
        if not len(inputs) == len(self.weights):
            # 输入层的数量要和权重的维数一样
            raise NeuralErr("输入数据的个数不正确")
        sum = 0
        for i in range(len(inputs)):
            sum += inputs[i] * self.weights[i]
        self.value = sigmod(sum)
        # 通过sigmoid函数输出
        return self.value
#       权值*输入数据的结果的累计和

# 层中的数据
class Layer(object):
    def __init__(self, neuron_num, pre_neuron_num):
        self.neurons = [Neuron(pre_neuron_num) for i in range(neuron_num)]

    def __iter__(self):
        for n in self.neurons:
            yield n

    def __len__(self):
        return len(self.neurons)


class NeuralNetwork(object):
    def __init__(self, input, hiddens, output):
        self.layers = []
        pre_layer_neurons = 0
        # 1.输入层
        input_layer = Layer(input, pre_layer_neurons)
        # 初始化输入层
        self.layers.append(input_layer)
        # 将输入层放入layers中
        # 2.隐含层
        pre_layer_neurons = len(input_layer)
        for hidden in hiddens:
            # hiddens代表有多少层隐藏层
            hidden_layer = Layer(hidden, pre_layer_neurons)
            self.layers.append(hidden_layer)
            # 将隐藏层放进layers中
            pre_layer_neurons = len(hidden_layer)
        # 3.输出层
        output_layer = Layer(output, pre_layer_neurons)
        self.layers.append(output_layer)
        # 将输出层放进layers中

    def getResult(self, inputs):
        if not len(inputs) == len(self.layers[0]):
            raise NeuralErr("提供的数据和输入层节点数不匹配")
        pre_values = []
        for layer in self.layers:
            result = []
            # 输入层获取感知数据
            if layer == self.layers[0]:
                for i in range(len(inputs)):
                    layer.neurons[i].value = inputs[i]
                    pre_values.append(layer.neurons[i].value)
            else:
                for neuron in layer:
                    neuron.cal_result(pre_values)
                    result.append(neuron.value)
                pre_values = result
        return result

    def getNetwork(self):
        '''
        将神经网络模型数据化
        结构、数据集
        :return:{"network":[5,5,1],"weights":[w1,w2,w3,w4,w5...]}
        '''
        data = {"network": [], "weights": []}
        for layer in self.layers:
            data['network'].append(len(layer))
            for neuron in layer:
                for weight in neuron.weights:
                    data['weights'].append(weight)
        return data

    def setNetwork(self, networkData):
        # 根据数据对网络进行复制
        '''
        使用数据化模型重置神经网络
        :param networkData:数据化的神经网络模型
        :return: None
        '''
        self.layers = []
        pre_layer_neurons = 0
        weight_index = 0
        for layer_neuron_num in networkData['network']:
            layer = Layer(layer_neuron_num, pre_layer_neurons)
            for neuron in layer:
                for i in range(len(neuron.weights)):
                    neuron.weights[i] = networkData['weights'][weight_index]
                    weight_index += 1
            self.layers.append(layer)
            pre_layer_neurons = layer_neuron_num

    def __str__(self):
        s = ""
        for layer in self.layers:
            s += "=" * 50 + "\n"
            for n in layer:
                s += "{"
                for w in n.weights:
                    s += str(w) + ","
                s += "｝\n"
        return s


if __name__ == '__main__':
    network = config.network
    myNetwork1 = NeuralNetwork(network[0], network[1], network[2])
    myNetwork2 = NeuralNetwork(network[0], network[1], network[2])
    print(myNetwork1)
    print(myNetwork2)
    myNetwork2.setNetwork(myNetwork1.getNetwork())
    print(myNetwork2)



