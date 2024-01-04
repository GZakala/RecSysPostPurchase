import re

from functools import lru_cache, wraps
from itertools import chain
from typing import Any, Iterable, List, Mapping


def wrap_lru_cache(maxsize):
    """
    Декоратор н основе lru_cache, но с добавлением функционала wraps для 
    корректного отображения информации о декорируемой функции.
    Нельзя использовать как декоратор метода!!! Только как декоратор функции!!!
    """
    if callable(maxsize):
        func = maxsize
        @lru_cache
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    def func_wrapper(func):
        @lru_cache(maxsize)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return func_wrapper

def get_price_cat(price: float) -> int:
    if float(price) < 400_000: return 0
    if float(price) < 1_000_000: return 1
    if float(price) < 5_000_000: return 2
    if float(price) < 20_000_000: return 3
    if float(price) < 100_000_000: return 4
    if float(price) < 1_000_000_000: return 5
    return 6

@wrap_lru_cache
def prepare_okpd2_code(okpd2_code: str) -> str:
    okpd2_code = re.sub(r'[0.]+$', '', okpd2_code)
    if len(okpd2_code) == 1:
        okpd2_code = okpd2_code + '0'
    if len(okpd2_code) > 8 and len(okpd2_code) < 12:
        okpd2_code += '0' * (12 - len(okpd2_code))
    return okpd2_code 

def prepare_okpd2_codes(okpd2_codes: Iterable[str]) -> List[str]:
    return [prepare_okpd2_code(oc) for oc in okpd2_codes]


class NormData:
    __slots__ = ('count', 'norm')
    def __init__(self, count: int = 0, norm: float | None = None) -> None:
        self.count = count
        self.norm = norm if norm is not None else 0.

    def __eq__(self, other) -> bool:
        if not isinstance(other, (int, NormData)):
            raise ValueError(
                'Операнд справа должен иметь значение int или MyData')
        if isinstance(other, int):
            return self.count == other
        return self.count == other.count

    def __add__(self, other):
        if not isinstance(other, (int, NormData)):
            raise ArithmeticError(
                'Операнд справа должен иметь значение int или MyData')
        if isinstance(other, int):
            return NormData(self.count + other, self.norm)
        return NormData(self.count + other.count, self.norm)

    def __int__(self) -> int:
        return int(self.count)

    def __repr__(self) -> str:
        return f'(c: {self.count}, n: {round(self.norm, 2)})'


class NormDict(dict):
    __slots__ = ()
    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def from_counter(cls, counter: Mapping[str, int]):
        model = cls()
        for k, v in counter.items():
            model[k] = NormData(v)
        model._calc_norm()
        return model

    @classmethod
    def from_elements(cls, elements: Iterable[str]):
        model = cls()
        model.update(elements)
        model._calc_norm()
        return model

    def update(self, elements: Iterable[Any] | None) -> None:
        if elements is None: return 
        for elem in elements:
            if elem in self:
                self[elem] += 1
            else:
                self[elem] = NormData(1)

    def elements(
        self, 
        startswith: str = '', 
        trunc_prefix: bool = True
    ) -> Iterable[str]:
        if trunc_prefix:
            return chain.from_iterable(
                [k[len(startswith):]] * v.count for k, v in self.items() 
                if k.startswith(startswith)
            )
        return chain.from_iterable(
            [k] * v.count for k, v in self.items() 
            if k.startswith(startswith)
        )

    def get_count(self, key: Any, default: Any) -> int:
        v = self.get(key, default)
        if isinstance(v, NormData):
            return v.count
        return v

    def get_norm(self, key: Any, default: Any) -> float:
        v = self.get(key, default)
        if isinstance(v, NormData):
            return v.norm
        return v

    def _calc_norm(self) -> None:
        sum_count = sum(v.count for v in self.values())
        for k in self.keys():
            self[k].norm = self[k].count / sum_count
