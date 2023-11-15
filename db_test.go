package recsys

import (
	"fmt"
	"testing"
)

var db *RecSysDataBase = MustNewRecSysDataBase(
	"localhost", "5432", "postgres", "postgres", "12345")

func TestNewRecSysDataBase(t *testing.T) {
	db, err := NewRecSysDataBase(
		"localhost", "5432", "postgres", "postgres", "12345")
	if err != nil {
		t.Error(err)
	}
	db.db.Close()
}

func renameTable(old_name, new_name string) {
	_, err := db.db.Exec(fmt.Sprintf(`
	alter table if exists go_recsys.%s
		rename to %s
	`, old_name, new_name))
	if err != nil {
		panic(err.Error())
	}
}

func createTable(name string) {
	_, err := db.db.Exec(fmt.Sprintf(`
	create table go_recsys.%s
	(
		key varchar(100) primary key,
		inn_kpp varchar(22),
		num int not null
	)
	`, name))
	if err != nil {
		panic(err.Error())
	}

	_, err = db.db.Exec(fmt.Sprintf(`
	create index index_%s_inn_kpp on go_recsys.supplier_info(inn_kpp)
	`, name))
	if err != nil {
		panic(err.Error())
	}
}

func dropTable(name string) {
	_, err := db.db.Exec(fmt.Sprintf(`
	drop table if exists go_recsys.%s
	`, name))
	if err != nil {
		panic(err.Error())
	}
}

func selectCount() int {
	var v int
	row := db.db.QueryRow(`
	select count(*)
		from go_recsys.supplier_info
	`)
	if err := row.Scan(&v); err != nil {
		panic(err.Error())
	}
	return v
}

func selectNum(key string) int {
	var v int
	row := db.db.QueryRow(fmt.Sprintf(`
	select num
		from go_recsys.supplier_info
		where key = '%s'
	`, key))
	if err := row.Scan(&v); err != nil {
		panic(err.Error())
	}
	return v
}

func TestCreateSupplierInfo(t *testing.T) {
	renameTable("supplier_info", "temp_supplier_info")
	createTable("supplier_info")
	defer renameTable("temp_supplier_info", "supplier_info")
	defer dropTable("supplier_info")

	row := db.db.QueryRow(`
	select count(*) 
		from pg_catalog.pg_tables
		where tablename = 'supplier_info'
	`)
	var c int
	if err := row.Scan(&c); err != nil {
		panic(err.Error())
	}
}

func TestClearSupplierInfo(t *testing.T) {
	renameTable("supplier_info", "temp_supplier_info")
	createTable("supplier_info")
	defer renameTable("temp_supplier_info", "supplier_info")
	defer dropTable("supplier_info")

	_, err := db.db.Exec(`
	insert into go_recsys.supplier_info values
	('1', '1', 1),
	('2', '2', 2),
	('3', '3', 3),
	('4', '4', 4)
	`)
	if err != nil {
		panic(err.Error())
	}

	if c := selectCount(); c != 4 {
		panic(fmt.Sprintf("Bad insert into supplier_info, must 4, get %v", c))
	}
	db.ClearSupplierInfo()
	if c := selectCount(); c != 0 {
		t.Errorf("Num rows must be 0, get %v", c)
	}
}

func TestIncr(t *testing.T) {
	renameTable("supplier_info", "temp_supplier_info")
	createTable("supplier_info")
	defer renameTable("temp_supplier_info", "supplier_info")
	defer dropTable("supplier_info")

	var v int

	if v = selectCount(); v != 0 {
		t.Errorf("Count rows must be 0, get %v", v)
	}

	db.Incr("pr:1:1", 1)
	if v = selectCount(); v != 1 {
		t.Errorf("Count rows must be 1, get %v", v)
	}

	if v = selectNum("pr:1:1"); v != 1 {
		t.Errorf("Num must be 1, get %v", v)
	}

	db.Incr("pr:1:1", 10)
	if v = selectCount(); v != 1 {
		t.Errorf("Count rows must be 0, get %v", v)
	}
	if v = selectNum("pr:1:1"); v != 11 {
		t.Errorf("Num must be 11, get %v", v)
	}

	db.Incr("pr:1:2", 5)
	if v = selectCount(); v != 2 {
		t.Errorf("Count rows must be 2, get %v", v)
	}
	if v = selectNum("pr:1:1"); v != 11 {
		t.Errorf("Num must be 11, get %v", v)
	}
	if v = selectNum("pr:1:2"); v != 5 {
		t.Errorf("Num must be 5, get %v", v)
	}
}

func TestIncrby(t *testing.T) {
	renameTable("supplier_info", "temp_supplier_info")
	createTable("supplier_info")
	defer renameTable("temp_supplier_info", "supplier_info")
	defer dropTable("supplier_info")

	var v int

	if v = selectCount(); v != 0 {
		t.Errorf("Num rows must be 0, get %v", v)
	}

	db.IncrBy([]IncrByData{
		{"pr:1:1", "1_1", 1},
		{"pr:1:2", "1_1", 2},
	})
	if v = selectCount(); v != 2 {
		t.Errorf("Count rows must be 2, get %v", v)
	}
	if v = selectNum("pr:1:1"); v != 1 {
		t.Errorf("Num must be 1, get %v", v)
	}
	if v = selectNum("pr:1:2"); v != 2 {
		t.Errorf("Num must be 2, get %v", v)
	}

	db.IncrBy([]IncrByData{
		{"pr:1:1", "1_1", 3},
		{"pr:1:2", "1_1", 3},
		{"pr:1:3", "1_1", 1},
	})
	if v = selectCount(); v != 3 {
		t.Errorf("Count rows must be 3, get %v", v)
	}
	if v = selectNum("pr:1:1"); v != 4 {
		t.Errorf("Num must be 4, get %v", v)
	}
	if v = selectNum("pr:1:2"); v != 5 {
		t.Errorf("Num must be 5, get %v", v)
	}
	if v = selectNum("pr:1:3"); v != 1 {
		t.Errorf("Num must be 1, get %v", v)
	}
}

//     def test_get(self):
//         db.create_dict()

//         sql = f"""
//         delete from public.{db.dict_name}
//             where key = 'test_id';
//         """
//         db.execute(sql)

//         assert db.get('test_id') == 0
//         db.incr('test_id', 'test_inn_kpp')
//         assert db.get('test_id') == 1
//         db.execute(sql)

//     def test_get_innkpp(self):
//         db.create_dict()

//         sql = f"""
//         delete from public.{db.dict_name}
//             where key = 'test_id';
//         """
//         db.execute(sql)

//         assert db.get_innkpp('test_innkpp') == []
//         db.incr('test_id', 'test_innkpp')
//         assert db.get_innkpp('test_innkpp') == [('test_id', 1)]
//         db.execute(sql)

//     def test_gen_key(self):
//         assert db.gen_key(1, True, False, 's') == '1:True:False:s'
//         assert db.gen_key() == ''
//         assert db.gen_key('11111_11111', '11.11.11.111', '09', 6) == '11111_11111:11.11.11.111:09:6'

// class TestKeyInfoBuilder:
//     @pytest.mark.parametrize(
//         ('key', 'class_or_except'),
//         [
//             ('rc:7810098244_781001001:23', rc),
//             ('fz:7115500500_711501001:44fz', fz),
//             ('pr:7512000253_751201001:1', pr),
//             ('okw:7810098244_781001001:26.70.22.150:True', okw),
//             ('okrw:7115500500_711501001:20.14.75:48:True', okrw),
//             ('okcw:7512000253_751201001:19.20.21.100:7512004191_751201001:True', okcw),
//             ('rc:7810098244_781001001:23:True', 'except'),
//             ('fz', 'except'),
//             ('7512000253_751201001:1', 'except'),
//             ('ok:7810098244_781001001:26.70.22.150:True::::', 'except'),
//         ]
//     )
//     def test_from_str(self, key, class_or_except):
//         if class_or_except == 'except':
//             try:
//                 keyinfo_builder.from_str(key)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert isinstance(keyinfo_builder.from_str(key), class_or_except)

//     @pytest.mark.parametrize(
//         ('key', 'res_or_except'),
//         [
//             ('rc:7810098244_781001001:23', rc('23')),
//             ('rc:7810098244_781001001:01', rc('01')),
//             ('rc:20:7810098244_781001001:01', 'except'),
//             ('rc:01', 'except'),
//             ('fz:7115500500_711501001:44fz', 'except'),
//         ]
//     )
//     def test_rc_from_str(self, key, res_or_except):
//         if res_or_except == 'except':
//             try:
//                 keyinfo_builder.rc_from_str(key)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert keyinfo_builder.rc_from_str(key) == res_or_except
//             assert isinstance(keyinfo_builder.rc_from_str(key), rc)

//     @pytest.mark.parametrize(
//         ('key', 'res_or_except'),
//         [
//             ('fz:7810098244_781001001:44fz', fz('44fz')),
//             ('fz:7810098244_781001001:223fz', fz('223fz')),
//             ('fz:20:7810098244_781001001:44fz', 'except'),
//             ('fz:223fz', 'except'),
//             ('rc:7115500500_711501001:01', 'except'),
//         ]
//     )
//     def test_fz_from_str(self, key, res_or_except):
//         if res_or_except == 'except':
//             try:
//                 keyinfo_builder.fz_from_str(key)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert keyinfo_builder.fz_from_str(key) == res_or_except
//             assert isinstance(keyinfo_builder.fz_from_str(key), fz)

//     @pytest.mark.parametrize(
//         ('key', 'res_or_except'),
//         [
//             ('pr:7810098244_781001001:1', pr(1)),
//             ('pr:7810098244_781001001:2', pr(2)),
//             ('pr:20:7810098244_781001001:3', 'except'),
//             ('pr:4', 'except'),
//             ('rc:7115500500_711501001:1', 'except'),
//         ]
//     )
//     def test_pr_from_str(self, key, res_or_except):
//         if res_or_except == 'except':
//             try:
//                 keyinfo_builder.pr_from_str(key)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert keyinfo_builder.pr_from_str(key) == res_or_except
//             assert isinstance(keyinfo_builder.pr_from_str(key), pr)

//     @pytest.mark.parametrize(
//         ('key', 'res_or_except'),
//         [
//             ('okw:7810098244_781001001:22.22.14:True', okw('22.22.14', True)),
//             ('okw:7810098244_781001001:11.11.11:False', okw('11.11.11', False)),
//             ('okw:7810098244_781001001:10.12.32.100:1', okw('10.12.32.100', True)),
//             ('okw:7810098244_781001001:10.12.32.100:0', okw('10.12.32.100', False)),
//             ('okw:7810098244_781001001:10.12.32.100:Правда', 'except'),
//             ('okw:7810098244_781001001:10.12.32.100:21:11', 'except'),
//             ('okw:7810098244_781001001:10.12.32.100', 'except'),
//             ('rc:7115500500_711501001:1:True', 'except'),
//         ]
//     )
//     def test_okw_from_str(self, key, res_or_except):
//         if res_or_except == 'except':
//             try:
//                 keyinfo_builder.okw_from_str(key)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert keyinfo_builder.okw_from_str(key) == res_or_except
//             assert isinstance(keyinfo_builder.okw_from_str(key), okw)

//     @pytest.mark.parametrize(
//         ('key', 'res_or_except'),
//         [
//             ('okrw:7810098244_781001001:22.22.14:01:True', okrw('22.22.14', '01', True)),
//             ('okrw:7810098244_781001001:11.11.11:77:False', okrw('11.11.11', '77', False)),
//             ('okrw:7810098244_781001001:10.12.32.100:01:1', okrw('10.12.32.100', '01', True)),
//             ('okrw:7810098244_781001001:10.12.32.100:90:0', okrw('10.12.32.100', '90', False)),
//             ('okrw:7810098244_781001001:10.12.32.100:67:Правда', 'except'),
//             ('okrw:7810098244_781001001:10.12.32.100:21:11:True', 'except'),
//             ('okrw:7810098244_781001001:10.12.32.100:False', 'except'),
//             ('okw:7115500500_711501001:1:01:True', 'except'),
//         ]
//     )
//     def test_okrw_from_str(self, key, res_or_except):
//         if res_or_except == 'except':
//             try:
//                 keyinfo_builder.okrw_from_str(key)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert keyinfo_builder.okrw_from_str(key) == res_or_except
//             assert isinstance(keyinfo_builder.okrw_from_str(key), okrw)

//     @pytest.mark.parametrize(
//         ('key', 'res_or_except'),
//         [
//             ('okcw:7810098244_781001001:22.22.14:111_111:True', okcw('22.22.14', '111_111', True)),
//             ('okcw:7810098244_781001001:11.11.11:111_111:False', okcw('11.11.11', '111_111', False)),
//             ('okcw:7810098244_781001001:10.12.32.100:111_111:1', okcw('10.12.32.100', '111_111', True)),
//             ('okcw:7810098244_781001001:10.12.32.100:111_111:0', okcw('10.12.32.100', '111_111', False)),
//             ('okcw:7810098244_781001001:11.11.11:111_111:Правда', 'except'),
//             ('okcw:7810098244_781001001:11.11.11:111_111:11:True', 'except'),
//             ('okcw:7810098244_781001001:111_111:False', 'except'),
//             ('okrw:7115500500_711501001:1:01:True', 'except'),
//         ]
//     )
//     def test_okc_from_str(self, key, res_or_except):
//         if res_or_except == 'except':
//             try:
//                 keyinfo_builder.okcw_from_str(key)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert keyinfo_builder.okcw_from_str(key) == res_or_except
//             assert isinstance(keyinfo_builder.okcw_from_str(key), okcw)

//     @pytest.mark.parametrize(
//         ('iswin', 'res_or_except'),
//         [
//             ('True', True),
//             ('False', False),
//             ('10', True),
//             ('1', True),
//             ('0', False),
//             ('true', 'except'),
//             ('false', 'except'),
//             ('t', 'except'),
//             ('f', 'except'),
//             ('', 'except'),

//         ]
//     )
//     def test_parse_iswin(self, iswin, res_or_except):
//         if res_or_except == 'except':
//             try:
//                 keyinfo_builder.parse_iswin(iswin)
//                 assert False
//             except ValueError:
//                 assert True
//         else:
//             assert keyinfo_builder.parse_iswin(iswin) == res_or_except

//     def test_gen_key(self):
//         assert keyinfo_builder.gen_key(1, True, False, 's') == '1:True:False:s'
//         assert keyinfo_builder.gen_key() == ''
//         assert keyinfo_builder.gen_key('11111_11111', '11.11.11.111', '09', 6) == '11111_11111:11.11.11.111:09:6'
