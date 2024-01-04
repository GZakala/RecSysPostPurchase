package main

import (
	"encoding/json"
	"fmt"
	"os"
)

func main() {
	d, err := os.ReadFile("./dep/msp_inn_reestr.json")
	if err != nil {
		panic(err.Error())
	}

	f := []string{}
	json.Unmarshal(d, &f)
	fmt.Println(f[:3])

	// d := []string{}
	// f, err := os.ReadFile(s)
	// if err != nil {
	// 	panic(err.Error())
	// }
	// err = json.Unmarshal(f, &d)
	// if err != nil {
	// 	panic(err.Error())
	// }
	// fmt.Println(d[:10])
}
