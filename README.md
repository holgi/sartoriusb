# pySartoriUSB

USB serial connection to Sartorius Scales

## Example:

```python

    import pysartoriusb as sub

    with sub.SartoriusUsb('COM4') as conn:
        result = conn.measure()

    assert result.mode == "G"
    assert result.value == "+3.4"
    assert result.unit == "mg"
    assert result.stable == True
    assert result.error == False
    assert result.calibration == True
```

## Available Commands

There are two methods available to send commands to the scale:

- ```SartoriusUsb.send(cmd)```: just sends a command, results must be read programatically
- ```SartoriusUsb.get(cmd)```: send a command and return the answer from the scale


Since "printing" the current measurement and parsing the result is something
very common, there is a simple method for it: ```SartoriusUsb.measure()```


These commands are available:

- ```CMD_PRINT```: "Print" the current measurement result
- ```CMD_TARA```: performa a tara or set the display to zero

- ```CMD_EXPCLICIT_TARA```: explicit tara only
- ```CMD_EXPCLICIT_NULL```: explicit set display to zero

- ```CMD_INFO_TYPE```:  show scale type
- ```CMD_INFO_SNR```: show serial number of scale
- ```CMD_INFO_VERSION_SCALE```: show software version of the scale
- ```CMD_INFO_VERSION_CONTROL_UNIT```: show the software version of the command and display module
- ```CMD_INFO_USER```: display user and device id

- ```CMD_FILTER_ENVIRONMENT_VERY_STABLE```: set the filter to "very stable enviroment"
- ```CMD_FILTER_ENVIRONMENT_STABLE```: set the filter to "stable enviroment"
- ```CMD_FILTER_ENVIRONMENT_UNSTABLE```:  set the filter to "unstable enviroment"
- ```CMD_FILTER_ENVIRONMENT_VERAY_UNSTABLE```:  set the filter to "very unstable enviroment"

- ```CMD_KEYBOARD_LOCK```: lock the keyboard on the command and display module
- ```CMD_KEYBOARD_UNKLOCK```: unlock the keyboard on the command and display module
- ```CMD_KEYPRESS_PRINT```: simulate a keypress on the command modules 'print' key
- ```CMD_KEYPRESS_CANCEL```: simulate a keypress on the command modules 'cancel' key

- ```CMD_BEEP```: make the scale beep

- ```CMD_ADJUST_INTERNAL```: start internal adjustment
- ```CMD_ADJUST_EXTERNAL```: start external adjustment with standard weights

- ```CMD_RESTART```: restart the scale
