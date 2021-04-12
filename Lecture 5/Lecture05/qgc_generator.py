import json


def generate(points):
    plan = {}
    geoFence = {}
    plan['fileType'] = 'Plan'

    geoFence['polygon'] = []
    geoFence['version'] = 1
    plan['geoFence'] = geoFence

    plan['groundStation'] = 'QGroundControl'

    items = [{
        "autoContinue": True,
        "command": 22,
        "doJumpId": 1,
        "frame": 3,
        "params": [0, 0, 0, 0, points[0][0], points[0][1], points[0][2]],
        "type": "SimpleItem"
    }]
    for i, p in enumerate(points[1:]):
        items.append({
            "autoContinue": True,
            "command": 16,
            "doJumpId": i + 1,
            "frame": 3,
            "params": [0, 0, 0, 0, points[0], points[1], points[2]],
            "type": "SimpleItem"
        })

    mission = {
        'cruiseSpeed': 15,
        'firmwareType': 3,
        'hoverSpeed': 5,
        'items': items,
        'plannedHomePosition': list(points[0]),
        'vehicleType': 2,
        'version': 2
    }
    plan['mission'] = mission

    rallyPoints = {
        'points': [],
        'version': 1
    }
    plan['rallyPoints'] = rallyPoints
    plan['version'] = 1

    plan_json = json.dumps(plan, indent=4, sort_keys=True)

    file = open('new_mission.plan', 'w')
    file.write(plan_json)
    file.close()

    return plan
