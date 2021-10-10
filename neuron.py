class Y:
    def __init__(self, n: int):
        self.z_weight = [0] * n
        self.y_next = []
        self.y_value = 0
        self.index_layer = 0
        self.index_number = 0
        self.flag_freeze = False
        self.type = None
        self.s_list = []
        self.y_previous = None
        self.scanned = False
        self.avclass = None

    def search_y_max(self):
        """
        Поиск максимального значения среди y_next
        :return:
        i_max -- Индекс максимального значения y_next.y_value
        y_max -- объект класса Y, содержащий максимальный y_value
        """
        if self.y_next:
            y_max = None
            i_max = None
            for i in range(len(self.y_next)):
                y = self.y_next[i]
                if not y.flag_freeze:
                    i_max = i
                    y_max = y
                    break

            for i in range(len(self.y_next)):
                y = self.y_next[i]
                if not y.flag_freeze:
                    if y.y_value > y_max.y_value:
                        i_max = i
                        y_max = y
        else:
            i_max = -1
            y_max = self
        return i_max, y_max

    def set_indexes(self, layer: int, number: int) -> None:
        self.index_layer = layer
        self.index_number = number
