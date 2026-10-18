"""Behaviour tests for the AccessBridge Home Assistant blueprints.

Runs a real Home Assistant core (pytest-homeassistant-custom-component) with
the blueprints from ../automations and mocked lock/logbook/system_log
services. See integrations/home-assistant/README.md for how to run.
"""

import asyncio
from datetime import timedelta
import pathlib
import shutil

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
import homeassistant.util.dt as dt_util
from pytest_homeassistant_custom_component.common import (
    async_fire_time_changed,
    async_mock_service,
)

BLUEPRINTS = pathlib.Path(__file__).resolve().parents[1] / "automations"

COUNTER = "sensor.accessbridge_relay_pulses"
CONTACT = "binary_sensor.accessbridge_relay_contact"
LOCK = "lock.front_door"
ENABLE = "input_boolean.accessbridge_unlatch_enabled"
DOOR = "binary_sensor.accessbridge_door_closed"
BELL = "sensor.accessbridge_doorbell_pulses"


@pytest.fixture
async def env(hass: HomeAssistant, tmp_path):
    hass.config.config_dir = str(tmp_path)
    dest = tmp_path / "blueprints" / "automation" / "accessbridge"
    dest.mkdir(parents=True)
    for f in BLUEPRINTS.glob("*.yaml"):
        shutil.copy(f, dest / f.name)

    calls = {
        "open": async_mock_service(hass, "lock", "open"),
        "unlock": async_mock_service(hass, "lock", "unlock"),
        "logbook": async_mock_service(hass, "logbook", "log"),
        "syslog": async_mock_service(hass, "system_log", "write"),
        "notify": async_mock_service(hass, "notify", "test"),
    }
    hass.states.async_set(COUNTER, "0")
    hass.states.async_set(CONTACT, "off")
    hass.states.async_set(LOCK, "locked")
    hass.states.async_set(ENABLE, "on")
    hass.states.async_set(DOOR, "on")
    hass.states.async_set(BELL, "0")
    return calls


async def setup_unlock(hass, **extra):
    inputs = {
        "pulse_counter": COUNTER,
        "relay_contact": CONTACT,
        "lock_entity": LOCK,
        "enable_entity": ENABLE,
        "door_entity": DOOR,
    }
    inputs.update(extra)
    assert await async_setup_component(
        hass,
        "automation",
        {"automation": {"id": "unlock", "alias": "unlock",
                        "use_blueprint": {"path": "accessbridge/nuki-unlock.yaml", "input": inputs}}},
    )
    await hass.async_block_till_done()


async def settle(hass):
    """Let triggered automations run without waiting for their timeouts
    (async_block_till_done would wait for wait_for_trigger to time out)."""
    for _ in range(50):
        await asyncio.sleep(0)


async def pulse(hass, value, contact="on"):
    hass.states.async_set(CONTACT, contact)
    hass.states.async_set(COUNTER, str(value))
    await settle(hass)


def messages(calls):
    return [c.data.get("message", "") for c in calls]


async def finish_wait(hass, freezer, seconds=20):
    """Advance time so pending wait_for_trigger timeouts expire."""
    freezer.tick(timedelta(seconds=seconds))
    async_fire_time_changed(hass, dt_util.utcnow(), fire_all=True)
    await settle(hass)


async def test_new_pulse_unlatches_and_confirms(hass, env):
    await setup_unlock(hass)
    await pulse(hass, 1)
    assert len(env["open"]) == 1
    assert env["open"][0].data["entity_id"] == [LOCK]
    hass.states.async_set(LOCK, "opening")
    await settle(hass)
    assert any("confirmed" in m for m in messages(env["logbook"]))
    assert not env["syslog"]


async def test_restored_state_is_ignored(hass, env):
    await setup_unlock(hass)
    hass.states.async_set(COUNTER, "unavailable")
    await settle(hass)
    await pulse(hass, 7)
    assert not env["open"]


async def test_device_reboot_is_ignored_silently(hass, env):
    hass.states.async_set(COUNTER, "5")
    await setup_unlock(hass)
    await pulse(hass, 0)
    assert not env["open"]
    assert not env["syslog"]
    # a real pulse right after the reboot still works (no cooldown started)
    await pulse(hass, 0, contact="off")
    await pulse(hass, 1)
    assert len(env["open"]) == 1


async def test_jump_of_more_than_one_is_rejected(hass, env):
    await setup_unlock(hass)
    await pulse(hass, 3)
    assert not env["open"]
    assert any("jumped" in m for m in messages(env["syslog"]))


async def test_stale_pulse_is_rejected(hass, env, freezer):
    await setup_unlock(hass)
    hass.states.async_set(CONTACT, "off")
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=120))
    hass.states.async_set(COUNTER, "1")  # contact unchanged for 120 s
    await settle(hass)
    assert not env["open"]
    assert any("not closed within" in m for m in messages(env["syslog"]))


async def test_cooldown_suppresses_repeats(hass, env, freezer):
    await setup_unlock(hass)
    await pulse(hass, 1)
    hass.states.async_set(LOCK, "opening")
    await settle(hass)
    assert len(env["open"]) == 1
    freezer.tick(timedelta(seconds=3))
    await pulse(hass, 1, contact="off")
    await pulse(hass, 2)
    assert len(env["open"]) == 1
    assert any("cooldown" in m for m in messages(env["logbook"]))
    freezer.tick(timedelta(seconds=15))
    await pulse(hass, 2, contact="off")
    await pulse(hass, 3)
    assert len(env["open"]) == 2


async def test_disabled_switch_blocks(hass, env):
    hass.states.async_set(ENABLE, "off")
    await setup_unlock(hass)
    await pulse(hass, 1)
    assert not env["open"]
    assert any("disabled" in m for m in messages(env["logbook"]))


async def test_open_door_blocks(hass, env):
    hass.states.async_set(DOOR, "off")
    await setup_unlock(hass)
    await pulse(hass, 1)
    assert not env["open"]
    assert any("door already open" in m for m in messages(env["logbook"]))


async def test_unconfirmed_unlatch_is_logged_as_error(hass, env, freezer):
    await setup_unlock(hass)
    await pulse(hass, 1)
    assert len(env["open"]) == 1
    await finish_wait(hass, freezer, 20)
    errors = [c for c in env["syslog"] if c.data.get("level") == "error"]
    assert errors and "FAILED" in errors[0].data["message"]


async def test_unlock_only_mode(hass, env):
    await setup_unlock(hass, lock_action="lock.unlock")
    await pulse(hass, 1)
    assert len(env["unlock"]) == 1
    assert not env["open"]


async def test_contact_state_alone_never_unlatches(hass, env):
    await setup_unlock(hass)
    for state in ("on", "off", "on", "unavailable", "on"):
        hass.states.async_set(CONTACT, state)
        await settle(hass)
    assert not env["open"]


async def test_doorbell_notifies_once_per_press(hass, env, freezer):
    assert await async_setup_component(
        hass,
        "automation",
        {"automation": {"id": "bell", "alias": "bell", "use_blueprint": {
            "path": "accessbridge/doorbell-notify.yaml",
            "input": {"pulse_counter": BELL,
                      "notify_actions": [{"action": "notify.test", "data": {"message": "ding"}}]}}}},
    )
    await hass.async_block_till_done()
    hass.states.async_set(BELL, "1")
    await settle(hass)
    assert len(env["notify"]) == 1
    freezer.tick(timedelta(seconds=5))
    hass.states.async_set(BELL, "2")  # within rate limit
    await hass.async_block_till_done()
    assert len(env["notify"]) == 1
    hass.states.async_set(BELL, "unavailable")
    await settle(hass)
    freezer.tick(timedelta(seconds=60))
    hass.states.async_set(BELL, "3")  # restore, not a press
    await hass.async_block_till_done()
    assert len(env["notify"]) == 1
    assert not env["open"]
