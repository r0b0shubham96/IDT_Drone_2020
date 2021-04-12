import csv
from matplotlib import pyplot as plt


class DataLoader():
    def __init__(self):
        self.data = {
            "acc": {
                "t": [],
                "x": [],
                "y": [],
                "z": []
            },
            "para": {
                "t": [],
                "trigger": []
            },
            "telem": {
                "t": [],
                "rx_err": []
            }
        }

    def load_para(self, file: str):
        with open(file) as f:
            reader = csv.DictReader(f, delimiter=',')
            print(reader)
            for row in reader:
                self.data["para"]["t"].append(float(row['timestamp']) * 1e-6)
                self.data["para"]["trigger"].append(float(row['aux1']) * 20)

    def load_acc(self, file: str):
        with open(file) as f:
            reader = csv.DictReader(f, delimiter=',')
            print(reader)
            for row in reader:
                self.data["acc"]["t"].append(float(row['timestamp']) * 1e-6)
                self.data["acc"]["x"].append(float(row['accelerometer_m_s2[0]']))
                self.data["acc"]["y"].append(float(row['accelerometer_m_s2[1]']))
                self.data["acc"]["z"].append(float(row['accelerometer_m_s2[2]']))

    def load_telemetry(self, file: str):
        with open(file) as f:
            reader = csv.DictReader(f, delimiter=',')
            print(reader)
            for row in reader:
                self.data["telem"]["t"].append(float(row['timestamp']) * 1e-6)
                self.data["telem"]["rx_error"].append(float(row['rxerrors']))


### Class end - Main start

if __name__ == '__main__':
    tests = {
        "5": {
            "tstart": 302 - 10,
            "tend": 344
        },
        "8": {

        },
        "9": {

        }
    }
    SENSOR_COMBINED = '/home/sh/School/IDT/IDT_materials_module_8/exercise_materials/csv_files/TEST9_08-02-19/TEST9_08-02-19_sensor_combined_0.csv'
    MANUAL_CONTROLLED_SETPOINT = '/home/sh/School/IDT/IDT_materials_module_8/exercise_materials/csv_files/TEST9_08-02-19/TEST9_08-02-19_manual_control_setpoint_0.csv'

    dl = DataLoader()
    dl.load_acc(SENSOR_COMBINED)
    dl.load_para(MANUAL_CONTROLLED_SETPOINT)

    # Here you can add the analysis of the different parameters and create boolean variables that triggers upon failure detection.
    # You can likewise plot these failure detection parameters (with the same timestamp as the investigated dataset) together with the logged data.

    fig, ax = plt.subplots()

    # Acceleration plot
    ax.plot(dl.data["acc"]["t"], dl.data["acc"]["x"], linewidth=0.5, label='accel_x')
    ax.plot(dl.data["acc"]["t"], dl.data["acc"]["y"], linewidth=0.5, label='accel_y')
    ax.plot(dl.data["acc"]["t"], dl.data["acc"]["z"], linewidth=0.5, label='accel_z')

    # Parachute plot
    ax.plot(dl.data["para"]["t"], dl.data["para"]["trigger"], linewidth=1, label='para_trigger')

    ax.set(xlabel='time (s)', ylabel='acceleration (m/s^2)', title='Acceleration Plot of Test 9')
    legend = ax.legend(loc='best', shadow=True, fontsize='medium')
    ax.grid()
    plt.show()