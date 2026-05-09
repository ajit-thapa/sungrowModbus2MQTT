# Home Assistant Configuration Examples

Complete `configuration.yaml` examples and automations for Sungrow integration.

## Basic Configuration

### Option 1: Direct Modbus (HA Component)

```yaml
# configuration.yaml

# Sungrow SG10RT integration via custom component
sungrow_sg10rt:
  - host: 192.168.9.106
    port: 502
    slave: 1
```

**Entities created:**
- `sensor.sungrow_total_active_power`
- `sensor.sungrow_daily_yield`
- `sensor.sungrow_total_yield`
- `number.sungrow_export_limit_percent`

### Option 2: MQTT Bridge

```yaml
# configuration.yaml

# MQTT Broker
mqtt:
  broker: 192.168.1.50
  port: 1883
  username: ha_user
  password: your_password
  discovery: true
  discovery_prefix: homeassistant
```

**Entities created automatically** via MQTT discovery:
- `sensor.total_active_power`
- `sensor.daily_yield`
- `sensor.total_yield`
- etc.

### Option 3: Hybrid Setup (Modbus + MQTT)

```yaml
# Use direct Modbus for real-time data
sungrow_sg10rt:
  - host: 192.168.9.106
    port: 502
    slave: 1

# Also publish via MQTT for multi-system access
mqtt:
  broker: 192.168.1.50
  port: 1883
  username: ha_user
  password: your_password
```

---

## Dashboard Configuration

### Energy Management Dashboard

```yaml
# dashboards/solar.yaml (in YAML mode or UI builder)
# Or use Lovelace UI editor

views:
  - title: Solar
    cards:
      - type: grid
        columns: 2
        cards:
          # Current Power
          - type: gauge
            entity: sensor.sungrow_total_active_power
            title: Current Power
            min: 0
            max: 10000
            unit: W
            severity:
              green: 5000
              yellow: 2500
              red: 0

          # Daily Yield
          - type: statistic
            entity: sensor.sungrow_daily_yield
            stat_period: day
            title: Today's Yield
            unit: kWh

          # Temperature
          - type: gauge
            entity: sensor.sungrow_internal_temperature
            title: Inverter Temp
            min: 0
            max: 80
            unit: °C
            severity:
              green: 60
              yellow: 70
              red: 80

          # Grid Frequency
          - type: gauge
            entity: sensor.sungrow_grid_frequency
            title: Grid Frequency
            min: 49
            max: 51
            unit: Hz
            severity:
              green: [49.8, 50.2]
              yellow: [49.5, 50.5]
              red: 0

      # History graph
      - type: history-stats
        entity: sensor.sungrow_total_active_power
        title: Generation Today
        stat_period: day
        state_stat: mean

      # Energy table
      - type: entities
        title: System Stats
        entities:
          - sensor.sungrow_nominal_active_power
          - sensor.sungrow_total_running_time
          - sensor.sungrow_power_factor
```

---

## Sensor Templates

Create derived sensors using template sensors:

```yaml
template:
  - sensor:
      # Monthly yield (requires history_stats)
      - name: "Solar Monthly Yield"
        unique_id: solar_monthly_yield
        unit_of_measurement: "kWh"
        state: >
          {% set entities = [
            'sensor.sungrow_daily_yield'
          ] %}
          {{ entities[0] }}

      # Power generation percentage of max
      - name: "Solar Generation %"
        unique_id: solar_generation_percent
        unit_of_measurement: "%"
        state: >
          {% set power = states('sensor.sungrow_total_active_power') | float(0) %}
          {% set max_power = states('sensor.sungrow_nominal_active_power') | float(10000) %}
          {{ ((power / max_power) * 100) | round(0) }}

      # Average temperature today
      - name: "Solar Avg Temp Today"
        unique_id: solar_avg_temp
        unit_of_measurement: "°C"
        state: >
          {% set temp = states('sensor.sungrow_internal_temperature') | float(0) %}
          {{ temp | round(1) }}

      # Power factor health
      - name: "Power Factor Status"
        unique_id: power_factor_status
        state: >
          {% set pf = states('sensor.sungrow_power_factor') | float(1) %}
          {% if pf >= 0.95 %}
            Excellent
          {% elif pf >= 0.9 %}
            Good
          {% elif pf >= 0.8 %}
            Fair
          {% else %}
            Poor
          {% endif %}
```

---

## Automations

### Dynamic Export Limiting

Limit solar export when grid frequency is high (oversupply):

```yaml
automation:
  - alias: "Limit Solar Export on High Grid Frequency"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_grid_frequency
        above: 50.05
        for:
          minutes: 5
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit_percent
        data:
          value: 50  # Limit to 50% export

  - alias: "Remove Solar Export Limit on Normal Grid"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_grid_frequency
        below: 49.95
        for:
          minutes: 10
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit_percent
        data:
          value: 100  # Full export allowed
```

### Price-Based Curtailment

Limit export during high grid prices:

```yaml
automation:
  - alias: "Reduce Solar Export on High Prices"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        above: 0.40
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit_percent
        data:
          # Set to 10% (minimum is usually 1-10%)
          value: 10

  - alias: "Restore Solar Export on Normal Prices"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price
        below: 0.30
    action:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit_percent
        data:
          value: 100
```

### Inverter Health Monitoring

Alert when inverter temperature too high:

```yaml
automation:
  - alias: "Inverter Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_internal_temperature
        above: 70
    action:
      - service: notify.notify
        data:
          title: "⚠️ Inverter Hot"
          message: >
            Sungrow inverter temperature: 
            {{ states('sensor.sungrow_internal_temperature') }}°C
      
      - service: persistent_notification.create
        data:
          title: "Inverter Temperature Warning"
          message: >
            Temperature: {{ states('sensor.sungrow_internal_temperature') }}°C.
            Check airflow and shading.
          notification_id: inverter_temp

  - alias: "Clear Inverter Temperature Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_internal_temperature
        below: 60
    action:
      - service: persistent_notification.dismiss
        data:
          notification_id: inverter_temp
```

### Daily Statistics

Log daily generation:

```yaml
automation:
  - alias: "Log Daily Solar Generation"
    trigger:
      - platform: time
        at: "23:59:59"
    action:
      - service: logger.log
        data:
          message: >
            Daily generation: {{ states('sensor.sungrow_daily_yield') }} kWh,
            Total yield: {{ states('sensor.sungrow_total_yield') }} kWh
          level: info
```

---

## Scripts

### Reset Daily Yield Counter (manual operation)

```yaml
script:
  reset_solar_daily:
    description: "Reset daily yield (usually automatic at midnight)"
    sequence:
      - service: logger.log
        data:
          message: "Manual daily yield reset"
          level: warning
      - delay:
          seconds: 2
```

### Manual Export Limiting

```yaml
script:
  set_solar_export_limit:
    description: "Set solar export limit percentage"
    fields:
      percentage:
        name: "Export Limit %"
        description: "Limit solar export to this percentage"
        required: true
        example: 50
    sequence:
      - service: number.set_value
        target:
          entity_id: number.sungrow_export_limit_percent
        data:
          value: "{{ percentage }}"
      - service: notify.notify
        data:
          title: "Solar Export Limited"
          message: "Export limit set to {{ percentage }}%"
```

---

## Utility Meter (Energy Dashboard Integration)

Track daily, monthly, yearly generation:

```yaml
utility_meter:
  solar_daily:
    source: sensor.sungrow_daily_yield
    cycle: daily
    name: Solar Daily Consumption

  solar_monthly:
    source: sensor.sungrow_total_yield
    cycle: monthly
    name: Solar Monthly Consumption

  solar_yearly:
    source: sensor.sungrow_total_yield
    cycle: yearly
    name: Solar Yearly Consumption
```

Then in energy dashboard:
- Energy generated: `sensor.sungrow_total_yield`
- Solar devices: Sungrow SG10RT

---

## Notifications

### Telegram/Discord Alerts

```yaml
automation:
  - alias: "Inverter Error Alert"
    trigger:
      - platform: state
        entity_id: sensor.sungrow_inverter_status
        to: "error"
    action:
      - service: notify.telegram
        data:
          title: "⚠️ Inverter Error"
          message: >
            {{ state_attr('sensor.sungrow_inverter_status', 'description') }}
```

### Mobile Push Notifications

```yaml
automation:
  - alias: "High Temperature Push Notification"
    trigger:
      - platform: numeric_state
        entity_id: sensor.sungrow_internal_temperature
        above: 75
    action:
      - service: notify.mobile_app_iphone
        data:
          title: "⚠️ Inverter Hot"
          message: "Temperature: {{ states('sensor.sungrow_internal_temperature') }}°C"
          data:
            group: "inverter_alerts"
            tag: "inverter_temp"
```

---

## Multi-Inverter Setup

If you have multiple Sungrow inverters:

```yaml
# Option 1: Multiple HA components
sungrow_sg10rt:
  - host: 192.168.9.106
    port: 502
    slave: 1
  - host: 192.168.9.107
    port: 502
    slave: 1

# Option 2: Multiple MQTT topics
mqtt:
  sensor:
    # Inverter 1
    - name: "Solar1 Power"
      state_topic: "sungrow1/sg10rt/total_active_power"
      unit_of_measurement: W
      device_class: power

    # Inverter 2
    - name: "Solar2 Power"
      state_topic: "sungrow2/sg10rt/total_active_power"
      unit_of_measurement: W
      device_class: power

  # Combined power template
  template:
    - sensor:
        - name: "Total Solar Power"
          unit_of_measurement: W
          state: >
            {{ (states('sensor.solar1_power') | float(0) +
                states('sensor.solar2_power') | float(0)) | round(0) }}
```

---

## Integration with Energy Dashboard

Home Assistant's built-in Energy dashboard can track:

1. **Solar generation**: `sensor.sungrow_total_yield`
2. **Daily yield**: `sensor.sungrow_daily_yield`
3. **Realtime power**: `sensor.sungrow_total_active_power`

Setup:
1. Settings → Dashboards → Energy
2. Click "Solar production"
3. Select: `sensor.sungrow_total_yield`
4. Now tracks daily, monthly, yearly generation

---

## Lovelace Card Examples

### Apexcharts Power Graph

```yaml
type: custom:apexcharts-card
header:
  title: Solar Generation
series:
  - entity: sensor.sungrow_total_active_power
    name: Power
    type: area
    color: '#ffc107'
    stroke_width: 2
```

### Mini Graph Card

```yaml
type: custom:mini-graph-card
entity: sensor.sungrow_total_active_power
name: Solar Power
unit: W
hours_to_show: 24
aggregate_func: avg
group_by: hour
```

### Button Card with Status

```yaml
type: custom:button-card
entity: number.sungrow_export_limit_percent
name: Export Limit
state:
  - value: 100
    color: green
    label: Unlimited
  - value: 50
    color: orange
    label: 50% Limited
  - value: 10
    color: red
    label: Minimal
```

---

## Performance Tuning

### Reduce Update Frequency

If HA CPU usage is high, reduce sensor update frequency:

```yaml
# In custom component or MQTT:
# Increase scan_interval
scan_interval: 60  # Poll every 60 seconds instead of 10
```

### Disable Unused Sensors

Comment out unused registers in `registers.py`:

```python
# REGISTERS = [
#     Register(5011, "mppt1_voltage", ...),  # Disabled
#     Register(5012, "mppt1_current", ...),  # Disabled
]
```

---

## Backup & Restore

### Automate Configuration Backup

```yaml
automation:
  - alias: "Backup config daily"
    trigger:
      - platform: time
        at: "03:00:00"
    action:
      - service: shell_command.backup_config
```

---

## Advanced: Custom Entities

Create custom entities using REST API calls:

```yaml
rest_command:
  set_solar_export_limit:
    url: "http://192.168.9.106/api/setpower"
    method: POST
    payload: '{"limit": {{ limit }}, "slave": 1}'

automation:
  - alias: "Set limit via REST API"
    trigger: ...
    action:
      - service: rest_command.set_solar_export_limit
        data:
          limit: 5000
```

---

See [SETUP.md](SETUP.md) for installation instructions.
