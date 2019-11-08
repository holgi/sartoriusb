import pytest

from unittest.mock import call


def test_sartorius_usb_init():
    from sartoriusb import SartoriusUsb

    sub = SartoriusUsb(1, 2, timeout=3, something=4, different=6)

    assert sub._serial_args == (1, 2)
    assert sub._serial_kargs == {"timeout": 3, "something": 4, "different": 6}
    assert sub._con is None


@pytest.mark.parametrize("con_value,expected", [(None, 1), ("Something", 0)])
def test_sartorius_usb_connection_property(mocker, con_value, expected):
    from sartoriusb import SartoriusUsb

    mocker.patch.object(SartoriusUsb, "connect")
    sub = SartoriusUsb()
    sub._con = con_value

    con = sub.connection

    assert sub.connect.call_count == expected
    assert con == con_value


def test_sartorius_connect_usb_parameters_passed_to_serial(mocker):
    from sartoriusb import SartoriusUsb, serial

    mocker.patch.object(serial, "Serial", return_value="dummy connection")
    sub = SartoriusUsb(1, 2, something=4, different=6)

    sub.connect()

    assert serial.Serial.call_count == 1
    assert serial.Serial.call_args == call(
        1, 2, timeout=1, something=4, different=6
    )
    assert sub._con == "dummy connection"


def test_sartorius_connect_on_alredy_established_connection(mocker):
    from sartoriusb import SartoriusUsb, serial

    mocker.patch.object(serial, "Serial")
    sub = SartoriusUsb()
    sub._con = "alredy connected"

    sub.connect()

    assert serial.Serial.call_count == 0


def test_sartorius_open_calls_connect(mocker):
    from sartoriusb import SartoriusUsb

    sub = SartoriusUsb()
    sub.connect = mocker.Mock()

    sub.open()

    assert sub.connect.call_count == 1


def test_sartorius_usb_close_calls_close_on_established_connection(mocker):
    from sartoriusb import SartoriusUsb

    sub = SartoriusUsb()
    sub._con = mocker.Mock()
    mocked_con = sub._con

    sub.close()

    assert sub._con is None
    assert mocked_con.close.call_count == 1


@pytest.mark.parametrize(
    "value,expected", [(b"bytes", b"bytes"), ("string", b"string")]
)
def test_sartorius_sends_bytes(mocker, value, expected):
    from sartoriusb import SartoriusUsb, ESC, CR, LF

    sub = SartoriusUsb()
    sub._con = mocker.Mock()

    sub.send(value)

    assert sub._con.write.call_count == 1
    assert sub._con.write.call_args == call(ESC + expected + CR + LF)


def test_sartorius_read_passes_argument(mocker):
    from sartoriusb import SartoriusUsb

    sub = SartoriusUsb()
    sub._con = mocker.Mock()
    sub._con.read.return_value = "Hello!"

    result = sub.read(42)

    assert sub._con.read.call_count == 1
    assert sub._con.read.call_args == call(42)
    assert result == "Hello!"


def test_sartorius_readline(mocker):
    from sartoriusb import SartoriusUsb

    sub = SartoriusUsb()
    sub._con = mocker.Mock()
    sub._con.readline.return_value = "Hello!"

    result = sub.readline()

    assert sub._con.readline.call_count == 1
    assert sub._con.readline.call_args == call()
    assert result == "Hello!"


@pytest.mark.parametrize("stop_line", [b"", b" "])
@pytest.mark.parametrize(
    "stop_position,expected",
    [(0, []), (1, ["one"]), (2, ["one", "two"]), (3, ["one", "two", "three"])],
)
def test_sartorius_readlines(mocker, stop_line, stop_position, expected):
    from sartoriusb import SartoriusUsb

    data = [b"one", b"two", b"three", b"four", b"five"]
    data[stop_position] = stop_line

    sub = SartoriusUsb()
    sub._con = mocker.Mock()
    sub._con.readline.side_effect = data

    result = sub.readlines()

    assert sub._con.readline.call_count == stop_position + 1
    assert result == expected


def test_sartorius_get(mocker):
    from sartoriusb import SartoriusUsb

    sub = SartoriusUsb()
    mocker.patch.object(sub, "send")
    mocker.patch.object(sub, "readlines", return_value="some result")

    result = sub.get("some command")

    assert sub.send.call_count == 1
    assert sub.send.call_args == call("some command")
    assert sub.readlines.call_count == 1
    assert sub.readlines.call_args == call()
    assert result == "some result"


def test_sartorius_measure_with_data(mocker):
    from sartoriusb import SartoriusUsb, CMD_PRINT

    sub = SartoriusUsb()
    mocker.patch.object(sub, "get", return_value=["value", "some other stuff"])
    mocker.patch("sartoriusb.parse_measurement", return_value="parsed result")

    result = sub.measure()

    assert sub.get.call_count == 1
    assert sub.get.call_args == call(CMD_PRINT)
    assert result == "parsed result"


def test_sartorius_measure_with_timeout(mocker):
    from sartoriusb import SartoriusUsb, CMD_PRINT

    sub = SartoriusUsb()
    mocker.patch.object(sub, "get", return_value=[])
    mocker.patch("sartoriusb.parse_measurement", return_value="parsed result")

    result = sub.measure()

    assert sub.get.call_count == 1
    assert sub.get.call_args == call(CMD_PRINT)
    assert result == (None, None, None, None, "Connection Timeout")

def test_sartorius_context_manager(mocker):
    from sartoriusb import SartoriusUsb

    sub = SartoriusUsb()
    mocker.patch.object(sub, "connect")
    mocker.patch.object(sub, "close")

    with sub as context:
        assert sub is context
        assert sub.connect.call_count == 1
        assert sub.close.call_count == 0

    assert sub.connect.call_count == 1
    assert sub.close.call_count == 1



@pytest.mark.parametrize(
    "value,count_16,count_22,expected",
    [
        ("123456789012345", 1, 0, "16"),
        ("1234567890123456", 1, 0, "16"),
        ("12345678901234567", 0, 1, "22"),
    ],
)
def test_sartorius_parse_measurement(
    mocker, value, count_16, count_22, expected
):
    from sartoriusb import parse_measurement

    mocker.patch("sartoriusb._parse_16_char_output", return_value="16")
    mocker.patch("sartoriusb._parse_22_char_output", return_value="22")

    result = parse_measurement(value)

    assert result == expected


def test_sartorius_parse_22_char_output(mocker):
    from sartoriusb import _parse_22_char_output

    mocker.patch("sartoriusb._parse_16_char_output", return_value="16")

    result = _parse_22_char_output(" mode value ")

    assert result == "16"


@pytest.mark.parametrize(
    "value,expected",
    [
        ("12345", False),
        (" some text ", False),
        (" Error 123 ", True),
        ("highlander ", True),
        (" too low", True),
        ("123--456", True),
        ("some calibration", True),
    ],
)
def test_sartorius_measurement_is_message(value, expected):
    from sartoriusb import _is_message

    result = _is_message(value)

    assert result == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", ""),
        ("1", "1"),
        ("1]3", "1]3"),
        ("[", ""),
        ("1[2", "12"),
        ("1[2]", "12  "),
        ("1[2] x", "12   x"),
    ],
)
def test_sartorius_remove_calibration_note(value, expected):
    from sartoriusb import _remove_calibration_note

    result = _remove_calibration_note(value)

    assert result == expected


@pytest.mark.parametrize(
    "text,value,unit,stable,cal",
    [
        (" 123.45678 g  ", "123.45678", "g", True, True),
        (" 123.4567[8]g  ", "123.45678", "g", True, False),
        ("+123.45678 mg  ", "+123.45678", "mg", True, True),
        ("-  3.456 mg  ", "-3.456", "mg", True, True),
        ("-  3.456     ", "-3.456", None, False, True),
        (" 0.0   ", "0.0", None, False, True),
    ],
)
def test_sartorius_parse_16_char_output(text, value, unit, stable, cal):
    from sartoriusb import _parse_16_char_output

    result = _parse_16_char_output(text, mode="X")

    assert result == ("X", value, unit, stable, None)


def test_sartorius_parse_16_char_output_on_message(mocker):
    from sartoriusb import _parse_16_char_output

    result = _parse_16_char_output(" some Error ")

    assert result == (None, None, None, None, "some Error")


