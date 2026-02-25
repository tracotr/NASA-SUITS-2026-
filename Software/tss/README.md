To run this:
1. Set up the local [NASA TSS Server](https://github.com/SUITS-Techteam/TSS2026/tree/main)   
    a. After running and loading into the website, start the simulations.   
2. Run the appropriate script (```.sh``` for mac, ```.bat``` for windows)

3. Reference ```example.html``` for connecting to the websockets.   

Let Jaxon know if anything is wrong/need help :)

## Websocket Info

Base Websocket URL: ```ws://localhost:8000/ws/{category}```
    
Default Response Structure:
| Data Name | Type|
| ----------------------------- | ----- |
|data | JSON|
|timestamp | UNIX Timestamp as integer |

## EVA1 and EVA2:    
### Telemetry Endpoint: ```eva1:telemetry```, ```eva2:telemetry```

| Data Name | Type|
| ----------------------------- | ----- |
|```primary_battery_level```    | Float |
|```secondary_battery_level```| Float|
|```oxy_pri_storage```| Float|
|```oxy_sec_storage```| Float|
|```oxy_pri_pressure```| Float|
|```oxy_sec_pressure``` | Float|
|```suit_pressure_oxy``` | Float|
|```suit_pressure_co2``` | Float|
|```suit_pressure_other```| Float|
|```suit_pressure_total``` | Float|
|```helmet_pressure_co2``` | Float|
|```fan_pri_rpm``` | Integer|
|```fan_sec_rpm``` | Integer|
|```scrubber_a_co2_storage``` | Float|
|```scrubber_b_co2_storage```  | Float|
|```temperature``` | Float|
|```coolant_storage``` | Float|
|```coolant_gas_pressure``` | Float|
|```coolant_liquid_pressure``` | Float|
|```heart_rate``` | Float|
|```oxy_consumption``` | Float|
|```co2_production```| Float|
|```eva_elapsed_time``` | Integer|

### DCU Endpoint: ```eva1:dcu```, ```eva2:dcu```
| Data Name | Type|
| ----------------------------- | ----- |
|```oxy``` |Boolean|
|```fan``` |Boolean|
|```pump```| Boolean|
|```co2```| Boolean|
|```batt``` | Object|
|    ```batt.lu``` | Boolean|
|    ```batt.ps```| Boolean|

### IMU Endpoint: ```eva1:imu```, ```eva2:imu```

| Data Name | Type|
| ----------------------------- | ----- |
|```posx``` | Float|
|```posy``` | Float|
|```heading``` | Float|


## Global
### Eva Started Endpoint: ```eva:status```

| Data Name | Type|
| ----------------------------- | ----- |
|```started``` | Boolean|

### Errors Endpoint: ```eva:error```

| Data Name | Type|
| ----------------------------- | ----- |
|```fan_error``` | Boolean|
|```oxy_error``` | Boolean|
|```power_error``` | Boolean|
|```scrubber_error``` |Boolean|

### UIA Endpoint: ```eva:uia```

| Data Name | Type|
| ----------------------------- | ----- |
|```eva1_power``` |Boolean
|```eva1_oxy``` | Boolean
|```eva1_water_supply``` | Boolean
|```eva1_water_waste``` | Boolean
|```eva2_power``` | Boolean
|```eva2_oxy``` | Boolean
|```eva2_water_supply``` | Boolean
|```eva2_water_waste``` | Boolean
|```oxy_vent``` | Boolean
|```depress``` |Boolean



## LTV    
### Location Endpoint: ```ltv:location```

| Data Name | Type|
| ----------------------------- | ----- |
| ```last_known_x``` |  Float|
| ```last_known_y``` | Float|

### Signal Endpoint: ```ltv:signal```

| Data Name | Type|
| ----------------------------- | ----- |
| ```strength```  |  Integer|
| ```pings_left```  |  Integer|
| ```ping_requested```  |  Boolean|

### Errors Endpoint: ```ltv:errors```

| Data Name | Type|
| ----------------------------- | ----- |
|``` recovery_mode```  | Boolean|
|``` dust_sensor```  | Boolean|
|``` power_distribution```  |Boolean|
|``` nav_system```  | Boolean|
|``` electronic_heater```  | Boolean|
|``` comms```  | Boolean|
|``` fuse```  |Boolean|

## Rover

### Telemetry Endpoint ```rover:pr_telemetry```

| Data Name | Type|
| ----------------------------- | ----- |
|```cabin_heating``` |Boolean|
|```cabin_cooling``` | Boolean|
|```co2_scrubber``` |Boolean|
|```lights_on``` |Boolean|
|```brakes``` | Boolean|
|```throttle``` | Integer|
|```steering```| Integer|
|```rover_pos_x``` | Float|
|```rover_pos_y```|Float|
|```rover_pos_z```| Float|
|```heading``` | Float|
|```pitch``` |Float|
|```roll``` | Float|
|```distance_traveled``` | Float|
|```speed``` | Float|
|```sunlight```|Float|
|```surface_incline``` | Float|
|```lidar``` | Array[Float]|
|```oxygen_tank```| Float|
|```oxygen_pressure``` | Float|
|```fan_pri_rpm```|Float|
|```fan_sec_rpm``` | Float|
|```cabin_pressure```| Float|
|```cabin_temperature```|Float|
|```battery_level``` | Float|
|```external_temp``` | Float|
|```coolant_pressure``` | Float|
|```coolant_storage```|Float|
|```rover_elapsed_time```| Integer|
|```sim_running``` | Boolean|
|```dust_connected``` | Boolean|
|```distance_from_base```| Float|



