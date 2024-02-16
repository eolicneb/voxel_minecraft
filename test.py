import csv
import math
import pathlib
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use('Agg')

csv_file = pathlib.Path("data.csv")
csv_file.exists()

reader = csv.reader(csv_file.open("r"), delimiter=";")
def get_data(reader):
    h = next(reader)
    for val in reader:
        yield {col: float(v) for col, v in zip(h, val)}

data = list(get_data(reader))
data_2 = [d | {'v_norm': math.sqrt(d['vx']**2 + d['vz']**2)} for d in data]
data_3 = [d | {'v_yaw': math.atan2(d['vx'], d['vz'])} for d in data_2]
points = [(d['time'], d['p_yaw'], d['v_yaw']) for d in data_3]

plt.plot(*zip(*points))
plt.show()