import matplotlib.pyplot as plt

def plot_curve(x, y, title, xlabel, ylabel, color="blue"):
    plt.plot(x, y, label="data_curve", color=color)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.legend()
    plt.show()
