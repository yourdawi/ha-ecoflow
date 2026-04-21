"""Constants for the EcoFlow integration."""

DOMAIN = "ecoflow"
MANUFACTURER = "EcoFlow"

# API
API_HOST = "https://api-e.ecoflow.com"
API_DEVICE_LIST = "/iot-open/sign/device/list"
API_QUOTA_ALL = "/iot-open/sign/device/quota/all"
API_QUOTA_SET = "/iot-open/sign/device/quota"
API_QUOTA_GET = "/iot-open/sign/device/quota"
API_CERTIFICATION = "/iot-open/sign/certification"

# Config
CONF_ACCESS_KEY = "access_key"
CONF_SECRET_KEY = "secret_key"
CONF_DEVICE_SN = "device_sn"
CONF_REGION = "region"
CONF_API_HOST = "api_host"

# Regions
API_REGION_EU = "eu"
API_REGION_US = "us"
API_REGION_CUSTOM = "custom"

# Mapping regions to hosts
API_HOSTS = {
    API_REGION_EU: "https://api-e.ecoflow.com",
    API_REGION_US: "https://api-a.ecoflow.com",
}

# Update interval (fallback polling in seconds)
UPDATE_INTERVAL = 30

# Device types (detected from serial number prefix)
DEVICE_DELTA_PRO = "delta_pro"
DEVICE_DELTA_2 = "delta_2"
DEVICE_DELTA_2_MAX = "delta_2_max"
DEVICE_STREAM = "stream"          # BKW / STREAM
DEVICE_POWERSTREAM = "powerstream"
DEVICE_SMART_PLUG = "smart_plug"
DEVICE_RIVER_2_PRO = "river_2_pro"
DEVICE_POWEROCEAN = "powerocean"
DEVICE_SMART_METER = "smart_meter"
DEVICE_UNKNOWN = "unknown"

# Serial number prefix → device type mapping
SN_PREFIX_MAP = {
    "DCAB": DEVICE_DELTA_PRO,
    "DCEB": DEVICE_DELTA_PRO,
    "BJ21": DEVICE_DELTA_2,
    "BZ21": DEVICE_DELTA_2,
    "ZMR21": DEVICE_DELTA_2_MAX,
    "BK1": DEVICE_STREAM,
    "BK3": DEVICE_STREAM,
    "BK4": DEVICE_STREAM,
    "BK5": DEVICE_STREAM,
    "HW51": DEVICE_POWERSTREAM,
    "HW52": DEVICE_SMART_PLUG,
    "R621": DEVICE_RIVER_2_PRO,
    "HJ31": DEVICE_POWEROCEAN,
    "BK2": DEVICE_SMART_METER,
}

# ─── Sensor definitions per device type ─────────────────────────────────────
# Each entry: (quota_key, name, unit, device_class, state_class, icon, factor)
# factor: multiply raw value by this before displaying (e.g. 0.1 for "unit: 0.1 W")
# device_class: HA sensor device class string or None
# state_class: "measurement" | "total_increasing" | "total" | None

from homeassistant.components.sensor import SensorStateClass, SensorDeviceClass  # noqa: E402

SENSORS_DELTA_PRO = [
    # BMS
    ("bmsMaster.soc", "Battery SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.temp", "Battery Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.inputWatts", "Battery Input Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.outputWatts", "Battery Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.maxCellTemp", "Max Cell Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.minCellTemp", "Min Cell Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 1),
    # INV
    ("inv.inputWatts", "AC Charging Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.outputWatts", "AC Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.outTemp", "Inverter Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.cfgAcOutVoltage", "AC Output Voltage", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.cfgAcOutFreq", "AC Output Frequency", "Hz", SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, None, 1),
    # MPPT
    ("mppt.inWatts", "Solar Input Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:solar-power", 1),
    ("mppt.outWatts", "MPPT Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("mppt.carOutWatts", "Car Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("mppt.dcdc12vWatts", "DC 12V Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    # PD
    ("pd.soc", "Display SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.usb1Watts", "USB1 Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.usb2Watts", "USB2 Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.typec1Watts", "USB-C1 Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.typec2Watts", "USB-C2 Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.carWatts", "Car Port Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.chgPowerAc", "AC Total Charged", "Wh", SensorDeviceClass.ENERGY, SensorStateClass.TOTAL_INCREASING, None, 1),
    # EMS
    ("ems.maxChargeSoc", "Charge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-charging-high", 1),
    ("ems.minDsgSoc", "Discharge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-arrow-down", 1),
    ("pd.remainTime", "Remaining Time", "min", None, SensorStateClass.MEASUREMENT, "mdi:timer-outline", 1),
]

SENSORS_DELTA_2 = [
    ("bmsMaster.soc", "Battery SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.temp", "Battery Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.inputWatts", "Battery Input Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("bmsMaster.outputWatts", "Battery Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.inputWatts", "AC Charging Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.outputWatts", "AC Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.outTemp", "Inverter Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 1),
    ("mppt.inWatts", "Solar Input Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:solar-power", 1),
    ("mppt.carOutWatts", "Car Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.soc", "Display SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.usb1Watts", "USB1 Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.typec1Watts", "USB-C Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.remainTime", "Remaining Time", "min", None, SensorStateClass.MEASUREMENT, "mdi:timer-outline", 1),
    ("ems.maxChargeSoc", "Charge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-charging-high", 1),
    ("ems.minDsgSoc", "Discharge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-arrow-down", 1),
]

SENSORS_STREAM = [
    ("powGetPvSum", "Solar Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:solar-power", 1),
    ("gridConnectionPower", "Grid Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:transmission-tower", 1),
    ("powGetSysLoad", "Home Load Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:home-lightning-bolt", 1),
    ("powGetSysGrid", "Grid Import Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:transmission-tower-import", 1),
    ("powGetBpCms", "Battery Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:battery-charging", 1),
    ("cmsBattSoc", "Battery SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("cmsMaxChgSoc", "Charge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-charging-high", 1),
    ("cmsMinDsgSoc", "Discharge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-arrow-down", 1),
    ("backupReverseSoc", "Backup Reserve Level", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-lock", 1),
]

SENSORS_POWERSTREAM = [
    ("20_1.batSoc", "Battery SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("20_1.batTemp", "Battery Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.pv1InputVolt", "PV1 Voltage", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.pv1InputCur", "PV1 Current", "A", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.pv1InputWatts", "PV1 Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:solar-power", 0.1),
    ("20_1.pv2InputVolt", "PV2 Voltage", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.pv2InputCur", "PV2 Current", "A", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.pv2InputWatts", "PV2 Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:solar-power", 0.1),
    ("20_1.invOutputWatts", "Inverter Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.permanentWatts", "Custom Load Power Setting", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.lowerLimit", "Battery Discharge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-arrow-down", 1),
    ("20_1.upperLimit", "Battery Charge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-charging-high", 1),
    ("20_1.invBrightness", "LED Brightness", None, None, SensorStateClass.MEASUREMENT, "mdi:brightness-6", 1),
    ("20_1.ratedPower", "Rated Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 0.1),
    ("20_1.chgRemainTime", "Charge Remaining Time", "min", None, SensorStateClass.MEASUREMENT, "mdi:timer-outline", 1),
    ("20_1.dsgRemainTime", "Discharge Remaining Time", "min", None, SensorStateClass.MEASUREMENT, "mdi:timer-outline", 1),
]

SENSORS_SMART_PLUG = [
    ("2_1.watts", "Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 0.1),
    ("2_1.volt", "Voltage", "V", SensorDeviceClass.VOLTAGE, SensorStateClass.MEASUREMENT, None, 1),
    ("2_1.current", "Current", "A", SensorDeviceClass.CURRENT, SensorStateClass.MEASUREMENT, None, 0.001),
    ("2_1.temp", "Temperature", "°C", SensorDeviceClass.TEMPERATURE, SensorStateClass.MEASUREMENT, None, 1),
    ("2_1.freq", "Frequency", "Hz", SensorDeviceClass.FREQUENCY, SensorStateClass.MEASUREMENT, None, 1),
    ("2_1.errCode", "Error Code", None, None, SensorStateClass.MEASUREMENT, "mdi:alert-circle", 1),
]

SENSORS_RIVER_2_PRO = [
    ("pd.soc", "Battery SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.wattsOutSum", "Total Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.carWatts", "DC Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.usb1Watts", "USB1 Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("pd.typec1Watts", "USB-C Output", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.inputWatts", "AC Input Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("inv.outputWatts", "AC Output Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, None, 1),
    ("mppt.inWatts", "Solar Input Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:solar-power", 1),
    ("bms_emsStatus.dsgRemainTime", "Discharge Remaining Time", "min", None, SensorStateClass.MEASUREMENT, "mdi:timer-outline", 1),
    ("bms_bmsStatus.remainTime", "Charge Remaining Time", "min", None, SensorStateClass.MEASUREMENT, "mdi:timer-outline", 1),
    ("bms_emsStatus.maxChargeSoc", "Charge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-charging-high", 1),
    ("bms_emsStatus.minDsgSoc", "Discharge Limit", "%", None, SensorStateClass.MEASUREMENT, "mdi:battery-arrow-down", 1),
]

SENSORS_POWEROCEAN = [
    ("mpptPwr", "Solar Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:solar-power", 1),
    ("bpSoc", "Battery SOC", "%", SensorDeviceClass.BATTERY, SensorStateClass.MEASUREMENT, None, 1),
    ("bpPwr", "Battery Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:battery-charging", 1),
    ("sysLoadPwr", "Load Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:home-lightning-bolt", 1),
    ("sysGridPwr", "Grid Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:transmission-tower", 1),
    ("evPwr", "EV Charger Power", "W", SensorDeviceClass.POWER, SensorStateClass.MEASUREMENT, "mdi:ev-station", 1),
]

SENSORS_SMART_METER = []

BINARY_SENSORS_COMMON = [
    ("online", "Cloud Status", "connectivity", "mdi:cloud-check"),
]

# Sensors by device type
DEVICE_SENSORS = {
    DEVICE_DELTA_PRO: SENSORS_DELTA_PRO,
    DEVICE_DELTA_2: SENSORS_DELTA_2,
    DEVICE_DELTA_2_MAX: SENSORS_DELTA_2,
    DEVICE_STREAM: SENSORS_STREAM,
    DEVICE_POWERSTREAM: SENSORS_POWERSTREAM,
    DEVICE_SMART_PLUG: SENSORS_SMART_PLUG,
    DEVICE_RIVER_2_PRO: SENSORS_RIVER_2_PRO,
    DEVICE_POWEROCEAN: SENSORS_POWEROCEAN,
    DEVICE_SMART_METER: SENSORS_SMART_METER,
    DEVICE_UNKNOWN: SENSORS_DELTA_PRO,  # fallback
}

DEVICE_BINARY_SENSORS = {
    DEVICE_DELTA_PRO: BINARY_SENSORS_COMMON,
    DEVICE_DELTA_2: BINARY_SENSORS_COMMON,
    DEVICE_DELTA_2_MAX: BINARY_SENSORS_COMMON,
    DEVICE_STREAM: BINARY_SENSORS_COMMON,
    DEVICE_POWERSTREAM: BINARY_SENSORS_COMMON,
    DEVICE_SMART_PLUG: BINARY_SENSORS_COMMON,
    DEVICE_RIVER_2_PRO: BINARY_SENSORS_COMMON,
    DEVICE_POWEROCEAN: BINARY_SENSORS_COMMON,
    DEVICE_SMART_METER: BINARY_SENSORS_COMMON,
    DEVICE_UNKNOWN: BINARY_SENSORS_COMMON,
}

# ─── Switch definitions ──────────────────────────────────────────────────────
# (quota_key, name, icon, set_params_fn)
# set_params_fn(value: bool) → dict to send as params

def _delta_pro_ac_switch(enabled: bool) -> dict:
    return {"cmdSet": 32, "id": 66, "enabled": 1 if enabled else 0}

def _delta_pro_car_switch(enabled: bool) -> dict:
    return {"cmdSet": 32, "id": 81, "enabled": 1 if enabled else 0}

def _powerstream_inv_switch(enabled: bool) -> dict:
    return {"cmdCode": "WN511_SET_SUPPLY_PRIORITY_PACK", "supplyPriority": 0 if enabled else 1}

def _smart_plug_switch(enabled: bool) -> dict:
    return {"cmdCode": "WN511_SOCKET_SET_PLUG_SWITCH_MESSAGE", "plugSwitch": 1 if enabled else 0}

def _stream_ac1_switch(enabled: bool) -> dict:
    return {"cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2,
            "needAck": True, "params": {"cfgRelay2Onoff": enabled}}

def _stream_ac2_switch(enabled: bool) -> dict:
    return {"cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2,
            "needAck": True, "params": {"cfgRelay3Onoff": enabled}}

SWITCHES_DELTA_PRO = [
    ("inv.cfgAcEnabled", "AC Output", "mdi:power-plug", _delta_pro_ac_switch),
    ("mppt.carState", "Car Charger Output", "mdi:car", _delta_pro_car_switch),
]

SWITCHES_STREAM = [
    ("relay2Onoff", "AC1 Switch", "mdi:power-plug", _stream_ac1_switch),
    ("relay3Onoff", "AC2 Switch", "mdi:power-plug", _stream_ac2_switch),
]

SWITCHES_SMART_PLUG = [
    ("2_1.switchSta", "Plug Switch", "mdi:power-plug", _smart_plug_switch),
]

DEVICE_SWITCHES = {
    DEVICE_DELTA_PRO: SWITCHES_DELTA_PRO,
    DEVICE_DELTA_2: SWITCHES_DELTA_PRO,
    DEVICE_DELTA_2_MAX: SWITCHES_DELTA_PRO,
    DEVICE_STREAM: SWITCHES_STREAM,
    DEVICE_SMART_PLUG: SWITCHES_SMART_PLUG,
    DEVICE_RIVER_2_PRO: SWITCHES_DELTA_PRO,
    DEVICE_POWERSTREAM: [],
    DEVICE_POWEROCEAN: [],
    DEVICE_SMART_METER: [],
    DEVICE_UNKNOWN: [],
}

# ─── Number (slider) definitions ────────────────────────────────────────────
# (quota_key, name, unit, min_val, max_val, step, icon, set_params_fn)

def _delta_pro_charge_limit(value: int) -> dict:
    return {"cmdSet": 32, "id": 49, "maxChgSoc": value}

def _delta_pro_discharge_limit(value: int) -> dict:
    return {"cmdSet": 32, "id": 51, "minDsgSoc": value}

def _powerstream_lower_limit(value: int) -> dict:
    return {"cmdCode": "WN511_SET_BAT_LOWER_PACK", "lowerLimit": value}

def _powerstream_upper_limit(value: int) -> dict:
    return {"cmdCode": "WN511_SET_BAT_UPPER_PACK", "upperLimit": value}

def _powerstream_perm_watts(value: int) -> dict:
    return {"cmdCode": "WN511_SET_PERMANENT_WATTS_PACK", "permanentWatts": value}

def _stream_backup_soc(value: int) -> dict:
    return {"cmdId": 17, "cmdFunc": 254, "dirDest": 1, "dirSrc": 1, "dest": 2,
            "needAck": True, "params": {"cfgBackupReverseSoc": value}}

NUMBERS_DELTA_PRO = [
    ("ems.maxChargeSoc", "Charge Limit", "%", 50, 100, 1, "mdi:battery-charging-high", _delta_pro_charge_limit),
    ("ems.minDsgSoc", "Discharge Limit", "%", 0, 30, 1, "mdi:battery-arrow-down", _delta_pro_discharge_limit),
]

NUMBERS_POWERSTREAM = [
    ("20_1.lowerLimit", "Battery Discharge Limit", "%", 1, 30, 1, "mdi:battery-arrow-down", _powerstream_lower_limit),
    ("20_1.upperLimit", "Battery Charge Limit", "%", 70, 100, 1, "mdi:battery-charging-high", _powerstream_upper_limit),
    ("20_1.permanentWatts", "Custom Load Power", "W", 0, 600, 1, "mdi:flash", _powerstream_perm_watts),
]

NUMBERS_STREAM = [
    ("backupReverseSoc", "Backup Reserve Level", "%", 3, 95, 1, "mdi:battery-lock", _stream_backup_soc),
]

DEVICE_NUMBERS = {
    DEVICE_DELTA_PRO: NUMBERS_DELTA_PRO,
    DEVICE_DELTA_2: NUMBERS_DELTA_PRO,
    DEVICE_DELTA_2_MAX: NUMBERS_DELTA_PRO,
    DEVICE_STREAM: NUMBERS_STREAM,
    DEVICE_POWERSTREAM: NUMBERS_POWERSTREAM,
    DEVICE_SMART_PLUG: [],
    DEVICE_RIVER_2_PRO: NUMBERS_DELTA_PRO,
    DEVICE_POWEROCEAN: [],
    DEVICE_SMART_METER: [],
    DEVICE_UNKNOWN: [],
}
