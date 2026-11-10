"""Test the surepetcare sensor platform."""

import pytest
from pytest_homeassistant.common import MockConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntryDisabler

from . import HOUSEHOLD_ID, MOCK_FELAQUA, MOCK_PET, UNKNOWN_TAG_ID

EXPECTED_ENTITIES = (
    ("sensor.pet_flap_battery_level", f"{HOUSEHOLD_ID}-13576-battery", "100"),
    ("sensor.cat_flap_battery_level", f"{HOUSEHOLD_ID}-13579-battery", "100"),
    ("sensor.feeder_battery_level", f"{HOUSEHOLD_ID}-12345-battery", "100"),
    (
        "sensor.felaqua_battery_level",
        f"{HOUSEHOLD_ID}-{MOCK_FELAQUA['id']}-battery",
        "100",
    ),
    (
        "sensor.pet_last_seen_flap_device_id",
        f"{HOUSEHOLD_ID}-24680-last_seen_flap_device",
        str(MOCK_PET["position"]["device_id"]),
    ),
    (
        "sensor.pet_last_seen_user_id",
        f"{HOUSEHOLD_ID}-24680-last_seen_user",
        str(MOCK_PET["position"]["user_id"]),
    ),
    (
        "sensor.pet_last_feeding",
        f"{HOUSEHOLD_ID}-24680-last_feeding",
        "2026-11-03T08:07:32+00:00",
    ),
    ("sensor.feeder_training_mode", f"{HOUSEHOLD_ID}-12345-training_mode", "step_2"),
    ("sensor.feeder_lid_close_delay", f"{HOUSEHOLD_ID}-12345-lid_close_delay", "4"),
    ("sensor.feeder_registered_pets", f"{HOUSEHOLD_ID}-12345-registered_pets", "1"),
    ("sensor.cat_flap_registered_pets", f"{HOUSEHOLD_ID}-13579-registered_pets", "2"),
    ("sensor.pet_flap_registered_pets", f"{HOUSEHOLD_ID}-13576-registered_pets", "0"),
    (
        "sensor.felaqua_registered_pets",
        f"{HOUSEHOLD_ID}-{MOCK_FELAQUA['id']}-registered_pets",
        "0",
    ),
)

DEFAULT_DISABLED_ENTITIES = [
    "sensor.pet_last_seen_flap_device_id",
    "sensor.pet_last_seen_user_id",
]


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensors(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    surepetcare,
    mock_config_entry_setup: MockConfigEntry,
) -> None:
    """Test the generation of unique ids and sensor states."""
    state_entity_ids = hass.states.async_entity_ids()

    for entity_id, unique_id, expected_state in EXPECTED_ENTITIES:
        assert entity_id in state_entity_ids
        state = hass.states.get(entity_id)
        assert state
        assert state.state == expected_state
        entity = entity_registry.async_get(entity_id)
        assert entity.unique_id == unique_id


async def test_default_disabled_sensors(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    surepetcare,
    mock_config_entry_setup: MockConfigEntry,
) -> None:
    """Test sensor entities that are disabled by default."""
    for entity_id in DEFAULT_DISABLED_ENTITIES:
        entity = entity_registry.async_get(entity_id)
        assert entity
        assert entity.disabled_by == RegistryEntryDisabler.INTEGRATION
        assert not hass.states.get(entity_id)


@pytest.mark.usefixtures("surepetcare", "mock_config_entry_setup")
async def test_registered_pets_attributes(hass: HomeAssistant) -> None:
    """Test registered pet names, with the tag id for tags without a known pet."""
    feeder = hass.states.get("sensor.feeder_registered_pets")
    assert feeder
    assert feeder.attributes["pets"] == ["Pet"]
    assert "indoor_only" not in feeder.attributes

    flap = hass.states.get("sensor.cat_flap_registered_pets")
    assert flap
    assert flap.attributes["pets"] == ["Pet", str(UNKNOWN_TAG_ID)]
    assert flap.attributes["indoor_only"] == [str(UNKNOWN_TAG_ID)]


@pytest.mark.usefixtures("surepetcare", "mock_config_entry_setup")
async def test_last_feeding_attributes(hass: HomeAssistant) -> None:
    """Test the last feeding names the feeder and keeps the per-bowl change."""
    state = hass.states.get("sensor.pet_last_feeding")
    assert state
    assert state.attributes["feeder"] == "Feeder"
    assert state.attributes["change"] == [-11.15, 0.06]
