from pathlib import Path
from typing import Mapping, Generator, Sequence, Tuple, List, NamedTuple
from functools import wraps

import jinja2
import psycopg2


def autocommit(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.commit()
        res = func(self, *args, **kwargs)
        self.commit()
        return res
    return wrapper

class RecSysDataBase:
    CURDIR = Path(__file__).parent
    def __init__(
        self, 
        database: str = 'postgres',
        user: str = 'postgres',
        password: str = '12345',
        host: str = 'localhost',
        port: int = 5432
    ) -> None:
        self.connection = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()
        self.tpl_loader = jinja2.FileSystemLoader(self.CURDIR / 'templates')
        self.tpl_env = jinja2.Environment(loader=self.tpl_loader, trim_blocks=True)
        self.dict_name = 'key2num'
        self.create_dict()

    def commit(self) -> None:
        self.connection.commit()

    def select(self, sql: str) -> List[Tuple]:
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        return res

    def close(self) -> None:
        self.commit()
        self.connection.close()

    def new_connect(
        self,
        database: str = 'postgres',
        user: str = 'postgres',
        password: str = '12345',
        host: str = 'localhost',
        port: int = 5432
    ) -> None:
        if not self.connection.closed:
            self.close()
        self.connection = psycopg2.connect(
            database=database,
            user=user,
            password=password,
            host=host,
            port=port
        )
        self.cursor = self.connection.cursor()

    @autocommit
    def execute(self, sql: str) -> None:
        self.cursor.execute(sql)

    @autocommit
    def create_dict(self) -> bool:
        sql = """
        select tablename
            from pg_catalog.pg_tables
            where schemaname = 'public';
        """
        tables = [row[0] for row in self.select(sql)]
        if self.dict_name in tables:
            return False

        sql = f"""
        create table {self.dict_name}
        (
            key varchar(100) primary key,
            inn_kpp varchar(22),
            num int not null
        );
        create index index_{self.dict_name}_inn_kpp on key2num(inn_kpp);
        """
        self.execute(sql)
        return True

    def clear_dict(self) -> bool:
        sql = f"""
        select count(*)
            from pg_catalog.pg_tables
            where schemaname = 'public'
                and tablename = '{self.dict_name}';
        """
        if self.select(sql)[0][0] == 0:
            return False

        sql = f"""
        truncate table public.{self.dict_name};
        """
        self.execute(sql)
        return True

    def incr(self, key: str, inn_kpp: str, num: int = 1) -> None:
        sql = f"""
        insert into public.{self.dict_name} values
        ('{key}', '{inn_kpp}', {num})
        on conflict (key)
        do update set
            key = excluded.key,
            num = {self.dict_name}.num + excluded.num;
        """
        self.execute(sql)

    def incrby(
        self, 
        rows: Mapping[str, Tuple[str, int]] | Sequence[Tuple[str, str, int]]
    ) -> None:
        tpl = self.tpl_env.from_string("""
        insert into public.{{ dict_name }} values
        {% for key, innkpp, num in rows[:-1] -%}
        ('{{ key }}', '{{ innkpp }}', {{ num }}),
        {%- endfor %}
        ('{{ rows[-1][0] }}', '{{ rows[-1][1] }}', {{ rows[-1][2] }})
        on conflict (key)
        do update set
            key = excluded.key,
            num = {{ dict_name }}.num + excluded.num;
        """)
        if isinstance(rows, Mapping):
            rows = tuple((key, inn_kpp, num) 
                         for key, (inn_kpp, num) in rows.items())
        elif isinstance(rows, Generator):
            rows = tuple(rows)
        elif isinstance(rows, Sequence):
            rows = rows
        else:
            raise ValueError(f'Неправильный тип rows - `{type(rows)}`.')

        sql = tpl.render({
            'dict_name': self.dict_name,
            'rows': rows
        })
        self.execute(sql)

    def get(self, key: str) -> str:
        sql = f"""
        select num
            from public.{self.dict_name}
            where key = '{key}';
        """
        res = self.select(sql)
        try:
            return res[0][0]
        except IndexError:
            return 0

    def get_innkpp(self, inn_kpp: str) -> List[Tuple[str, int]]:
        sql = f"""
        select key, num
            from public.{self.dict_name}
            where inn_kpp = '{inn_kpp}';
        """
        return self.select(sql)

    @staticmethod
    def gen_key(*args) -> str:
        return ':'.join(str(arg) for arg in args) 


rc = NamedTuple('rc', region_code=str)
fz = NamedTuple('fz', fz=str)
pr = NamedTuple('pr', price_cat=int)
ok = NamedTuple('ok', okpd2_code=str)
okr = NamedTuple('okr', okpd2_code=str, region_code=str)
okc = NamedTuple('okc', okpd2_code=str, customer_inn_kpp=str)
okw = NamedTuple('okw', okpd2_code=str, iswin=bool)
okrw = NamedTuple('okrw', okpd2_code=str, region_code=str, iswin=bool)
okcw = NamedTuple('okcw', okpd2_code=str, customer_inn_kpp=str, iswin=bool)

class KeyInfoBuilder:
    def from_str(self, key: str) -> NamedTuple:
        key_elems = key.split(':')
        if len(key_elems) < 3 or len(key_elems) > 5:
            raise ValueError(f'Структура ключа `{key}` является невалидной.')
        
        if key_elems[0] == 'rc': return self.rc_from_str(key)
        if key_elems[0] == 'fz': return self.fz_from_str(key)
        if key_elems[0] == 'pr': return self.pr_from_str(key)
        if key_elems[0] == 'okw': return self.okw_from_str(key)
        if key_elems[0] == 'okrw': return self.okrw_from_str(key)
        if key_elems[0] == 'okcw': return self.okcw_from_str(key)

        raise ValueError(
            f'Ключ `{key}` содержит неправильный определитель (1 элемент).'
        )

    def rc_from_str(self, key: str) -> rc:
        key_elems = key.split(':')
        if len(key_elems) != 3:
            raise ValueError(f'В ключе `{key}` неправильное кол-во элементов.')
        if key_elems[0] != 'rc':
            raise ValueError(f'Ключ `{key}` имеет неправильную структуру.')
        region_code = key_elems[2]
        return rc(region_code)
    
    def fz_from_str(self, key: str) -> fz:
        key_elems = key.split(':')
        if len(key_elems) != 3:
            raise ValueError(f'В ключе `{key}` неправильное кол-во элементов.')
        if key_elems[0] != 'fz':
            raise ValueError(f'Ключ `{key}` имеет неправильную структуру.')
        fz_ = key_elems[2]
        return fz(fz_)

    def pr_from_str(self, key: str) -> pr:
        key_elems = key.split(':')
        if len(key_elems) != 3:
            raise ValueError(f'В ключе `{key}` неправильное кол-во элементов.')
        if key_elems[0] != 'pr':
            raise ValueError(f'Ключ `{key}` имеет неправильную структуру.')
        price_cat = int(key_elems[2])
        return pr(price_cat)

    def okw_from_str(self, key: str) -> rc:
        key_elems = key.split(':')
        if len(key_elems) != 4:
            raise ValueError(f'В ключе `{key}` неправильное кол-во элементов.')
        if key_elems[0] != 'okw':
            raise ValueError(f'Ключ `{key}` имеет неправильную структуру.')
        okpd2_code = key_elems[2]
        iswin = self.parse_iswin(key_elems[3])
        return okw(okpd2_code, iswin)

    def okrw_from_str(self, key: str) -> rc:
        key_elems = key.split(':')
        if len(key_elems) != 5:
            raise ValueError(f'В ключе `{key}` неправильное кол-во элементов.')
        if key_elems[0] != 'okrw':
            raise ValueError(f'Ключ `{key}` имеет неправильную структуру.')
        okpd2_code = key_elems[2]
        region_code = key_elems[3]
        iswin = self.parse_iswin(key_elems[4])
        return okrw(okpd2_code, region_code, iswin)

    def okcw_from_str(self, key: str) -> rc:
        key_elems = key.split(':')
        if len(key_elems) != 5:
            raise ValueError(f'В ключе `{key}` неправильное кол-во элементов.')
        if key_elems[0] != 'okcw':
            raise ValueError(f'Ключ `{key}` имеет неправильную структуру.')
        okpd2_code = key_elems[2]
        customer_inn_kpp = key_elems[3]
        iswin = self.parse_iswin(key_elems[4])
        return okcw(okpd2_code, customer_inn_kpp, iswin)

    def parse_iswin(self, iswin: str) -> bool:
        if iswin == 'True':
            iswin = True
        elif iswin == 'False':
            iswin = False
        else:
            try:
                iswin = bool(int(iswin))
            except ValueError:
                raise ValueError(f'iswin `{iswin}` записан некорректно.')
        return iswin

    @staticmethod
    def gen_key(*args) -> str:
        return ':'.join(str(arg) for arg in args) 
