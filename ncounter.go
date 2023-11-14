package recsys

import (
	"errors"
	"fmt"
)

// Counter с отдельным полем norm, которое считает процентное соотношение
// каждого элемента словаря относительно остальных елементов.
type NCounter struct {
	data *map[KeyInterface]*ValueInfo
}

// Создать новый NCounter на основе среза элементов.
func NewNCounter(elements []KeyInterface) *NCounter {
	nc := NCounter{&map[KeyInterface]*ValueInfo{}}
	nc.Update(elements)
	nc.CalcNorm()
	return &nc
}

// Посчитать нормализованные значения во всех ValueInfo.
func (nc *NCounter) CalcNorm() {
	var sum int = 0
	for _, v := range nc.Values() {
		sum += v.Count()
	}
	for _, v := range nc.Values() {
		v.SetNorm(float64(v.Count()) / float64(sum))
	}
}

func (nc *NCounter) Update(elements []KeyInterface) {
	for _, elem := range elements {
		if _, ok := (*nc.data)[elem]; ok {
			(*nc.data)[elem].AddCount(1)
		} else {
			(*nc.data)[elem] = NewValueInfo(1)
		}
	}
}

// Получить значение по ключу.
func (nc NCounter) Get(k KeyInterface) (*ValueInfo, bool) {
	v, ok := (*nc.data)[k]
	return v, ok
}

// Установить значение по ключу.
func (nc NCounter) Set(k KeyInterface, v ValueInfo) {
	(*nc.data)[k] = &v
}

// Увеличить частотность элемента словаря на 1.
func (nc NCounter) Incr(k KeyInterface, c int) {
	if val, ok := (*nc.data)[k]; ok == true {
		val.AddCount(c)
		(*nc.data)[k] = val
	} else {
		(*nc.data)[k] = NewValueInfo(c)
	}
}

// Получить все ключи словаря.
func (nc NCounter) Keys() []KeyInterface {
	keys := make([]KeyInterface, 0, len(*nc.data))
	for kii := range *nc.data {
		keys = append(keys, kii)
	}
	return keys
}

// Получить все значения словаря.
func (nc NCounter) Values() []*ValueInfo {
	values := make([]*ValueInfo, 0, len(*nc.data))
	for _, v := range *nc.data {
		values = append(values, v)
	}
	return values
}

type item struct {
	KeyInterface
	*ValueInfo
}

// Получить пару ключ - значение словаря.
func (nc NCounter) Items() []item {
	items := make([]item, 0, len(*nc.data))
	for k, v := range *nc.data {
		items = append(items, item{k, v})
	}
	return items
}

// Вывести структуру словаря.
func (nc NCounter) Print() {
	fmt.Print("NCounter{")
	i := 1
	for k, v := range *nc.data {
		fmt.Printf("%s:(%d, %v)", k, v.Count(), v.Norm())
		if i < len(*nc.data) {
			fmt.Print(" ")
		}
		i += 1
	}
	fmt.Println("}")
}

// Строитель ключей для NCounter.
type KeyBuilder struct{}

// Создать ключ RC.
func (kb KeyBuilder) Region(region_code string) (RC, error) {
	if !validateRegionCode(region_code) {
		err := fmt.Sprintf("Bad region_code %s", region_code)
		return RC{}, errors.New(err)
	}
	return RC{region_code}, nil
}

// Создать ключ FZ.
func (kb KeyBuilder) Fz(fz string) (FZ, error) {
	if !validateFZ(fz) {
		err := "FZ must be one of next values {'44fz', '223fz', 'com', 'atom'}, get %s"
		return FZ{}, errors.New(fmt.Sprintf(err, fz))
	}
	return FZ{fz}, nil
}

// Создать ключ PR.
func (kb KeyBuilder) Price(price float64) (PR, error) {
	price_cat := getPriceCat(price)
	return PR{price_cat}, nil
}

// Создать ключ ОК.
func (kb KeyBuilder) Okpd2(okpd2_code string) (OK, error) {
	if !validateOkpd2Code(okpd2_code) {
		err := fmt.Sprintf("okpd2_code '%s' not validate", okpd2_code)
		return OK{}, errors.New(err)
	}
	return OK{okpd2_code}, nil
}

// Создать ключ ОКW.
func (kb KeyBuilder) Okpd2IsWin(okpd2_code string, iswin bool) (OKW, error) {
	if !validateOkpd2Code(okpd2_code) {
		err := fmt.Sprintf("okpd2_code '%s' not validate", okpd2_code)
		return OKW{}, errors.New(err)
	}
	return OKW{okpd2_code, iswin}, nil
}

// Создать ключ OKR.
func (kb KeyBuilder) Okpd2Region(okpd2_code, region_code string) (OKR, error) {
	if !validateOkpd2Code(okpd2_code) {
		err := fmt.Sprintf("okpd2_code '%s' not validate", okpd2_code)
		return OKR{}, errors.New(err)
	}
	return OKR{okpd2_code, region_code}, nil
}

// Создать ключ OKRW.
func (kb KeyBuilder) Okpd2RegionIsWin(okpd2_code, region_code string, iswin bool) (OKRW, error) {
	if !validateOkpd2Code(okpd2_code) {
		err := fmt.Sprintf("okpd2_code '%s' not validate", okpd2_code)
		return OKRW{}, errors.New(err)
	}
	if !validateRegionCode(region_code) {
		err := fmt.Sprintf("Bad region_code %s", region_code)
		return OKRW{}, errors.New(err)
	}
	return OKRW{okpd2_code, region_code, iswin}, nil
}

// Создать ключ OKC.
func (kb KeyBuilder) Okpd2Customer(okpd2_code, customer string) (OKC, error) {
	if !validateOkpd2Code(okpd2_code) {
		err := fmt.Sprintf("okpd2_code '%s' not validate", okpd2_code)
		return OKC{}, errors.New(err)
	}
	return OKC{okpd2_code, customer}, nil
}

// Создать ключ OKCW.
func (kb KeyBuilder) Okpd2CustomerIsWin(okpd2_code, customer string, iswin bool) (OKCW, error) {
	if !validateOkpd2Code(okpd2_code) {
		err := fmt.Sprintf("okpd2_code '%s' not validate", okpd2_code)
		return OKCW{}, errors.New(err)
	}
	return OKCW{okpd2_code, customer, iswin}, nil
}

type KeyInterface interface{}

// key info region_code
type RC struct {
	region_code string
}

func (k RC) RegionCode() string {
	return k.region_code
}

// key info fz
type FZ struct {
	fz string
}

func (k FZ) FZ() string {
	return k.fz
}

// key info price_cat
type PR struct {
	price_cat int
}

func (k PR) PriceCat() int {
	return k.price_cat
}

// key info okpd2_codes
type OK struct {
	okpd2_code string
}

func (k OK) OKPD2() string {
	return k.okpd2_code
}

// key info okpd2_codes with win
type OKW struct {
	okpd2_code string
	iswin      bool
}

func (k OKW) OKPD2() string {
	return k.okpd2_code
}

func (k OKW) IsWin() bool {
	return k.iswin
}

// key info okpd2_codes with region_code
type OKR struct {
	okpd2_code  string
	region_code string
}

func (k OKR) OKPD2() string {
	return k.okpd2_code
}

func (k OKR) RegionCode() string {
	return k.region_code
}

// key info okpd2_codes with region_code anc iswin
type OKRW struct {
	okpd2_code  string
	region_code string
	iswin       bool
}

func (k OKRW) OKPD2() string {
	return k.okpd2_code
}

func (k OKRW) RegionCode() string {
	return k.region_code
}

func (k OKRW) IsWin() bool {
	return k.iswin
}

// key info okpd2_codes with win
type OKC struct {
	okpd2_code string
	customer   string
}

func (k OKC) OKPD2() string {
	return k.okpd2_code
}

func (k OKC) Customer() string {
	return k.customer
}

// key info okpd2_codes with win
type OKCW struct {
	okpd2_code string
	customer   string
	iswin      bool
}

func (k OKCW) OKPD2() string {
	return k.okpd2_code
}

func (k OKCW) Customer() string {
	return k.customer
}

func (k OKCW) IsWin() bool {
	return k.iswin
}

type ValueInfo struct {
	count int
	norm  float64
}

func NewValueInfo(c int) *ValueInfo {
	return &ValueInfo{c, 0}
}

func (v ValueInfo) Count() int {
	return v.count
}

func (v ValueInfo) Norm() float64 {
	return v.norm
}

func (v *ValueInfo) SetNorm(n float64) {
	v.norm = n
}

func (v *ValueInfo) AddCount(c int) {
	v.count += c
}
