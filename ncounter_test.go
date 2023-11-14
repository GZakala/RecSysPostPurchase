package recsys

import (
	"testing"
)

var bk KeyBuilder = KeyBuilder{}

func getKeyRC(region_code string) RC {
	k, _ := bk.Region(region_code)
	return k
}
func getKeyFZ(fz string) FZ {
	k, _ := bk.Fz(fz)
	return k
}
func getKeyPR(price float64) PR {
	k, _ := bk.Price(price)
	return k
}
func getKeyOK(okpd2_code string) OK {
	k, _ := bk.Okpd2(okpd2_code)
	return k
}
func getKeyOKW(okpd2_code string, iswin bool) OKW {
	k, _ := bk.Okpd2IsWin(okpd2_code, iswin)
	return k
}

func getKeyOKR(okpd2_code, region_code string) OKR {
	k, _ := bk.Okpd2Region(okpd2_code, region_code)
	return k
}
func getKeyOKRW(okpd2_code, retgion_code string, iswin bool) OKRW {
	k, _ := bk.Okpd2RegionIsWin(okpd2_code, retgion_code, iswin)
	return k
}

func getKeyOKC(okpd2_code, customer_inn_kpp string) OKC {
	k, _ := bk.Okpd2Customer(okpd2_code, customer_inn_kpp)
	return k
}
func getKeyOKCW(okpd2_code, customer_inn_kpp string, iswin bool) OKCW {
	k, _ := bk.Okpd2CustomerIsWin(okpd2_code, customer_inn_kpp, iswin)
	return k
}

func TestNewNCounter(t *testing.T) {
	var elements []KeyInterface
	var nc *NCounter
	var k KeyInterface

	elements = []KeyInterface{
		getKeyRC("77"),
		getKeyRC("77"),
		getKeyRC("77"),
		getKeyRC("01"),
		getKeyRC("01"),
	}
	nc = NewNCounter(elements)
	k = getKeyRC("77")
	if val := (*nc.data)[k]; val.Count() != 3 || val.Norm() != float64(0.6) {
		t.Errorf("Wrong calc RC(77), need (3, 0.6), get (%v, %v)", val.Count(), val.Norm())
	}
	k = getKeyRC("01")
	if val := (*nc.data)[k]; val.Count() != 2 || val.Norm() != float64(0.4) {
		t.Errorf("Wrong calc RC(01), need (2, 0.4), get (%v, %v)", val.Count(), val.Norm())
	}

	elements = []KeyInterface{
		getKeyFZ("223fz"),
		getKeyFZ("223fz"),
		getKeyFZ("223fz"),
		getKeyFZ("44fz"),
		getKeyFZ("44fz"),
		getKeyFZ("44fz"),
		getKeyFZ("com"),
		getKeyFZ("com"),
		getKeyFZ("com"),
		getKeyFZ("atom"),
	}
	nc = NewNCounter(elements)
	k = getKeyFZ("223fz")
	if val := (*nc.data)[k]; val.Count() != 3 || val.Norm() != float64(0.3) {
		t.Errorf("Wrong calc FZ(223fz), need (3, 0.3), get (%v, %v)", val.Count(), val.Norm())
	}
	k = getKeyFZ("44fz")
	if val := (*nc.data)[k]; val.Count() != 3 || val.Norm() != float64(0.3) {
		t.Errorf("Wrong calc FZ(44fz), need (3, 0.3), get (%v, %v)", val.Count(), val.Norm())
	}
	k = getKeyFZ("com")
	if val := (*nc.data)[k]; val.Count() != 3 || val.Norm() != float64(0.3) {
		t.Errorf("Wrong calc FZ(com), need (3, 0.3), get (%v, %v)", val.Count(), val.Norm())
	}
	k = getKeyFZ("atom")
	if val := (*nc.data)[k]; val.Count() != 1 || val.Norm() != float64(0.1) {
		t.Errorf("Wrong calc FZ(atom), need (1, 0.1), get (%v, %v)", val.Count(), val.Norm())
	}
}
