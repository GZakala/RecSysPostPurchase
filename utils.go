package recsys

import (
	"regexp"
	"strconv"
	"strings"
)

func getPriceCat(price float64) int {
	var price_cat int
	switch {
	case price < 400_000:
		price_cat = 0
	case price < 1_000_000:
		price_cat = 1
	case price < 5_000_000:
		price_cat = 2
	case price < 20_000_000:
		price_cat = 3
	case price < 100_000_000:
		price_cat = 4
	case price < 1_000_000_000:
		price_cat = 5
	default:
		price_cat = 6
	}
	return price_cat
}

func validateRegionCode(region_code string) bool {
	int_region_code, err := strconv.Atoi(region_code)
	if err != nil || int_region_code < 1 || int_region_code > 200 {
		return false
	}
	return true
}

func validateFZ(fz string) bool {
	if fz != "44fz" && fz != "223fz" && fz != "com" && fz != "atom" {
		return false
	}
	return true
}

func validateOkpd2Code(okpd2_code string) bool {
	pattern := `^[0-9]{2}$`
	pattern += `|^[0-9]{2}\.[0-9]{1,2}$`
	pattern += `|^[0-9]{2}\.[0-9]{2}\.[0-9]{1,2}$`
	pattern += `|^[0-9]{2}\.[0-9]{2}\.[0-9]{2}\.[0-9]{1,3}$`
	r := regexp.MustCompile(pattern)
	return r.MatchString(okpd2_code)
}

func prepareOkpd2Code(okpd2_code string) string {
	re_okpd2 := regexp.MustCompile(`[0.]+$`)
	okpd2_code = re_okpd2.ReplaceAllString(okpd2_code, "")
	if len(okpd2_code) == 1 {
		okpd2_code = okpd2_code + "0"
	} else if len(okpd2_code) > 8 && len(okpd2_code) < 12 {
		okpd2_code += strings.Repeat("0", 12-len(okpd2_code))
	}
	return okpd2_code
}

func prepareOkpd2Codes(okpd2_codes []string) []string {
	prepared_okpd2_codes := make([]string, 0, len(okpd2_codes))
	var prepared_okpd2_code string
	for _, okpd2_code := range okpd2_codes {
		prepared_okpd2_code = prepareOkpd2Code(okpd2_code)
		prepared_okpd2_codes = append(prepared_okpd2_codes, prepared_okpd2_code)
	}
	return prepared_okpd2_codes
}
