from matplotlib import pyplot as plt
import re
import numpy as np

if __name__ == "__main__":
    std_loc = []
    std_rem = []
    new_loc = []
    new_rem = []
    for i, file in enumerate(["standard_antenna.txt", "new_antenna.txt"]):
        with open(file) as f:
            lines = f.readlines()

        for l in lines:
            m = re.match(r"^RSSI: (-\d+) dbm, Remote RSSI: (-\d+) dbm$", l)
            if i == 0:
                std_loc.append(int(m.group(1)))
                std_rem.append(int(m.group(2)))
            else:
                new_loc.append(int(m.group(1)))
                new_rem.append(int(m.group(2)))

    std_t = np.linspace(0, 1, len(std_loc))
    new_t = np.linspace(0, 1, len(new_loc))
    plt.plot(std_t, std_loc, label='Local Standard')
    plt.plot(std_t, std_rem, label='Remote Standard')
    plt.plot(new_t, new_loc, label='Local Homemade')
    plt.plot(new_t, new_rem, label='Remote Homemade')
    plt.legend()
    plt.grid(True)
    plt.title('Antenna RSSI comparison')
    plt.xlabel('normalized distance')
    plt.ylabel('RSSI [dbm]')
    plt.savefig('comparison.png')
    plt.show()

    print(std_loc)
    print(std_rem)
    print(new_loc)
    print(new_rem)
