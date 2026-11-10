"""Tests for Sure Petcare integration."""

HOUSEHOLD_ID = 987654321
HUB_ID = 123456789
PET_TAG_ID = 1001
UNKNOWN_TAG_ID = 1002

MOCK_HUB = {
    "id": HUB_ID,
    "product_id": 1,
    "household_id": HOUSEHOLD_ID,
    "name": "Hub",
    "status": {
        "led_mode": 0,
        "pairing_mode": 0,
        "online": True,
    },
}

MOCK_FEEDER = {
    "id": 12345,
    "product_id": 4,
    "household_id": HOUSEHOLD_ID,
    "name": "Feeder",
    "parent": {"product_id": 1, "id": HUB_ID},
    "control": {"training_mode": 2, "lid": {"close_delay": 4}},
    "tags": [{"id": PET_TAG_ID, "index": 1, "profile": 2}],
    "status": {
        "battery": 6.4,
        "locking": {"mode": 0},
        "learn_mode": 0,
        "signal": {"device_rssi": 60, "hub_rssi": 65},
        "online": True,
    },
}

MOCK_FELAQUA = {
    "id": 31337,
    "product_id": 8,
    "household_id": HOUSEHOLD_ID,
    "name": "Felaqua",
    "parent": {"product_id": 1, "id": HUB_ID},
    "status": {
        "battery": 6.4,
        "signal": {"device_rssi": 70, "hub_rssi": 65},
        "online": True,
    },
}

MOCK_CAT_FLAP = {
    "id": 13579,
    "product_id": 6,
    "household_id": HOUSEHOLD_ID,
    "name": "Cat Flap",
    "parent": {"product_id": 1, "id": HUB_ID},
    "control": {
        "curfew": [{"enabled": True, "lock_time": "19:00", "unlock_time": "07:00"}],
    },
    "tags": [
        {"id": PET_TAG_ID, "index": 1, "profile": 2},
        {"id": UNKNOWN_TAG_ID, "index": 2, "profile": 3},
    ],
    "status": {
        "battery": 6.4,
        "locking": {"mode": 0},
        "learn_mode": 0,
        "signal": {"device_rssi": 65, "hub_rssi": 64},
        "online": True,
    },
}

MOCK_PET_FLAP = {
    "id": 13576,
    "product_id": 3,
    "household_id": HOUSEHOLD_ID,
    "name": "Pet Flap",
    "parent": {"product_id": 1, "id": HUB_ID},
    "status": {
        "battery": 6.4,
        "locking": {"mode": 0},
        "learn_mode": 0,
        "signal": {"device_rssi": 70, "hub_rssi": 65},
        "online": True,
    },
}

MOCK_PET = {
    "id": 24680,
    "household_id": HOUSEHOLD_ID,
    "name": "Pet",
    "tag_id": PET_TAG_ID,
    "position": {
        "since": "2020-08-23T23:10:50",
        "where": 1,
        "device_id": MOCK_PET_FLAP["id"],
        "user_id": 112233,
    },
    "status": {},
}

MOCK_API_DATA = {
    "devices": [MOCK_HUB, MOCK_CAT_FLAP, MOCK_PET_FLAP, MOCK_FEEDER, MOCK_FELAQUA],
    "pets": [MOCK_PET],
}
