"""The tests for the Sure Petcare binary sensor platform."""

import pytest
from pytest_homeassistant.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import HOUSEHOLD_ID, HUB_ID

EXPECTED_ENTITY_IDS = {
    "binary_sensor.pet_flap_connectivity": f"{HOUSEHOLD_ID}-13576-connectivity",
    "binary_sensor.cat_flap_connectivity": f"{HOUSEHOLD_ID}-13579-connectivity",
    "binary_sensor.feeder_connectivity": f"{HOUSEHOLD_ID}-12345-connectivity",
    "binary_sensor.pet": f"{HOUSEHOLD_ID}-24680",
    "binary_sensor.hub": f"{HOUSEHOLD_ID}-{HUB_ID}",
    "binary_sensor.cat_flap_curfew": f"{HOUSEHOLD_ID}-13579-curfew",
}

LEARN_MODE_ENTITY_IDS = {
    "binary_sensor.pet_flap_learn_mode": f"{HOUSEHOLD_ID}-13576-learn_mode",
    "binary_sensor.cat_flap_learn_mode": f"{HOUSEHOLD_ID}-13579-learn_mode",
    "binary_sensor.feeder_learn_mode": f"{HOUSEHOLD_ID}-12345-learn_mode",
}


async def test_binary_sensors(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    surepetcare,
    mock_config_entry_setup: MockConfigEntry,
) -> None:
    """Test the generation of unique ids."""
    state_entity_ids = hass.states.async_entity_ids()

    for entity_id, unique_id in EXPECTED_ENTITY_IDS.items():
        assert entity_id in state_entity_ids
        state = hass.states.get(entity_id)
        assert state
        assert state.state == "on"
        entity = entity_registry.async_get(entity_id)
        assert entity.unique_id == unique_id


@pytest.mark.usefixtures("surepetcare", "mock_config_entry_setup")
async def test_learn_mode(
    hass: HomeAssistant, entity_registry: er.EntityRegistry
) -> None:
    """Test learn mode is off and has stable unique ids."""
    for entity_id, unique_id in LEARN_MODE_ENTITY_IDS.items():
        state = hass.states.get(entity_id)
        assert state
        assert state.state == "off"
        entity = entity_registry.async_get(entity_id)
        assert entity
        assert entity.unique_id == unique_id


@pytest.mark.usefixtures("surepetcare", "mock_config_entry_setup")
async def test_curfew_attributes(hass: HomeAssistant) -> None:
    """Test the curfew times are exposed as attributes."""
    state = hass.states.get("binary_sensor.cat_flap_curfew")
    assert state
    assert state.attributes["curfews"] == [
        {"enabled": True, "lock_time": "19:00", "unlock_time": "07:00"}
    ]


@pytest.mark.usefixtures("surepetcare", "mock_config_entry_setup")
async def test_hub_attributes(hass: HomeAssistant) -> None:
    """Test the hub LED and pairing mode attributes."""
    state = hass.states.get("binary_sensor.hub")
    assert state
    assert state.attributes["led_mode"] == 0
    assert state.attributes["pairing_mode"] is False
