import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def plot_single_curve(x, y, title, xlabel, ylabel, color="blue"):
    plt.plot(x, y, label="data_curve", color=color)

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.legend()
    plt.show()

def plot_muti_curve(x_data, y_data, title, xlabel, ylabel, colors=None, labels=None):
    """
    在同一张图上绘制多条曲线
    参数:
        x_data (list of lists): 多个x数据集，例如 [[x1], [x2], ...]
        y_data (list of lists): 多个y数据集，例如 [[y1], [y2], ...]
        title (str): 图表标题
        xlabel (str): X轴标签
        ylabel (str): Y轴标签
        colors (list of str, 可选): 每条曲线的颜色，例如 ["red", "blue"]
        labels (list of str, 可选): 每条曲线的图例标签
    """
    # 处理单条曲线的情况（保持兼容性）
    if not isinstance(x_data[0], (list, tuple, np.ndarray)):
        x_data = [x_data]
    if not isinstance(y_data[0], (list, tuple, np.ndarray)):
        y_data = [y_data]
    
    # 检查数据长度是否一致
    if len(x_data) != len(y_data):
        raise ValueError("x_data和y_data的曲线数量不一致")
    
    # 设置默认颜色和标签
    n_curves = len(x_data)
    default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    if colors is None:
        colors = default_colors[:n_curves]
    else:
        colors += default_colors[len(colors):n_curves]  # 补充不足的颜色
    
    if labels is None:
        labels = [f"Curve {i+1}" for i in range(n_curves)]
    
    # 绘制所有曲线
    for i in range(n_curves):
        plt.plot(x_data[i], y_data[i], color=colors[i], label=labels[i])
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)  # 可选：添加网格线
    plt.show()


def data_to_csv(t, T, dT):
    df = pd.DataFrame({
        "Time" : t,
        "Temperature" : T,
        "Derivative of temperature" : dT
    })
    df.to_csv("Data/Data_Collect.csv", index=False)
