import json
import os
import sqlite3
from unittest import mock

import pytest

from hotconsole import hotconsole
from hotconsole.helpers import MarkHelper, MarkType, InnGenerator, DBHelper, OSHelper


class TestOSHelper:
    def test_input_number_error(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("builtins.input", lambda _: "f")
        with pytest.raises(TypeError):
            OSHelper.input_number()

    def test_input_number_success(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("builtins.input", lambda _: "4")
        assert OSHelper.input_number() == 4

    def test_input_numbers_error(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("builtins.input", lambda _: "4 f")
        with pytest.raises(TypeError):
            OSHelper.input_number_array()

    def test_input_numbers_success(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("builtins.input", lambda _: "1 2 3")
        assert OSHelper.input_number_array() == [1, 2, 3]


class TestDBHelper:
    def test_connect_with_absent_address_error(self):
        with pytest.raises(AttributeError):
            DBHelper.connect("fqklfq")

    def test_connect_with_not_db_address_error(self):
        with pytest.raises(sqlite3.OperationalError):
            DBHelper.connect(os.path.dirname(__file__))

    @mock.patch("sqlite3.connect")
    def test_connect_and_execute_query_select_success(
            self, mock_connect: mock.MagicMock, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr("os.path.exists", lambda _: True)

        mock_cursor = mock.Mock()
        mock_connection = mock.Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        query = "select"

        DBHelper.connect_and_execute_query(os.path.dirname(__file__) + ".db", query)
        mock_connect.assert_called_once()
        mock_connection.commit.assert_not_called()
        mock_connection.close.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()

    @mock.patch("sqlite3.connect")
    def test_connect_and_execute_query_update_success(
            self, mock_connect: mock.MagicMock, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr("os.path.exists", lambda _: True)

        mock_cursor = mock.Mock()
        mock_connection = mock.Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        query = "update"
        DBHelper.connect_and_execute_query(os.path.dirname(__file__) + ".db", query)
        mock_connect.assert_called_once()
        mock_connection.cursor.assert_called_once()
        mock_connection.commit.assert_called_once()
        mock_connection.close.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_not_called()

    @mock.patch("sqlite3.connect")
    def test_connect_and_execute_query_error(self, mock_connect: mock.MagicMock, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("os.path.exists", lambda _: True)

        mock_cursor = mock.Mock()
        mock_cursor.execute.side_effect = sqlite3.OperationalError
        mock_connection = mock.Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        with pytest.raises(sqlite3.OperationalError):
            DBHelper.connect_and_execute_query(os.path.dirname(__file__) + ".db", "select")
        mock_connect.assert_called_once()
        mock_connection.cursor.assert_called_once()
        mock_connection.commit.assert_not_called()
        mock_connection.close.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_not_called()


class TestCommandHelpers:
    @mock.patch("builtins.print")
    def test_print_one_option(self, mock_print: mock.MagicMock):
        hotconsole.CommandHelpers.print_options(["Опция"])
        mock_print.assert_called_with("1. Опция")

    @mock.patch("builtins.print")
    def test_print_few_options(self, mock_print: mock.MagicMock):
        hotconsole.CommandHelpers.print_options(["Опция1", "Опция2"])
        mock_print.assert_has_calls([mock.call("1. Опция1"), mock.call("2. Опция2")], any_order=False)

    @mock.patch("builtins.print")
    def test_print_tuple_options(self, mock_print: mock.MagicMock):
        hotconsole.CommandHelpers.print_options_tuple([("Ключ1", "Значение1"), ("Ключ2", "Значение2")])
        mock_print.assert_has_calls([mock.call("1. Значение1"), mock.call("2. Значение2")], any_order=False)


class TestInnGenerator:
    @pytest.mark.parametrize("real_inn", ["245801671843", "810700624122", "421710073190"])
    def test_inn_for_fl(self, real_inn):
        actual_control_numbers = InnGenerator._get_controls_inn_fl(real_inn[:-2])
        assert actual_control_numbers == real_inn[-2:]

    @pytest.mark.parametrize("real_inn", ["7842024502", "7842439200", "9405001425"])
    def test_inn_for_ul(self, real_inn):
        actual_control_numbers = InnGenerator._get_controls_inn_ul(real_inn[:-1])
        assert actual_control_numbers == real_inn[-1]


class TestMarkHelper:
    @pytest.mark.parametrize("price, expected", [(0, "AAAA"), (1, "AAAB"), (1000000, "B=UA")])
    def test_encode_price_for_mark(self, price, expected):
        coded_min_price = MarkHelper._encode_price_for_mark(price)
        assert coded_min_price == expected

    @pytest.mark.parametrize("real_barcode", ["3321339135834", "2100000000418"])
    def test_gen_barcode(self, real_barcode):
        actual_control_number = MarkHelper.gen_barcode(real_barcode[:-1])[-1]
        assert actual_control_number == real_barcode[-1]

    @pytest.mark.parametrize("weight, expected", [("985931", "985931"), ("1", "000001")])
    def test_gen_mark_milk(self, monkeypatch: pytest.MonkeyPatch, weight, expected):
        monkeypatch.setattr("builtins.input", lambda: weight)
        mark = MarkHelper.gen_mark(MarkType.MILK)
        assert "3103" in mark
        assert mark[-6:] == expected

    def test_gen_mark_milk_without_weight(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("builtins.input", lambda: "0")
        mark = MarkHelper.gen_mark(MarkType.MILK)
        assert "3103" not in mark
        assert mark[-6:] != "000000"

    @pytest.mark.parametrize(
        "mark, splitted_mark",
        [
            (
                    r"010210000000008121mmykmz\u001d93TrJ1\u001d3103005678",
                    ["010210000000008121mmykmz", "93TrJ1", "3103005678"]
            ),
            (
                    r"010210000000008121mmykmz93TrJ13103005678",
                    ["010210000000008121mmykmz", "93TrJ1", "3103005678"]
            ),
            (
                    r"04606203086627-UWzSA8AABUptys",
                    ["04606203086627-UWzSA8AABUptys"]
            ),
            (
                    r"(01)03221424250793(21)Xz&NASDPoeBd&0000000(91)8039(92)f4+32XYI/05BpU41ug3v1J8+t/9oaAutrfUzgVBWsQ==",
                    [
                        "(01)03221424250793(21)Xz&NASDPoeBd&0000000(91)8039(92)f4+32XYI/05BpU41ug3v1J8+t/9oaAutrfUzgVBWsQ=="]
            ),
            (
                    r"01030410947877712152TZW&93cAce31031234567",
                    ["01030410947877712152TZW&", "93cAce", "31031234567"]
            ),
            (
                    r"RU-430302-ABC0686893",
                    ["RU-430302-ABC0686893"]
            ),
            (
                    r"3595193310382",
                    ["3595193310382"]
            ),
            (
                    "010210000000\r\n008121mmykmz93TrJ13103005678",
                    ["010210000000008121mmykmz", "93TrJ1", "3103005678"]
            ),
            (
                    r"010462930887704421DzkcYt2\u001d8005177000\u001d93dGVz",
                    ["010462930887704421DzkcYt2", "8005177000", "93dGVz"]
            ),
            (
                    r"010462930887704421DzkcYt2\u001d8005177000\u001d93dGVz",
                    ["010462930887704421DzkcYt2", "8005177000", "93dGVz"]
            ),
            (
                "010210000000046321123456789723491444492fqkflqkkfwjfkqwjflqwkfjwkjf",
                ["0102100000000463211234567897234", "914444", "92fqkflqkkfwjfkqwjflqwkfjwkjf"]
            )
        ])
    def test_format_mark(self, mark, splitted_mark):
        assert MarkHelper.format_mark(mark) == splitted_mark


class TestIni:
    def test_get_updated_config(self, monkeypatch: pytest.MonkeyPatch):
        current_config = hotconsole.Config(
            version=1, consoleMode=False, refuseStartup=False, firstLegalEntity="", inn2UL="6699000000"
        )

        init_config = hotconsole.Config(
            version=2,
            consoleMode=True,
            refuseStartup=True,
            firstLegalEntity="5f29ca5e-8237-40a7-a842-de93a0c0f2f4",
            inn2UL="992570272700",
            new_field="new_string",
        )

        monkeypatch.setattr(hotconsole.Config, "load_dict", lambda: current_config.model_dump())
        assert hotconsole.Init.add_new_fields(init_config) == hotconsole.Config(
            version=2,
            consoleMode=False,
            refuseStartup=False,
            firstLegalEntity="",
            inn2UL="6699000000",
            new_field="new_string",
        )


class TestJsonMethods:
    def test_get_from_json_file_success(self):
        file_path = self.get_file_path()
        assert OSHelper.get_from_json_file("version", file_path) == 1
        assert OSHelper.get_from_json_file("consoleModeIsDefault", file_path) is False
        assert OSHelper.get_from_json_file("inn2UL", file_path) == "6699000000"

    def test_get_from_json_file_error(self):
        with pytest.raises(KeyError):
            OSHelper.get_from_json_file("wrong_field", self.get_file_path())

    def test_update_json_success(self):
        OSHelper.update_json_file("version", 100, self.get_file_path())
        assert OSHelper.get_from_json_file("version", self.get_file_path()) == 100
        assert OSHelper.get_from_json_file("inn2UL", self.get_file_path()) == "6699000000"

    def test_update_json_new_field_success(self):
        OSHelper.update_json_file("new_field", "new_value", self.get_file_path())
        assert OSHelper.get_from_json_file("new_field", self.get_file_path()) == "new_value"
        assert OSHelper.get_from_json_file("inn2UL", self.get_file_path()) == "6699000000"

    def test_extract_whole_json(self):
        assert OSHelper.extract_whole_json(self.get_file_path()) == {
            "version": 1,
            "inn2UL": "6699000000",
            "consoleModeIsDefault": False,
        }

    def setup_method(self):
        user_config = {"version": 1, "inn2UL": "6699000000", "consoleModeIsDefault": False}

        with open(self.get_file_path(), "w+", encoding="utf-8") as file:
            file.writelines(json.dumps(user_config))

    def teardown_method(self):
        if os.path.exists(self.get_file_path()):
            os.remove(self.get_file_path())

    def get_file_path(self):
        return os.path.join(os.path.dirname(__file__), "test.json")
