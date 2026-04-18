{
  "part_number": "EXAMPLE_SENSOR_NODE",
  "vendor": "generic",
  "class": "sensor_node",
  "core": {
    "arch": "cortex-m",
    "frequency_mhz": 100
  },
  "memory": {
    "flash_kb": 256,
    "ram_kb": 64
  },
  "peripherals": [
    {
      "name": "adc0",
      "type": "adc",
      "channels": [0, 1]
    },
    {
      "name": "uart0",
      "type": "uart",
      "baud_rates": [115200]
    },
    {
      "name": "gpio",
      "type": "gpio",
      "pins": ["LED_STATUS"]
    }
  ],
  "constraints": {
    "max_temp_c": 85,
    "recommended_sample_hz": 10
  }
}
