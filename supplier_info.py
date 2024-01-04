import re
import json
import sys

from collections import Counter
from typing import Iterable, Tuple, List
from functools import cached_property, cache
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utils import NormDict, prepare_okpd2_code
from db.db import KeyInfoBuilder, rc, fz, pr, ok, okw, okr, okrw, okc, okcw


class SupplierInfo:
    KEYINFO_BUILDER = KeyInfoBuilder()
    DEP_PATH = Path(__file__).parent.parent/'dependencies' 
    with open(DEP_PATH/'msp_inn_reestr.json', 'r') as f:
        msp_inn_reestr = set(json.load(f))

    def __init__(self, inn_kpp: str | None = None) -> None:
        self.inn_kpp = inn_kpp
        self.msp = None if inn_kpp is None else self._check_msp()
        self.info = Counter()

    @classmethod
    def from_rows(cls, inn_kpp: str, rows: Iterable[Tuple[str, int]]):
        model = cls(inn_kpp)
        for key, num in rows:
            key_info = cls.KEYINFO_BUILDER.from_str(key)
            model.info[key_info] = num
        return model

    def as_rows(self) -> List[Tuple[str, str, int]]:
        rows = []
        for key, num in self.region2count.items():
            key = self.KEYINFO_BUILDER.gen_key('rc', self.inn_kpp, key.region_code)
            rows.append((key, self.inn_kpp, num.count))
        for key, num in self.fz2count.items():
            key = self.KEYINFO_BUILDER.gen_key('fz', self.inn_kpp, key.fz)
            rows.append((key, self.inn_kpp, num.count))
        for key, num in self.price_cat2count.items():
            key = self.KEYINFO_BUILDER.gen_key('pr', self.inn_kpp, key.price_cat)
            rows.append((key, self.inn_kpp, num.count))
        for keys, num in self.okpd_iswin2count.items():
            key = self.KEYINFO_BUILDER.gen_key('okw', self.inn_kpp, *keys)
            rows.append((key, self.inn_kpp, num.count))
        for keys, num in self.okpd_region_iswin2count.items():
            key = self.KEYINFO_BUILDER.gen_key('okrw', self.inn_kpp, *keys)
            rows.append((key, self.inn_kpp, num.count))
        for keys, num in self.okpd_customer_iswin2count.items():
            key = self.KEYINFO_BUILDER.gen_key('okcw', self.inn_kpp, *keys)
            rows.append((key, self.inn_kpp, num.count))
        return rows
        
    def update_region2count(self, region_codes: Iterable[str]) -> None:
        rc_codes = (rc(str(region_code)) for region_code in region_codes)
        self.info.update(rc_codes)
    
    def update_fz2count(self, fz_codes: Iterable[str]) -> None:
        fz_codes = (fz(str(fz_code)) for fz_code in fz_codes)
        self.info.update(fz_codes)

    def update_price_cat2count(self, price_cats: Iterable[int]) -> None:
        pr_codes = (pr(int(price_cat)) for price_cat in price_cats)
        self.info.update(pr_codes)

    def update_okpd_iswin2count(
        self, 
        okpd2_codes: Iterable[str], 
        is_win: bool
    ) -> None:
        okw_codes = (
            okw(str(prepare_okpd2_code(okpd2_code)), bool(is_win)) 
            for okpd2_code in okpd2_codes
        )
        self.info.update(okw_codes)

    def update_okpd_region_iswin2count(
        self, 
        okpd2_codes: Iterable[str], 
        region_code: str,
        is_win: bool
    ) -> None:
        okrw_codes = (
            okrw(
                str(prepare_okpd2_code(okpd2_code)), 
                str(region_code), 
                bool(is_win)
            )
            for okpd2_code in okpd2_codes
        )
        self.info.update(okrw_codes)

    def update_okpd_customer_iswin2count(
        self, 
        okpd2_codes: Iterable[str], 
        customer_inn_kpp: str,
        is_win: bool
    ) -> None:
        okcw_codes = (
            okcw(
                str(prepare_okpd2_code(okpd2_code)), 
                str(customer_inn_kpp),
                bool(is_win)
            )
            for okpd2_code in okpd2_codes
        )
        self.info.update(okcw_codes)

    @cached_property
    def region2count(self) -> NormDict:
        return NormDict.from_counter({
            rc_: count for rc_, count in self.info.items() 
            if isinstance(rc_, rc)
        })

    @cached_property
    def fz2count(self) -> NormDict:
        return NormDict.from_counter({
            fz_: count for fz_, count in self.info.items() 
            if isinstance(fz_, fz)
        })

    @cached_property
    def price_cat2count(self) -> NormDict:
        return NormDict.from_counter({
            pr_: count for pr_, count in self.info.items() 
            if isinstance(pr_, pr)
        })

    @cached_property
    def max_price_cat(self) -> int:
        return max(
            pr_.price_cat for pr_ in self.info.keys()
            if isinstance(pr_, pr)
        )

    @cached_property
    def okpd_iswin2count(self) -> NormDict:
        return NormDict.from_counter({
            okw_: count for okw_, count in self.info.items() 
            if isinstance(okw_, okw)
        })

    @cached_property
    def okpd_region_iswin2count(self) -> NormDict:
        return NormDict.from_counter({
            okrw_: count for okrw_, count in self.info.items() 
            if isinstance(okrw_, okrw)
        })

    @cached_property
    def okpd_customer_iswin2count(self) -> NormDict:
        return NormDict.from_counter({
            okcw_: count for okcw_, count in self.info.items() 
            if isinstance(okcw_, okcw)
        })

    @cache
    def get_okpd2count(
        self, 
        len_okpd: int = 12, 
        only_win: bool = False
    ) -> NormDict:
        ok_codes = {
            ok(prepare_okpd2_code(okw_.okpd2_code[:len_okpd])): count
            for okw_, count in self.info.items() 
            if isinstance(okw_, okw)
            and ((only_win and ok.iswin) or (not only_win))
        }
        return NormDict.from_counter(ok_codes)

    # @wrap_lru_cache
    @cache
    def get_okpd_region2count(
        self, 
        len_okpd: int = 12,
        only_win: bool = False
    ) -> NormDict:
        okr_codes = {
            okr(
                prepare_okpd2_code(okrw_.okpd2_code[:len_okpd]), 
                okrw_.region_code
            ): count
            for okrw_, count in self.info.items() 
            if isinstance(okrw_, okrw)
            and ((only_win and okrw_.iswin) or (not only_win))
        }
        return NormDict.from_counter(okr_codes)

    # @wrap_lru_cache
    @cache
    def get_okpd_customer2count(
        self, 
        len_okpd: int = 5,
        only_win: bool = False
    ) -> NormDict:
        okc_codes = {
            okc(
                prepare_okpd2_code(okcw_.okpd2_code[:len_okpd]), 
                okcw_.customer_inn_kpp
            ): count
            for okcw_, count in self.info.items()
            if isinstance(okcw_, okcw)
            and ((only_win and okcw_.iswin) or (not only_win))
        }
        return NormDict.from_counter(okc_codes)

    def _check_msp(self) -> bool:
        if self.inn_kpp.split('_')[0] in self.msp_inn_reestr:
            return True
        return False

    def __repr__(self) -> None:
        return (
            f'(inn_kpp: {self.inn_kpp},\n' +
            f'\tmsp: {self.msp},\n' +
            f'\tregion2count: {self.region2count},\n' +
            f'\tfz2count: {self.fz2count},\n' +
            f'\tprice_cat2count: {self.price_cat2count},\n' +
            f'\tokpd2count: {self.get_okpd2count()},\n' +
            f'\tokpd_region2count: {self.get_okpd_region2count()},\n' +
            f'\tokpd_customer2count: {self.get_okpd_customer2count()})'
        )
