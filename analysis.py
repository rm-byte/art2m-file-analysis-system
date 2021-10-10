from matplotlib import pyplot as plt
from numpy import std, mean
from sklearn.metrics import roc_curve


def plot_roc_curve(real_type: list, predicted_type: list) -> None:
    fpr, tpr, thresholds = roc_curve(real_type, predicted_type)
    plt.plot(fpr, tpr, color='green', label='ROC')
    plt.plot([0, 1], [0, 1], color='black', linestyle='--')
    plt.xlabel('FPR')
    plt.ylabel('TPR')
    plt.title('ROC Curve')
    plt.legend()
    plt.show()


def average_time_analysis(filename: str) -> None:
    file = open(filename, 'r')
    f1_time, f2g_time = [], []
    for line in file:
        a = line.split(' ')
        f1_time.append(float(a[0]))
        f2g_time.append(float(a[1]))

    print('F1 | Среднекв.', std(f1_time), 'Кол-во образов:', len(f1_time), 'MAX элемент', max(f1_time),
          'Среднее арифм.:', mean(f1_time))
    print('F2 | Среднекв.', std(f2g_time), 'Кол-во образов:', len(f2g_time), 'MAX элемент', max(f2g_time),
          'Среднее арифм.', mean(f2g_time))


def classification_quality() -> None:
    matrix = []
    num_of_classes = 2
    for i in range(num_of_classes):
        matrix.append([0] * num_of_classes)
    file = open('recognized_current.txt', 'r')
    for line in file:
        recognized, current = line.split('-')[0], line.split('-')[1].split('\n')[0].split(' ')[0]
        if recognized == 'benign':
            j_index = 0
        else:
            j_index = 1
        if current == 'benign':
            i_index = 0
        else:
            i_index = 1
        matrix[i_index][j_index] += 1

    for line in matrix:
        print(line)
    tp = matrix[0][0]
    tn = matrix[1][1]
    fp = matrix[0][1]
    fn = matrix[1][0]
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    tpr = tp / (tp + fn)
    precision = tp / (tp + fp)
    specifity = tn / (fp + tn)
    fpr = fp / (fp + tn)
    print('accuracy', accuracy)
    print('TPR', tpr)
    print('precision', precision)
    print('specifity', specifity)
    print('FPR', fpr)
    print('Всего:', tp + tn + fp + fn)
