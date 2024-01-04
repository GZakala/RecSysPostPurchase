from itertools import product

import sys

from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent))
from db import (
    RecSysDataBase, KeyInfoBuilder, rc, fz, pr, ok, okw, okr, okrw, okc, okcw
)

db = RecSysDataBase()
keyinfo_builder = KeyInfoBuilder()


class TestRecSysDataBase:
    def test_close(self):
        db.close()
        assert db.connection.closed == 1
        db.new_connect()

    def test_new_connect(self):
        old_pid = db.connection.get_backend_pid()
        db.new_connect()
        new_pid = db.connection.get_backend_pid()
        assert old_pid != new_pid

    def test_create_dict(self):
        sql = f"""
        alter table if exists public.{db.dict_name}
            rename to {db.dict_name}_temp;
        """
        db.execute(sql)

        sql = f"""
        select count(*)
            from pg_catalog.pg_tables
            where tablename = '{db.dict_name}';
        """
        assert db.select(sql)[0][0] == 0

        status = db.create_dict()
        assert status == 1
        assert db.select(sql)[0][0] == 1

        status = db.create_dict()
        assert status == 0
        assert db.select(sql)[0][0] == 1

        sql = f"""
        drop table public.{db.dict_name};
        """
        db.execute(sql)

        sql = f"""
        alter table if exists public.{db.dict_name}_temp
            rename to {db.dict_name};
        """
        db.execute(sql)

    def test_clear_dict(self):
        sql = f"""
        alter table if exists public.{db.dict_name}
            rename to {db.dict_name}_temp;
        """
        db.execute(sql)

        sql = f"""
        select count(*)
            from public.{db.dict_name}
        """
        assert db.clear_dict() == 0
        db.create_dict()
        assert db.select(sql)[0][0] == 0
        assert db.clear_dict() == 1
        db.incr('test_id', 'innkpp')
        assert db.select(sql)[0][0] == 1
        assert db.clear_dict() == 1
        assert db.select(sql)[0][0] == 0

        sql = f"""
        drop table public.{db.dict_name};
        """
        db.execute(sql)

        sql = f"""
        alter table if exists public.{db.dict_name}_temp
            rename to {db.dict_name};
        """
        db.execute(sql)

    def test_incr(self):
        db.create_dict()
        
        sql = f"""
        delete from public.{db.dict_name}
            where key = 'test_id';
        """
        db.execute(sql)

        assert db.get('test_id') == 0
        db.incr('test_id', 'innkpp')
        assert db.get('test_id') == 1
        db.incr('test_id', 'innkpp', 10)
        assert db.get('test_id') == 11
        db.execute(sql)

    def test_incrby(self):
        db.create_dict()
        
        sql = f"""
        delete from public.{db.dict_name}
            where key = 'test_id'
                or key = 'test_id2';
        """
        db.execute(sql)

        assert db.get('test_id') == 0
        db.incrby({'test_id': ('innkpp', 1)})
        assert db.get('test_id') == 1
        assert db.get('test_id2') == 0
        db.incrby({'test_id': ('innkpp', 1), 'test_id2': ('innkpp', 5)})
        assert db.get('test_id') == 2
        assert db.get('test_id2') == 5
        db.incrby([('test_id', 'innkpp', 2)])
        assert db.get('test_id') == 4
        assert db.get('test_id2') == 5
        db.incrby([('test_id', 'innkpp', 2), ('test_id2', 'innkpp', 2)])
        assert db.get('test_id') == 6
        assert db.get('test_id2') == 7

        db.execute(sql)

    def test_get(self):
        db.create_dict()
        
        sql = f"""
        delete from public.{db.dict_name}
            where key = 'test_id';
        """
        db.execute(sql)

        assert db.get('test_id') == 0
        db.incr('test_id', 'test_inn_kpp')
        assert db.get('test_id') == 1
        db.execute(sql)

    def test_get_innkpp(self):
        db.create_dict()
        
        sql = f"""
        delete from public.{db.dict_name}
            where key = 'test_id';
        """
        db.execute(sql)

        assert db.get_innkpp('test_innkpp') == []
        db.incr('test_id', 'test_innkpp')
        assert db.get_innkpp('test_innkpp') == [('test_id', 1)]
        db.execute(sql)

    def test_gen_key(self):
        assert db.gen_key(1, True, False, 's') == '1:True:False:s'
        assert db.gen_key() == ''
        assert db.gen_key('11111_11111', '11.11.11.111', '09', 6) == '11111_11111:11.11.11.111:09:6'

class TestKeyInfoBuilder:
    @pytest.mark.parametrize(
        ('key', 'class_or_except'),
        [
            ('rc:7810098244_781001001:23', rc),
            ('fz:7115500500_711501001:44fz', fz),
            ('pr:7512000253_751201001:1', pr),
            ('okw:7810098244_781001001:26.70.22.150:True', okw),
            ('okrw:7115500500_711501001:20.14.75:48:True', okrw),
            ('okcw:7512000253_751201001:19.20.21.100:7512004191_751201001:True', okcw),
            ('rc:7810098244_781001001:23:True', 'except'),
            ('fz', 'except'),
            ('7512000253_751201001:1', 'except'),
            ('ok:7810098244_781001001:26.70.22.150:True::::', 'except'),
        ]
    )
    def test_from_str(self, key, class_or_except):
        if class_or_except == 'except':
            try:
                keyinfo_builder.from_str(key)
                assert False
            except ValueError:
                assert True
        else:
            assert isinstance(keyinfo_builder.from_str(key), class_or_except)

    @pytest.mark.parametrize(
        ('key', 'res_or_except'),
        [
            ('rc:7810098244_781001001:23', rc('23')),
            ('rc:7810098244_781001001:01', rc('01')),
            ('rc:20:7810098244_781001001:01', 'except'),
            ('rc:01', 'except'),
            ('fz:7115500500_711501001:44fz', 'except'),
        ]
    )
    def test_rc_from_str(self, key, res_or_except):
        if res_or_except == 'except':
            try:
                keyinfo_builder.rc_from_str(key)
                assert False
            except ValueError:
                assert True
        else:
            assert keyinfo_builder.rc_from_str(key) == res_or_except
            assert isinstance(keyinfo_builder.rc_from_str(key), rc)

    @pytest.mark.parametrize(
        ('key', 'res_or_except'),
        [
            ('fz:7810098244_781001001:44fz', fz('44fz')),
            ('fz:7810098244_781001001:223fz', fz('223fz')),
            ('fz:20:7810098244_781001001:44fz', 'except'),
            ('fz:223fz', 'except'),
            ('rc:7115500500_711501001:01', 'except'),
        ]
    )
    def test_fz_from_str(self, key, res_or_except):
        if res_or_except == 'except':
            try:
                keyinfo_builder.fz_from_str(key)
                assert False
            except ValueError:
                assert True
        else:
            assert keyinfo_builder.fz_from_str(key) == res_or_except
            assert isinstance(keyinfo_builder.fz_from_str(key), fz)

    @pytest.mark.parametrize(
        ('key', 'res_or_except'),
        [
            ('pr:7810098244_781001001:1', pr(1)),
            ('pr:7810098244_781001001:2', pr(2)),
            ('pr:20:7810098244_781001001:3', 'except'),
            ('pr:4', 'except'),
            ('rc:7115500500_711501001:1', 'except'),
        ]
    )
    def test_pr_from_str(self, key, res_or_except):
        if res_or_except == 'except':
            try:
                keyinfo_builder.pr_from_str(key)
                assert False
            except ValueError:
                assert True
        else:
            assert keyinfo_builder.pr_from_str(key) == res_or_except
            assert isinstance(keyinfo_builder.pr_from_str(key), pr)

    @pytest.mark.parametrize(
        ('key', 'res_or_except'),
        [
            ('okw:7810098244_781001001:22.22.14:True', okw('22.22.14', True)),
            ('okw:7810098244_781001001:11.11.11:False', okw('11.11.11', False)),
            ('okw:7810098244_781001001:10.12.32.100:1', okw('10.12.32.100', True)),
            ('okw:7810098244_781001001:10.12.32.100:0', okw('10.12.32.100', False)),
            ('okw:7810098244_781001001:10.12.32.100:Правда', 'except'),
            ('okw:7810098244_781001001:10.12.32.100:21:11', 'except'),
            ('okw:7810098244_781001001:10.12.32.100', 'except'),
            ('rc:7115500500_711501001:1:True', 'except'),
        ]
    )
    def test_okw_from_str(self, key, res_or_except):
        if res_or_except == 'except':
            try:
                keyinfo_builder.okw_from_str(key)
                assert False
            except ValueError:
                assert True
        else:
            assert keyinfo_builder.okw_from_str(key) == res_or_except
            assert isinstance(keyinfo_builder.okw_from_str(key), okw)

    @pytest.mark.parametrize(
        ('key', 'res_or_except'),
        [
            ('okrw:7810098244_781001001:22.22.14:01:True', okrw('22.22.14', '01', True)),
            ('okrw:7810098244_781001001:11.11.11:77:False', okrw('11.11.11', '77', False)),
            ('okrw:7810098244_781001001:10.12.32.100:01:1', okrw('10.12.32.100', '01', True)),
            ('okrw:7810098244_781001001:10.12.32.100:90:0', okrw('10.12.32.100', '90', False)),
            ('okrw:7810098244_781001001:10.12.32.100:67:Правда', 'except'),
            ('okrw:7810098244_781001001:10.12.32.100:21:11:True', 'except'),
            ('okrw:7810098244_781001001:10.12.32.100:False', 'except'),
            ('okw:7115500500_711501001:1:01:True', 'except'),
        ]
    )
    def test_okrw_from_str(self, key, res_or_except):
        if res_or_except == 'except':
            try:
                keyinfo_builder.okrw_from_str(key)
                assert False
            except ValueError:
                assert True
        else:
            assert keyinfo_builder.okrw_from_str(key) == res_or_except
            assert isinstance(keyinfo_builder.okrw_from_str(key), okrw)

    @pytest.mark.parametrize(
        ('key', 'res_or_except'),
        [
            ('okcw:7810098244_781001001:22.22.14:111_111:True', okcw('22.22.14', '111_111', True)),
            ('okcw:7810098244_781001001:11.11.11:111_111:False', okcw('11.11.11', '111_111', False)),
            ('okcw:7810098244_781001001:10.12.32.100:111_111:1', okcw('10.12.32.100', '111_111', True)),
            ('okcw:7810098244_781001001:10.12.32.100:111_111:0', okcw('10.12.32.100', '111_111', False)),
            ('okcw:7810098244_781001001:11.11.11:111_111:Правда', 'except'),
            ('okcw:7810098244_781001001:11.11.11:111_111:11:True', 'except'),
            ('okcw:7810098244_781001001:111_111:False', 'except'),
            ('okrw:7115500500_711501001:1:01:True', 'except'),
        ]
    )
    def test_okc_from_str(self, key, res_or_except):
        if res_or_except == 'except':
            try:
                keyinfo_builder.okcw_from_str(key)
                assert False
            except ValueError:
                assert True
        else:
            assert keyinfo_builder.okcw_from_str(key) == res_or_except
            assert isinstance(keyinfo_builder.okcw_from_str(key), okcw)

    @pytest.mark.parametrize(
        ('iswin', 'res_or_except'),
        [
            ('True', True),
            ('False', False),
            ('10', True),
            ('1', True),
            ('0', False),
            ('true', 'except'),
            ('false', 'except'),
            ('t', 'except'),
            ('f', 'except'),
            ('', 'except'),

        ]
    )
    def test_parse_iswin(self, iswin, res_or_except):
        if res_or_except == 'except':
            try:
                keyinfo_builder.parse_iswin(iswin)
                assert False
            except ValueError:
                assert True
        else:
            assert keyinfo_builder.parse_iswin(iswin) == res_or_except

    def test_gen_key(self):
        assert keyinfo_builder.gen_key(1, True, False, 's') == '1:True:False:s'
        assert keyinfo_builder.gen_key() == ''
        assert keyinfo_builder.gen_key('11111_11111', '11.11.11.111', '09', 6) == '11111_11111:11.11.11.111:09:6'
