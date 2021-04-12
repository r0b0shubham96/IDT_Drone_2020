from utm import utmconv
import numpy as np
from matplotlib import pyplot as plt
from random import randint, seed

from nordbo_ai.utils import utils as u
from qgc_generator import generate
from hermite import cubic_hermite_spline

seed(3)


def fix_outliers(es, ns, hs, ts):
    vs = []
    for i in range(1, len(es)):
        e0 = es[i - 1]
        n0 = ns[i - 1]
        h0 = hs[i - 1]
        e1 = es[i]
        n1 = ns[i]
        h1 = hs[i]
        dt = ts[i - 1] - ts[i]
        d = np.sqrt((e1 - e0) ** 2 + (n1 - n0) ** 2 + (h1 - h0) ** 2)
        vs.append(d / dt)

    mu = np.mean(vs)
    std = np.std(vs)

    new_es = [es[0]]
    new_ns = [ns[0]]
    new_hs = [hs[0]]
    new_ts = [ts[0]]
    for i in range(1, len(vs)):
        e0 = new_es[-1]
        n0 = new_ns[-1]
        h0 = new_hs[-1]
        e1 = es[i]
        n1 = ns[i]
        h1 = hs[i]
        d = np.sqrt((e1 - e0) ** 2 + (n1 - n0) ** 2 + (h1 - h0) ** 2)
        frac = (mu + std) / d

        # Shorten step in outlier direction
        # new_es.append(e0 + min(1, frac) * (e1 - e0))
        # new_ns.append(n0 + min(1, frac) * (n1 - n0))

        # Skip outlier
        if not frac < 1:
            new_es.append(e1)
            new_ns.append(n1)
            new_hs.append(h1)
            new_ts.append(ts[i])

    return new_es, new_ns, new_hs, new_ts


class TrackSimplifier:
    def __init__(self, es, ns, hs, ts):
        self.es = es
        self.ns = ns
        self.hs = hs
        self.ts = ts

    def max_waypoints(self, num):
        idxs = np.linspace(0, len(self.ts) - 1, num)
        idxs = [int(idx) for idx in idxs]
        new_es = [e for idx, e in enumerate(self.es) if idx in idxs]
        new_ns = [n for idx, n in enumerate(self.ns) if idx in idxs]
        new_hs = [h for idx, h in enumerate(self.hs) if idx in idxs]
        new_ts = [t for idx, t in enumerate(self.ts) if idx in idxs]

        return new_es, new_ns, new_hs, new_ts

    @staticmethod
    def douglas_peucker(points, epsilon, angle=None):
        def dist2line(p, a, b):
            p = np.array(p)
            a = np.array(a)
            b = np.array(b)

            # normalized tangent vector
            d = np.divide(b - a, np.linalg.norm(b - a))

            # signed parallel distance components
            s = np.dot(a - p, d)
            t = np.dot(p - b, d)

            # clamped parallel distance
            h = np.maximum.reduce([s, t, 0])

            # perpendicular distance component
            c = np.cross(p - a, d)

            return np.hypot(h, np.linalg.norm(c))

        dmax = 0
        index = 0
        end = len(points)
        for i in range(1, end - 1):
            d = dist2line(points[i][:-1], points[0][:-1], points[-1][:-1])
            if dmax < d:
                dmax = d
                index = i

        result_list = [points[0], points[-1]]
        if epsilon < dmax:
            rec_results1 = TrackSimplifier.douglas_peucker(points[:index + 1], epsilon, angle)
            rec_results2 = TrackSimplifier.douglas_peucker(points[index:], epsilon, angle)
            result_list = rec_results1[:-1] + rec_results2
        elif angle:
            ba = np.array(points[0][:-1]) - np.array(points[index][:-1])
            bc = np.array(points[-1][:-1]) - np.array(points[index][:-1])
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            a = np.degrees(np.arccos(cosine_angle))
            if abs(a) < angle:
                rec_results1 = TrackSimplifier.douglas_peucker(points[:index + 1], epsilon, angle)
                rec_results2 = TrackSimplifier.douglas_peucker(points[index:], epsilon, angle)
                result_list = rec_results1[:-1] + rec_results2
            else:
                result_list = [points[0], points[index], points[-1]]

        return result_list

    def minimize_deviation(self, epsilon, angle=None):
        results = self.douglas_peucker([(self.es[i], self.ns[i], self.hs[i], self.ts[i]) for i in range(len(self.ts))],
                                       epsilon, angle)

        new_es = []
        new_ns = []
        new_hs = []
        new_ts = []
        for r in results:
            new_es.append(r[0])
            new_ns.append(r[1])
            new_hs.append(r[2])
            new_ts.append(r[3])

        return new_es, new_ns, new_hs, new_ts


if __name__ == "__main__":
    mission = u.load_json("mission.plan")
    items = mission["mission"]["items"]
    coords = [tuple(i["params"][-3:]) for i in items]

    uc = utmconv()
    es = []
    ns = []
    hs = []
    for c in coords:
        lat, lon, height = c
        (hemisphere, zone, letter, e, n) = uc.geodetic_to_utm(lat, lon)
        es.append(e)
        ns.append(n)
        hs.append(height)

    mu_es = np.mean(es)
    mu_ns = np.mean(ns)
    es = [e - mu_es for e in es]
    ns = [n - mu_ns for n in ns]
    lim = max([abs(i) for i in ns + es]) * 1.2

    for c in range(5):
        i = randint(0, len(es))
        e = randint(int(min(es) * 0.9), int(max(es) * 1.1))
        n = randint(int(min(ns) * 0.9), int(max(ns) * 1.1))
        h = randint(int(min(hs) * 0.9), int(max(hs) * 1.1))
        es.insert(i, e * 0.9)
        ns.insert(i, n * 0.9)
        hs.insert(i, h)
        es.insert(i, e * 0.9)
        ns.insert(i, n * 1.1)
        hs.insert(i, h)
        es.insert(i, e * 1.1)
        ns.insert(i, n * 1.1)
        hs.insert(i, h)
        es.insert(i, e * 1.1)
        ns.insert(i, n * 0.9)
        hs.insert(i, h)

    ts = list(np.linspace(0, 180, len(es)))
    new_es, new_ns, new_hs, new_ts = fix_outliers(es, ns, hs, ts)


    def plot_track(ts, es, ns, hs, new_ts, new_es, new_ns, new_hs, filename, label1, label2):
        plt.subplot(1, 2, 1)
        plt.plot(es, ns, "k.:", label=label1, alpha=0.2)
        plt.plot(new_es, new_ns, "ro:", label=label2)
        plt.legend()
        plt.xlim(-lim, lim)
        plt.ylim(-lim, lim)
        plt.grid(True)
        plt.title("GNSS Mission Track")
        plt.xlabel("Eastings [m]")
        plt.ylabel("Northings [m]")
        plt.subplot(1, 2, 2)
        plt.plot(ts, hs, "k", label=label1)
        plt.plot(new_ts, new_hs, "r", label=label2)
        plt.legend()
        plt.grid(True)
        plt.title("GNSS Mission Height")
        plt.xlabel("Time [s]")
        plt.ylabel("Height [m]")
        plt.savefig(filename)


    plt.figure(1, (20, 8))
    plot_track(ts, es, ns, hs, new_ts, new_es, new_ns, new_hs, "mission.png", "original", "no outliers")

    simpler = TrackSimplifier(new_es, new_ns, new_hs, new_ts)

    plt.figure(2, (20, 8))
    ees, nns, hhs, tts = simpler.max_waypoints(10)
    wes, wns, wts = (ees, nns, tts)
    plot_track(new_ts, new_es, new_ns, new_hs, tts, ees, nns, hhs, "max_waypoints.png", "no outliers", "max waypoints")

    plt.figure(3, (20, 8))
    ees, nns, hhs, tts = simpler.minimize_deviation(3)
    plot_track(new_ts, new_es, new_ns, new_hs, tts, ees, nns, hhs, "track_deviation.png", "no outliers",
               "minimized track deviation")

    plt.figure(4, (20, 8))
    ees, nns, hhs, tts = simpler.minimize_deviation(10, 120)
    plot_track(new_ts, new_es, new_ns, new_hs, tts, ees, nns, hhs, "track_deviation_angle.png", "no outliers",
               "minimized track deviation and angle")

    new_coords = []
    for e, n, h in zip(ees, nns, hhs):
        lat, lon = uc.utm_to_geodetic(hemisphere, zone, e, n)
        new_coords.append((lat, lon, h))

    s_es = []
    s_ns = []

    chs = cubic_hermite_spline()
    for i in range(1, len(wts)):
        p0 = [wes[i - 1], wns[i - 1]]
        p1 = [wes[i], wns[i]]
        t0 = [p1[0] - p0[0], p1[1] - p0[1]]
        if i == len(wts) - 1:
            t1 = t0
        else:
            t1 = [wes[i + 1] - p1[0], wns[i + 1] - p1[1]]
        cs = chs.goto_wpt(p0, t0, p1, t1, steps=10)
        s_es += [c[0] for c in cs[1:]]
        s_ns += [c[1] for c in cs[1:]]

    s_es.append(wes[-1])
    s_ns.append(wns[-1])

    plt.figure(5, (10, 8))
    plt.plot(wes, wns, "k.:", label="max waypoints")
    plt.plot(s_es, s_ns, "ro:", label="fixed wing")
    plt.legend()
    plt.xlim(-lim, lim)
    plt.ylim(-lim, lim)
    plt.grid(True)
    plt.title("GNSS Mission Track")
    plt.xlabel("Eastings [m]")
    plt.ylabel("Northings [m]")
    plt.savefig("fixed_wing.png")