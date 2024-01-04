import pytest

from .utils import prepare_okpd2_code, get_price_cat


def test_get_price_cat():
    assert isinstance(get_price_cat(0), int)
    assert isinstance(get_price_cat(-1), int)
    assert isinstance(get_price_cat(1), int)
    try:
        get_price_cat('frifm')
        assert False
    except ValueError:
        assert True

def test_prepare_okpd2_code():
    assert prepare_okpd2_code('11.11.10.000') == '11.11.1'
    assert prepare_okpd2_code('11.11.11.2') == '11.11.11.200'
    assert prepare_okpd2_code('11.11.10.020') == '11.11.10.020'
    assert prepare_okpd2_code('10.00.0') == '10'
    assert prepare_okpd2_code('01.12.10.000') == '01.12.1'
