"""Support for Sure PetCare Flaps/Pets sensors."""

from typing import cast, override

from surepy.entities import SurepyEntity
from surepy.entities.devices import (
    Feeder as SurepyFeeder,
    Felaqua as SurepyFelaqua,
    Flap as SurepyFlap,
    SurepyDevice,
)
from surepy.entities.pet import Pet as SurepyPet
from surepy.enums import EntityType

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import (
    ATTR_VOLTAGE,
    PERCENTAGE,
    EntityCategory,
    UnitOfTime,
    UnitOfVolume,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import SURE_BATT_VOLTAGE_DIFF, SURE_BATT_VOLTAGE_LOW
from .coordinator import SurePetcareConfigEntry, SurePetcareDataCoordinator
from .entity import SurePetcareEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SurePetcareConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Sure PetCare Flaps sensors."""

    entities: list[SurePetcareEntity] = []

    coordinator = entry.runtime_data

    for surepy_entity in coordinator.data.values():
        if surepy_entity.type in [
            EntityType.CAT_FLAP,
            EntityType.PET_FLAP,
            EntityType.FEEDER,
            EntityType.FELAQUA,
        ]:
            entities.append(SureBattery(surepy_entity.id, coordinator))
            entities.append(RegisteredPets(surepy_entity.id, coordinator))

        if surepy_entity.type in [EntityType.FEEDER, EntityType.FEEDER_LITE]:
            entities.append(FeederTrainingMode(surepy_entity.id, coordinator))
            entities.append(FeederLidCloseDelay(surepy_entity.id, coordinator))

        if surepy_entity.type == EntityType.FELAQUA:
            entities.append(Felaqua(surepy_entity.id, coordinator))
        if surepy_entity.type == EntityType.PET:
            entities.append(PetLastSeenFlapDevice(surepy_entity.id, coordinator))
            entities.append(PetLastSeenUser(surepy_entity.id, coordinator))

    async_add_entities(entities)


class SureBattery(SurePetcareEntity, SensorEntity):
    """A sensor implementation for Sure Petcare batteries."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = PERCENTAGE

    def __init__(
        self, surepetcare_id: int, coordinator: SurePetcareDataCoordinator
    ) -> None:
        """Initialize a Sure Petcare battery sensor."""
        super().__init__(surepetcare_id, coordinator)

        self._attr_name = f"{self._device_name} Battery Level"
        self._attr_unique_id = f"{self._device_id}-battery"

    @callback
    @override
    def _update_attr(self, surepy_entity: SurepyEntity) -> None:
        """Update the state and attributes."""
        state = surepy_entity.raw_data()["status"]

        try:
            per_battery_voltage = state["battery"] / 4
            voltage_diff = per_battery_voltage - SURE_BATT_VOLTAGE_LOW
            self._attr_native_value = max(
                0, min(int(voltage_diff / SURE_BATT_VOLTAGE_DIFF * 100), 100)
            )
        except KeyError, TypeError:
            self._attr_native_value = None

        if state:
            voltage_per_battery = float(state["battery"]) / 4
            self._attr_extra_state_attributes = {
                ATTR_VOLTAGE: f"{float(state['battery']):.2f}",
                f"{ATTR_VOLTAGE}_per_battery": f"{voltage_per_battery:.2f}",
            }
        else:
            self._attr_extra_state_attributes = {}


class Felaqua(SurePetcareEntity, SensorEntity):
    """Sure Petcare Felaqua."""

    _attr_device_class = SensorDeviceClass.VOLUME
    _attr_native_unit_of_measurement = UnitOfVolume.MILLILITERS

    def __init__(
        self, surepetcare_id: int, coordinator: SurePetcareDataCoordinator
    ) -> None:
        """Initialize a Sure Petcare Felaqua sensor."""
        super().__init__(surepetcare_id, coordinator)

        surepy_entity = cast(SurepyFelaqua, coordinator.data[surepetcare_id])

        self._attr_name = self._device_name
        self._attr_unique_id = self._device_id
        self._attr_entity_picture = surepy_entity.icon

    @callback
    @override
    def _update_attr(self, surepy_entity: SurepyEntity) -> None:
        """Update the state."""
        surepy_entity = cast(SurepyFelaqua, surepy_entity)
        self._attr_native_value = surepy_entity.water_remaining


class PetLastSeenFlapDevice(SurePetcareEntity, SensorEntity):
    """Sensor for the last flap device id used by the pet.

    Note: Will be unknown if the last status is not from a flap update.
    """

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(
        self, surepetcare_id: int, coordinator: SurePetcareDataCoordinator
    ) -> None:
        """Initialize last seen flap device id sensor."""
        super().__init__(surepetcare_id, coordinator)

        self._attr_name = f"{self._device_name} Last seen flap device id"
        self._attr_unique_id = f"{self._device_id}-last_seen_flap_device"

    @callback
    @override
    def _update_attr(self, surepy_entity: SurepyEntity) -> None:
        surepy_entity = cast(SurepyPet, surepy_entity)
        position = surepy_entity._data.get("position", {})  # noqa: SLF001
        device_id = position.get("device_id")
        self._attr_native_value = str(device_id) if device_id is not None else None


class PetLastSeenUser(SurePetcareEntity, SensorEntity):
    """Sensor for the last user id that manually changed the pet location.

    Note: Will be unknown if the last status is not from a manual update.
    """

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(
        self, surepetcare_id: int, coordinator: SurePetcareDataCoordinator
    ) -> None:
        """Initialize last seen user id sensor."""
        super().__init__(surepetcare_id, coordinator)

        self._attr_name = f"{self._device_name} Last seen user id"
        self._attr_unique_id = f"{self._device_id}-last_seen_user"

    @callback
    @override
    def _update_attr(self, surepy_entity: SurepyEntity) -> None:
        surepy_entity = cast(SurepyPet, surepy_entity)
        position = surepy_entity._data.get("position", {})  # noqa: SLF001
        user_id = position.get("user_id")
        self._attr_native_value = str(user_id) if user_id is not None else None


TRAINING_MODE_OPTIONS = ["off", "step_1", "step_2", "step_3", "step_4"]
INDOOR_ONLY_PROFILE = 3


class FeederTrainingMode(SurePetcareEntity, SensorEntity):
    """Lid training step of a feeder."""

    _attr_has_entity_name = True
    _attr_translation_key = "training_mode"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = TRAINING_MODE_OPTIONS

    def __init__(
        self, surepetcare_id: int, coordinator: SurePetcareDataCoordinator
    ) -> None:
        """Initialize a Sure Petcare feeder training mode sensor."""
        super().__init__(surepetcare_id, coordinator)
        self._attr_unique_id = f"{self._device_id}-training_mode"

    @callback
    @override
    def _update_attr(self, surepy_entity: SurepyEntity) -> None:
        mode = cast(SurepyFeeder, surepy_entity).training_mode
        if mode is None or not 0 <= mode < len(TRAINING_MODE_OPTIONS):
            self._attr_native_value = None
        else:
            self._attr_native_value = TRAINING_MODE_OPTIONS[mode]


class FeederLidCloseDelay(SurePetcareEntity, SensorEntity):
    """Seconds a feeder's lid stays open after the pet leaves."""

    _attr_has_entity_name = True
    _attr_translation_key = "lid_close_delay"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_suggested_display_precision = 0

    def __init__(
        self, surepetcare_id: int, coordinator: SurePetcareDataCoordinator
    ) -> None:
        """Initialize a Sure Petcare feeder lid close delay sensor."""
        super().__init__(surepetcare_id, coordinator)
        self._attr_unique_id = f"{self._device_id}-lid_close_delay"

    @callback
    @override
    def _update_attr(self, surepy_entity: SurepyEntity) -> None:
        self._attr_native_value = cast(SurepyFeeder, surepy_entity).lid_close_delay


class RegisteredPets(SurePetcareEntity, SensorEntity):
    """Number of pets registered to a device, with their names as attributes."""

    _attr_has_entity_name = True
    _attr_translation_key = "registered_pets"

    def __init__(
        self, surepetcare_id: int, coordinator: SurePetcareDataCoordinator
    ) -> None:
        """Initialize a Sure Petcare registered pets sensor."""
        super().__init__(surepetcare_id, coordinator)
        self._attr_unique_id = f"{self._device_id}-registered_pets"

    @callback
    @override
    def _update_attr(self, surepy_entity: SurepyEntity) -> None:
        device = cast(SurepyDevice, surepy_entity)
        pets_by_tag = {
            pet.tag_id: pet.name
            for pet in self.coordinator.data.values()
            if isinstance(pet, SurepyPet) and pet.tag_id is not None
        }
        tags = list(device.tags.values())
        self._attr_native_value = len(tags)
        self._attr_extra_state_attributes = {
            "pets": [pets_by_tag.get(tag.id, str(tag.id)) for tag in tags]
        }
        if isinstance(device, SurepyFlap):
            self._attr_extra_state_attributes["indoor_only"] = [
                pets_by_tag.get(tag.id, str(tag.id))
                for tag in tags
                if tag.profile() == INDOOR_ONLY_PROFILE
            ]
