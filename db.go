package recsys

import (
	"database/sql"
	"fmt"
	"strings"

	_ "github.com/lib/pq"
)

type RecSysDataBase struct {
	db *sql.DB
}

func NewRecSysDataBase(host, port, user, dbname, password string) (*RecSysDataBase, error) {
	connStr := fmt.Sprintf(
		"host=%s port=%s user=%s dbname=%s password=%s sslmode=disable",
		host, port, user, dbname, password,
	)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return new(RecSysDataBase), err
	}

	model := RecSysDataBase{db}
	model.CreateSupplierInfo()
	return &model, nil
}

func MustNewRecSysDataBase(host, port, user, dbname, password string) *RecSysDataBase {
	db, err := NewRecSysDataBase(host, port, user, dbname, password)
	if err != nil {
		panic(err.Error())
	}
	return db
}

func (db RecSysDataBase) Close() {
	db.Close()
}

func (db RecSysDataBase) CreateSupplierInfo(args ...string) {
	if len(args) > 1 {
		err := fmt.Sprintf("Len args can't be more than 1, get %v", len(args))
		panic(err)
	}

	_, err := db.db.Exec(`
	create table if not exists go_recsys.supplier_info
	(
		key varchar(100) primary key,
		inn_kpp varchar(22),
		num int
	)`)
	if err != nil {
		panic(err.Error())
	}

	var index_name string
	if len(args) == 1 {
		index_name = args[0]
	} else {
		index_name = "supplier_info_inn_kpp_index"
	}
	_, err = db.db.Exec(fmt.Sprintf(`
	create index if not exists %s on go_recsys.supplier_info using btree (inn_kpp)
	`, index_name))
	if err != nil {
		panic(err.Error())
	}
}

func (db RecSysDataBase) ClearSupplierInfo() {
	var c int
	row := db.db.QueryRow(`
	select count(*)
		from pg_catalog.pg_tables
		where tablename = 'supplier_info'
	`)
	if err := row.Scan(&c); err != nil {
		panic(err.Error())
	}

	if c == 0 {
		return
	}

	_, err := db.db.Exec(`truncate table go_recsys.supplier_info`)
	if err != nil {
		panic(err.Error())
	}
}

func (db RecSysDataBase) Incr(key string, v int) {
	inn_kpp := strings.SplitN(key, ":", 3)[1]
	_, err := db.db.Exec(fmt.Sprintf(`
	insert into go_recsys.supplier_info values
	('%s', '%s', %v)
	on conflict (key)
	do update set
		key = excluded.key,
		num = go_recsys.supplier_info.num + excluded.num
	`, key, inn_kpp, v))
	if err != nil {
		panic(err.Error())
	}
}
