# EcoFlow — Home Assistant Custom Integration

Integrates EcoFlow devices into Home Assistant via the official EcoFlow IoT API (HTTP REST + MQTT).

## Supported Devices

| Device | Sensors | Switches | Controls |
|--------|---------|----------|----------|
| **STREAM / BKW** | Solar power, grid power, home load, battery SOC & power, backup reserve | AC1 switch, AC2 switch | Backup reserve level |
| **Delta Pro** | SOC, temperatures, AC/PV/DC power, USB outputs, remaining time | AC output, car charger | Charge limit, discharge limit |
| **Delta 2 / Delta 2 Max** | SOC, temperatures, AC/PV power, USB outputs, remaining time | AC output, car charger | Charge limit, discharge limit |
| **River 2 Pro** | SOC, all output powers, remaining time | AC output | Charge limit, discharge limit |
| **PowerStream** | PV1/PV2 voltage·current·power, battery SOC/temp, inverter output, remaining time | — | Battery limits, custom load power |
| **Smart Plug** | Power, voltage, current, temperature, frequency | Plug on/off | — |
| **PowerOcean** | Solar, battery SOC/power, load, grid, EV charger power | — | — |
| **Smart Meter** | Cloud connection status (Online/Offline) | — | — |

## Installation

### HACS (recommended)
1. In HACS, go to **Integrations** → ⋮ → **Custom repositories**
2. Add this repository URL: `https://github.com/yourdawi/ha-ecoflow` with category **Integration**
3. Search for **EcoFlow** and install

### Manual
1. Copy the `custom_components/ecoflow/` folder into your HA config directory:
   ```
   config/
   └── custom_components/
       └── ecoflow/
           ├── __init__.py
           ├── api.py
           ├── config_flow.py
           ├── const.py
           ├── coordinator.py
           ├── entity_base.py
           ├── manifest.json
           ├── number.py
           ├── sensor.py
           ├── switch.py
           └── translations/
               ├── de.json
               └── en.json
   ```
2. Restart Home Assistant.

## Getting API Credentials

1. Go to the EcoFlow Developer Portal for your region:
   - **Europe:** [https://developer-eu.ecoflow.com](https://developer-eu.ecoflow.com)
   - **Americas / Rest of World:** [https://developer.ecoflow.com/us/](https://developer.ecoflow.com/us/)
2. Log in with your EcoFlow account.
3. Navigate to **Developer Platform** → Create an application.
4. Copy your **Access Key** and **Secret Key**.
5. **Tip:** You can find the correct API host for your account in the portal under **Document** → **General**.

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **EcoFlow**
3. Enter your **Access Key** and **Secret Key**
4. Home Assistant auto-discovers all devices bound to your account

## How it Works

- **HTTP polling** every 30 seconds as baseline (configurable via `UPDATE_INTERVAL` in `const.py`)
- **MQTT push** for real-time updates — quota changes appear instantly without waiting for the next poll
- MQTT credentials are obtained automatically from the EcoFlow API

## Entity Examples

After setup you will find entities like:

| Entity ID | Name | Type |
|-----------|------|------|
| `sensor.stream_solar_power` | STREAM Solar Power | Sensor (W) |
| `sensor.stream_battery_soc` | STREAM Battery SOC | Sensor (%) |
| `sensor.delta_pro_ac_output_power` | Delta Pro AC Output Power | Sensor (W) |
| `switch.delta_pro_ac_output` | Delta Pro AC Output | Switch |
| `number.delta_pro_charge_limit` | Delta Pro Charge Limit | Number (%) |
| `number.stream_backup_reserve_level` | STREAM Backup Reserve Level | Number (%) |
| `switch.smart_plug_plug_switch` | Smart Plug Switch | Switch |
| `sensor.smart_plug_power` | Smart Plug Power | Sensor (W) |

## Automation Example

Turn off AC output when battery drops below 20 %:

```yaml
automation:
  - alias: "EcoFlow: Disable AC when battery low"
    trigger:
      - platform: numeric_state
        entity_id: sensor.delta_pro_battery_soc
        below: 20
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.delta_pro_ac_output
```

## Troubleshooting

| Problem | Solution |
|---------|---------|
| "Cannot connect" during setup | Check internet connection and API host reachability |
| "Invalid auth" | Double-check Access Key and Secret Key on the developer portal |
| Sensors show unavailable | Check HA logs for API errors; device may be offline |
| MQTT not updating | MQTT is optional — HTTP polling still works; check logs for MQTT errors |
| Device not detected | Serial number prefix may be unknown; the integration falls back to Delta Pro sensors |
