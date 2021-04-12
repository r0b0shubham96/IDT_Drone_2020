from matplotlib import pyplot as plt
import numpy as np


def fresnel(n, lamb, d1, d2):
    return np.sqrt(n * lamb * d1 * d2 / (d1 + d2))

if __name__ == "__main__":
    frequencies = {
        "433 MHz": {
            "freq": 433e6
        },
        "2.4 GHz": {
            "freq": 2.4e9
        },
        "5.8 HHz": {
            "freq": 5.8e9
        }
    }
    c = 299792458
    h1 = 1.5
    h2 = 50
    distance = 200
    theta = np.tanh((h2 - h1) / distance)
    sin = np.sin(theta)
    cos = np.cos(theta)
    print(sin)
    print(cos)
    fracs = np.linspace(0, 1, 1001)
    ds = [f * distance for f in fracs]
    plt.plot([0, distance], [0, 0], 'g')
    plt.plot([0, 0], [0, h1], 'k')
    plt.plot([distance, distance], [0, h2], 'k')
    for k, v in frequencies.items():
        f = v["freq"]
        fres1 = []
        fres2 = []
        lamb = c / f

        for frac in fracs:
            d = distance * frac
            fres = fresnel(1, lamb, d, distance - d)
            fres1.append(fres + h1 + (h2 - h1) * frac)
            fres2.append(-fres + h1 + (h2 - h1) * frac)
        v["fres1"] = fres1
        v["fres2"] = fres2
        plt.plot(ds * 2, fres1 + fres2, label=k)
    plt.grid()
    plt.legend()
    plt.title("Fresnel zones")
    plt.xlabel("Distance [m]")
    plt.ylabel("Height [m]")
    plt.show()

    for k, v in frequencies.items():
        print(k)
        i = np.argmin(v["fres2"])
        fres1 = v["fres1"][i]
        fres2 = v["fres2"][i]
        diff = fres1 - fres2
        obst = -min(0, fres2)
        print(f"Obstructed: {obst / diff:.2%}")
        print(f"Clearance: {1 - obst / diff:.2%}\n")

    print()
    for k, v in frequencies.items():
        print(k)
        i = 501
        fres1 = v["fres1"][i]
        fres2 = v["fres2"][i]
        los = fracs[i] * (h2 - h1)
        diff = fres1 - fres2
        max_h = 0.6 * diff
        obst = min(max_h, v["fres2"][i])

        print(f"LoS-line: {los:.2f}. LoS - fres2 + max_height: {los - fres2 + max_h:.2f}")
        print(f"Fres1 {fres1:.2f}, fres2 {fres2:.2f}")
        print(f"Max height halfway: {max_h:.2f}")
        print(f"Clearance: {1 - obst / diff:.2%}\n")
