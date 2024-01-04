import sys
import string

from pathlib import Path

import pytest

from .supplier_info import SupplierInfo

sys.path.append(str(Path(__file__).parent.parent))
from db.db import RecSysDataBase, rc, fz, pr, ok, okw, okr, okrw, okc, okcw
from utils import NormDict

db = RecSysDataBase()
inn_kpp = '9705031526_770501001'
rows = [
    ('rc:9705031526_770501001:52', 1),
    ('rc:9705031526_770501001:43', 70),
    ('fz:9705031526_770501001:44fz', 1356), 
    ('fz:9705031526_770501001:223fz', 62),
    ('pr:9705031526_770501001:1', 273),
    ('pr:9705031526_770501001:3', 123),
    ('pr:9705031526_770501001:0', 647),
    ('okw:9705031526_770501001:21.20.10.182:True', 3),
    ('okrw:9705031526_770501001:21.20.10.254:77:True', 17),
    ('okrw:9705031526_770501001:21.20.10.192:59:True', 5),
    ('okrw:9705031526_770501001:21.20.10.191:24:True', 3),
    ('okcw:9705031526_770501001:21.20.10.214:3205000938_324501001:True', 1),
    ('okcw:9705031526_770501001:21.20.10.214:4501054974_450101001:True', 2),
]
s = SupplierInfo.from_rows(inn_kpp, rows)


class TestSupplierInfo:
    def test_from_rows(self):
        try:
            SupplierInfo.from_rows(inn_kpp, rows)
            assert True
        except:
            assert False

    def test_as_rows(self):
        assert set(s.as_rows()) == {(row[0], inn_kpp, row[1]) for row in rows}

    def test_update_region2count(self):
        s = SupplierInfo(inn_kpp)
        assert len([k for k in s.info.keys() if isinstance(k, rc)]) == 0
        # s.update_region2count(('01', '02', '01'))
        # assert len([k for k in s.info.keys() if isinstance(k, rc)]) == 2
        # assert s.info.get(rc('01')) == 2
        # assert s.info.get(rc('02')) == 1
        # s.update_region2count(('01', '03'))
        # assert len([k for k in s.info.keys() if isinstance(k, rc)]) == 3
        # assert s.info.get(rc('01')) == 3
        # assert s.info.get(rc('02')) == 1
        # assert s.info.get(rc('03')) == 1

    def test_update_fz2count(self):
        s = SupplierInfo(inn_kpp)
        assert len([k for k in s.info.keys() if isinstance(k, fz)]) == 0
        # s.update_fz2count(('fz44', 'fz223', 'fz44'))
        # assert len([k for k in s.info.keys() if isinstance(k, fz)]) == 2
        # assert s.info.get(fz('fz44')) == 2
        # assert s.info.get(fz('fz223')) == 1
        # s.update_fz2count(('fz223', 'fz44'))
        # assert len([k for k in s.info.keys() if isinstance(k, fz)]) == 2
        # assert s.info.get(fz('fz44')) == 3
        # assert s.info.get(fz('fz223')) == 2

    def test_update_price_cat2count(self):
        s = SupplierInfo(inn_kpp)
        assert len([k for k in s.info.keys() if isinstance(k, pr)]) == 0
        # s.update_price_cat2count((1, 2, 1))
        # assert len([k for k in s.info.keys() if isinstance(k, pr)]) == 2
        # assert s.info.get(pr(1)) == 2
        # assert s.info.get(pr(2)) == 1
        # s.update_price_cat2count((1, 3))
        # assert len([k for k in s.info.keys() if isinstance(k, pr)]) == 3
        # assert s.info.get(pr(1)) == 3
        # assert s.info.get(pr(2)) == 1
        # assert s.info.get(pr(3)) == 1

    def test_update_okpd_iswin2count(self):
        s = SupplierInfo(inn_kpp)
        assert len([k for k in s.info.keys() if isinstance(k, okw)]) == 0
        # s.update_okpd_iswin2count(('11.11.11', '22.22.22', '11.11.11'), True)
        # assert len([k for k in s.info.keys() if isinstance(k, okw)]) == 2
        # assert s.info.get(okw('11.11.11', True)) == 2
        # assert s.info.get(okw('22.22.22', True)) == 1
        # s.update_okpd_iswin2count(('11.11.11', '33.33.33'), True)
        # assert len([k for k in s.info.keys() if isinstance(k, okw)]) == 3
        # assert s.info.get(okw('11.11.11', True)) == 3
        # assert s.info.get(okw('22.22.22', True)) == 1
        # assert s.info.get(okw('33.33.33', True)) == 1

    def test_update_okpd_region_iswin2count(self):
        s = SupplierInfo(inn_kpp)
        assert len([k for k in s.info.keys() if isinstance(k, okrw)]) == 0
        # s.update_okpd_region_iswin2count(('11.11.11', '22.22.22', '11.11.11'), '01', True)
        # assert len([k for k in s.info.keys() if isinstance(k, okrw)]) == 2
        # assert s.info.get(okrw('11.11.11', '01', True)) == 2
        # assert s.info.get(okrw('22.22.22', '01', True)) == 1
        # s.update_okpd_region_iswin2count(('11.11.11', '33.33.33'), '01', True)
        # assert len([k for k in s.info.keys() if isinstance(k, okrw)]) == 3
        # assert s.info.get(okrw('11.11.11', '01', True)) == 3
        # assert s.info.get(okrw('22.22.22', '01', True)) == 1
        # assert s.info.get(okrw('33.33.33', '01', True)) == 1

    def test_update_okpd_customer_iswin2count(self):
        s = SupplierInfo(inn_kpp)
        assert len([k for k in s.info.keys() if isinstance(k, okcw)]) == 0
        # s.update_okpd_customer_iswin2count(('11.11.11', '22.22.22', '11.11.11'), '111_111', True)
        # assert len([k for k in s.info.keys() if isinstance(k, okcw)]) == 2
        # assert s.info.get(okcw('11.11.11', '111_111', True)) == 2
        # assert s.info.get(okcw('22.22.22', '111_111', True)) == 1
        # s.update_okpd_customer_iswin2count(('11.11.11', '33.33.33'), '111_111', True)
        # assert len([k for k in s.info.keys() if isinstance(k, okcw)]) == 3
        # assert s.info.get(okcw('11.11.11', '111_111', True)) == 3
        # assert s.info.get(okcw('22.22.22', '111_111', True)) == 1
        # assert s.info.get(okcw('33.33.33', '111_111', True)) == 1

    def test_region2count(self):
        s = SupplierInfo(inn_kpp)
        assert s.region2count == NormDict()
        # s.update_region2count(('01', '02', '01'))
        # assert s.region2count == NormDict.from_counter({rc('01'): 2, rc('02'): 1})

    def test_fz2count(self):
        s = SupplierInfo(inn_kpp)
        assert s.fz2count == NormDict()
        # s.update_fz2count(('fz44', 'fz223', 'fz44'))
        # assert s.fz2count == NormDict.from_counter({fz('fz44'): 2, fz('fz223'): 1})

    def test_price_cat2count(self):
        s = SupplierInfo(inn_kpp)
        assert s.price_cat2count == NormDict()
        # s.update_price_cat2count((1, 2, 1))
        # assert s.price_cat2count == NormDict.from_counter({pr(1): 2, pr(2): 1})

    def test_okpd_iswin2count(self):
        s = SupplierInfo(inn_kpp)
        assert s.okpd_iswin2count == NormDict()
        # s.update_okpd_iswin2count(('11.1', '22.2', '11.1'), False)
        # assert s.okpd_iswin2count == NormDict.from_counter({okw('11.1', False): 2 , okw('22.2', False): 1})

    def test_okpd_region_iswin2count(self):
        s = SupplierInfo(inn_kpp)
        assert s.okpd_region_iswin2count == NormDict()
        # s.update_okpd_region_iswin2count(('11.1', '22.2', '11.1'), '99', True)
        # assert s.okpd_region_iswin2count == NormDict.from_counter({okrw('11.1', '99', True): 2, okrw('22.2', '99', True): 1})

    def test_okpd_customer_iswin2count(self):
        s = SupplierInfo(inn_kpp)
        assert s.okpd_customer_iswin2count == NormDict()
        # s.update_okpd_customer_iswin2count(('11.1', '22.2', '11.1'), '11_1', True)
        # assert s.okpd_customer_iswin2count == NormDict.from_counter({okcw('11.1', '11_1', True): 2, okcw('22.2', '11_1', True): 1})

    s_okpd = ['21.20.10.182'] * 3 \
        + ['21.20.10.254'] * 17 \
        + ['21.20.10.192'] * 5 \
        + ['21.20.10.191'] * 3 \
        + ['21.20.10.214'] * 1 \
        + ['21.20.10.214'] * 2
