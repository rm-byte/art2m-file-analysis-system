import networkx as nx
from matplotlib import pyplot as plt
from random import randint, choice

from logs import write_logs


class ARTGraph:
    def __init__(self):
        self._points_number = 1
        self._colors = []
        self._pos = {}
        self._type_color = {}
        self._nx_graph = nx.Graph()
        self._options = {
            'node_color': None,
            'edge_color': '#090001',
            'node_size': 40,
            'width': 1,
            'font_size': 50
        }

    def _generate_hex_colors(self, num_of_colors: int) -> list:
        hex_colors = []
        choice_sequence = ['A', 'B', 'C', 'D', 'E', 'F']
        for i in range(10):
            choice_sequence.append(str(i))
        for i in range(num_of_colors):
            color = '#'
            for j in range(6):
                color += choice(choice_sequence)
            hex_colors.append(color)
        # print('hex_colors', hex_colors)
        return hex_colors

    def _set_node_color(self) -> list:
        # перевод цветов узлов из int в hex
        hex_colors = self._generate_hex_colors(len(self._type_color))
        hex_type_color = {}
        ind = 0
        for i in self._type_color:
            type_color = self._type_color.get(i)
            if hex_type_color.get(type_color) is None:
                hex_type_color[type_color] = hex_colors[ind]
                ind += 1
        node_colors = [hex_type_color.get(color) for color in self._colors]

        print('Цвета узлов:', node_colors)
        print('HEX-цвет к ним', hex_type_color)
        return node_colors

    def create_graph(self, filename: str) -> None:
        try:
            f = open(filename)
            for line in f:
                # разделили вектор на числовую часть и его тип
                a = line.split("|")
                points = a[0].split(" ")
                try:
                    color_type = a[2]
                except IndexError:
                    color_type = a[1]
                # если к типу вектора есть цвет, то этот пункт пропускается,
                # иначе - выдается уникальный int-номер цвета для данного вектора
                if self._type_color.get(color_type) is None:
                    self._type_color[color_type] = randint(0, 1000000)

                # добавление вершин и связей в граф
                prev_point = None
                self._points_number -= 1
                for point in points:
                    cur_point = tuple([int(x) for x in point.split(',')])
                    assert len(cur_point) == 2
                    if cur_point not in self._nx_graph.nodes:
                        self._colors.append(self._type_color[color_type])
                        self._points_number += 1
                        self._nx_graph.add_node(cur_point)
                    if prev_point is not None:
                        if (cur_point, prev_point) not in self._nx_graph.edges:
                            self._nx_graph.add_edge(cur_point, prev_point)

                    self._pos[cur_point] = cur_point
                    prev_point = cur_point
            f.close()
        except FileNotFoundError as e:
            write_logs(str(e))
            print(e)

    def draw_graph(self) -> None:
        self._options['node_color'] = self._set_node_color()
        limits = plt.axis('on')
        nx.draw(self._nx_graph, pos=self._pos, **self._options)
        plt.savefig('./graphs/graph.png')
        plt.show()
        plt.close()

        nx.draw(self._nx_graph, pos=nx.spring_layout(self._nx_graph), **self._options)
        plt.savefig('./graphs/graph_spring_layout.png')
        plt.show()
        plt.close()

        # проверка на повторяющиеся цвета
        list = [self._type_color.get(str(i)) for i in self._type_color]
        list.sort()


if __name__ == '__main__':
    artgraph = ARTGraph()
    artgraph.create_graph('result/graph.txt')
    artgraph.draw_graph()
