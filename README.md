# SartoriUSB

USB serial connection to Sartorius Scales

## Example:

```python

    import sartoriusb as sub

    with sub.SartoriusUsb('COM4') as conn:
        result = conn.measure()

    assert result.mode == "G"
    assert result.value == "+3.4"
    assert result.unit == "mg"
    assert result.stable == True
    assert result.message == None
```

## Required settings on the scale

The USB protocol on the scale must be set to SBI.

## Connection to the scale

The prefered way to establish an connection is the use of a context manager:
`with sartoriusb.SartoriusUsb('COM4') as conn:`

For manually handling the connection, the methods `connect()` and
`close()` can be used. For convenience there is also and `open()`
method that just behaves like `connect()`


## Sending commands and receiving output

Sending commands to the scale can be done with the `send(cmd)`, the
available commands according to the manual are listed below, but you could
but propably shouldn't send any arbitrary commands to the scale.

For reading the results from the scale, there are two methods available:
- `read(bytes)`: reads a number of bytes from the scale
- `readlines()`: returns a list of text lines, already decoded from bytes

Since sending a command and recieving an output are often used side by side,
there is a convenience method: `get(cmd)` will first send the command and
returns the output from the scale as a list of strings.

## Measuring

To measure a weight (or whatever the scale is set to), you could use
`get(CMD_PRINT)` and parse the output yourselve or use the `measure()`
method and get an already parsed output:

The function returns a `sartoriusb.Measurement` named tuple:

- `Measurement.mode`:
   The measurement mode, might be `unknown` if reporting on the scale is set
   to 16 byte output
- `Measurement.value`:
    The value as string as reported by the scale; whitespace an nonnumeric
    characters are removed, so `int()` or `float()` could be used directly
- `Measurement.unit`:
    The unit of the Measurement reported by the scale. Might be `None` if it
    was an unstable read
- `Measurement.stable`:
    Boolean value indicating if the measured value was stable or unstable
- `Measurement.message`:
    If a non-measurement message was sent from the scale, it is reported here
    and all other fields are set to `None`. For a regular measurement result
    this field is `None`.

## Available Commands

- `CMD_PRINT`: "Print" the current measurement result
- `CMD_TARA`: performa a tara or set the display to zero

- `CMD_EXPCLICIT_TARA`: explicit tara only
- `CMD_EXPCLICIT_NULL`: explicit set display to zero

- `CMD_INFO_TYPE`:  show scale type
- `CMD_INFO_SNR`: show serial number of scale
- `CMD_INFO_VERSION_SCALE`: show software version of the scale
- `CMD_INFO_VERSION_CONTROL_UNIT`: show the software version of the command and display module
- `CMD_INFO_USER`: display user and device id

- `CMD_FILTER_ENVIRONMENT_VERY_STABLE`: set the filter to "very stable enviroment"
- `CMD_FILTER_ENVIRONMENT_STABLE`: set the filter to "stable enviroment"
- `CMD_FILTER_ENVIRONMENT_UNSTABLE`:  set the filter to "unstable enviroment"
- `CMD_FILTER_ENVIRONMENT_VERAY_UNSTABLE`:  set the filter to "very unstable enviroment"

- `CMD_KEYBOARD_LOCK`: lock the keyboard on the command and display module
- `CMD_KEYBOARD_UNKLOCK`: unlock the keyboard on the command and display module
- `CMD_KEYPRESS_PRINT`: simulate a keypress on the command modules 'print' key
- `CMD_KEYPRESS_CANCEL`: simulate a keypress on the command modules 'cancel' key

- `CMD_BEEP`: make the scale beep

- `CMD_ADJUST_INTERNAL`: start internal adjustment
- `CMD_ADJUST_EXTERNAL`: start external adjustment with standard weights

- `CMD_RESTART`: restart the scale
