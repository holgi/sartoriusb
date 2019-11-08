""" pysartoriusb

Controlling a Sartorius Scale via USB

"""

__version__ = "0.1.0"

import serial

from collections import namedtuple

CMD_PRINT = b"P"
CMD_TARA = b"T"

CMD_EXPCLICIT_TARA = b"U"
CMD_EXPCLICIT_NULL = b"V"

CMD_INFO_TYPE = b"x1_"
CMD_INFO_SNR = b"x2_"
CMD_INFO_VERSION_SCALE = b"x3_"
CMD_INFO_VERSION_CONTROL_UNIT = b"x4_"
CMD_INFO_USER = b"x5_"

CMD_FILTER_ENVIRONMENT_VERY_STABLE = b"K"
CMD_FILTER_ENVIRONMENT_STABLE = b"L"
CMD_FILTER_ENVIRONMENT_UNSTABLE = b"M"
CMD_FILTER_ENVIRONMENT_VERAY_UNSTABLE = b"N"

CMD_KEYBOARD_LOCK = b"O"
CMD_KEYBOARD_UNKLOCK = b"R"
CMD_KEYPRESS_PRINT = b"kP_"
CMD_KEYPRESS_CANCEL = b"s3_"

CMD_BEEP = b"Q"

CMD_RESTART = b"S"
CMD_ADJUST_INTERNAL = b"Z"
CMD_ADJUST_EXTERNAL = b"W"


ESC = chr(27).encode("utf-8")
CR = chr(13).encode("utf-8")
LF = chr(10).encode("utf-8")


Measurement = namedtuple(
    "Measurement",
    ["mode", "value", "unit", "stable", "message"],
)


class SartoriusUsb:

    encoding = "ascii"

    def __init__(self, *serial_args, timeout=1, **serial_kargs):
        """ initialization fo the class

        All arguments are passed on to serial.Serial

        :params *serial_args: positional arguments for serial.Serial
        :params timeout: timeout of connection in seconds, defaults to 1
        :params *serial_kargs: keyword arguments for serial.Serial
        """

        self._serial_args = serial_args

        self._serial_kargs = serial_kargs
        self._serial_kargs["timeout"] = timeout

        self._con = None

    @property
    def connection(self):
        """ returns the serial connection, establishes a new one if needed """
        if self._con is None:
            self.connect()
        return self._con

    def connect(self):
        """ establishes a new serial connection """
        self._con = serial.Serial(*self._serial_args, **self._serial_kargs)

    def open(self):
        """ establishes a new serial connection

        This function just calls the 'connect()' method and is here for
        compability with other libraries that use open() / close()
        """
        self.connect()

    def close(self):
        """ closes a serial connection, if one is open """
        if self._con:
            self._con.close()
            self._con = None

    def send(self, command):
        """ sends a command to the scale """
        if not isinstance(command, bytes):
            command = str(command).encode(self.encoding)
        self.connection.write(ESC + command + CR + LF)

    def read(self, nr_of_bytes=1):
        """ reads some number of bytes from the serial connection """
        return self.connection.read(nr_of_bytes)

    def readline(self):
        """ reads bytes from the serial connection until a newline """
        return self.connection.readline()

    def readlines(self):
        """ returns a list of lines of available data """
        lines = []
        while True:
            line = self.connection.readline()
            line = line.decode(self.encoding)
            if not line.strip():
                # a line with only whitespace shows the end of the output
                # also a read timeout produces b''
                break
            lines.append(line)
        return lines

    def get(self, command):
        """ sends a command and returns the available data """
        self.send(command)
        return self.readlines()

    def measure(self):
        """ sends a print"""
        raw_data_lines = self.get(CMD_PRINT)
        if raw_data_lines:
            raw_data = raw_data_lines[0]
            return self.parse_measurement(raw_data)
        else:
            # propably serial connection timeout
            return Measurement(
                None, None, None, None, "Connection Timeout")

    def parse_measurement(self, raw_data):
        """ parses the raw data from a measurement """
        if len(raw_data) <= 16:
            return self._parse_16_char_output(raw_data)
        else:
            return self._parse_22_char_output(raw_data)

    def _parse_22_char_output(self, raw_data):
        """ parse a 16 character measurement output

        The scale can be set to return two different types of output. This
        function parses a 16 character output.
        """

        mode = raw_data[:6].strip()
        rest = raw_data[6:]

        return self._parse_16_char_output(rest, mode)

    def _parse_16_char_output(self, raw_data, mode="unknown"):
        """ parse a 16 character measurement output

        The scale can be set to return two different types of output. This
        function parses a 16 character output.
        """

        if self._is_message(raw_data):
            msg = raw_data.strip()
            return Measurement(None, None, None, None, msg)

        raw_data = self._remove_calibration_note(raw_data)

        sign = raw_data[0].strip()
        value_and_unit = raw_data[1:].strip()
        parts = value_and_unit.rsplit(" ", 1)
        raw_value = parts[0]
        value = sign + "".join(raw_value.split())

        if len(parts) == 2:
            unit = parts[1]
            stable = True
        else:
            unit = None
            stable = False

        return Measurement(
            mode, value, unit, stable, None
        )

    def _is_message(self, raw_data):
        """ returns the message that occured in a measurement or False """
        for identifier in ("high", "low", "cal", "err", "--"):
            if identifier in raw_data.lower():
                return True
        return False

    def _remove_calibration_note(self, raw_data):
        """ adjusts the raw data string if a calibration note is present

        According to the manual, this should not happen in SBI mode of the
        scale. This is included to prevent hiccups but probably not handled
        the right way....

        The data with a calibration node on in put and output of this method

        in:  "+123.4567[8]g  "
        out: "+123.45678  g  "

        """
        if "[" in raw_data:
            raw_data = raw_data.replace("[", "").replace("]", "  ")
        return raw_data

    def __enter__(self):
        """ Context manager: establishes connection """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """ Context manager: closes connection """
        self.close()
