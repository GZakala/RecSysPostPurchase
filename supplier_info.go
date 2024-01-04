package recsys

import (
	"encoding/json"
	"os"
)

var mspReestr map[string]bool

func init() {
	f, err := os.ReadFile("msp_inn_reestr.json")
	if err != nil {
		panic(err.Error())
	}
	d := []string{}
	json.Unmarshal(f, &d)
	for _, innKpp := range d {
		mspReestr[innKpp] = true
	}
}

type SupplierInfo struct {
	InnKpp string
	MSP    bool
	Info   *NCounter
}

func NewSupplierInfo(innKpp string) *SupplierInfo {
	msp, _ := mspReestr[innKpp]
	return &SupplierInfo{InnKpp: innKpp, MSP: msp, Info: new(NCounter)}
}

type KeyNumRows []struct {
	Key string
	Num int
}

func FromRowsSupplierInfo(innKpp string, rows KeyNumRows) *SupplierInfo {
	si := new(SupplierInfo)
	var keyInfo KeyInterface
	keyBuilder := KeyBuilder{}
	for _, row := range rows {
		keyInfo = keyBuilder.
	}
}
