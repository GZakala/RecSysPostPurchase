package recsys

import "testing"

func TestGetPriceCat(t *testing.T) {
	switch {
	case getPriceCat(300_000) != 0:
		t.Error("Invalid price cat")
	case getPriceCat(500_000) != 1:
		t.Error("Invalid price cat")
	case getPriceCat(1_100_000) != 2:
		t.Error("Invalid price cat")
	case getPriceCat(5_100_000) != 3:
		t.Error("Invalid price cat")
	case getPriceCat(20_100_000) != 4:
		t.Error("Invalid price cat")
	case getPriceCat(100_100_000) != 5:
		t.Error("Invalid price cat")
	case getPriceCat(1_100_000_000) != 6:
		t.Error("Invalid price cat")
	}
}

func TestValidateRegionCode(t *testing.T) {
	switch {
	case validateRegionCode("") == true:
		t.Errorf("Error validate ''")
	case validateRegionCode("some") == true:
		t.Errorf("Error validate 'some'")
	case validateRegionCode("-1") == true:
		t.Errorf("Error validate '-1'")
	case validateRegionCode("0") == true:
		t.Errorf("Error validate '0'")
	case validateRegionCode("201") == true:
		t.Errorf("Error validate '101'")
	case validateRegionCode("1") == false:
		t.Errorf("Error validate '1'")
	case validateRegionCode("01") == false:
		t.Errorf("Error validate '01'")
	case validateRegionCode("55") == false:
		t.Errorf("Error validate '55'")
	case validateRegionCode("200") == false:
		t.Errorf("Error validate '100'")
	}
}

func TestValidateFZ(t *testing.T) {
	switch {
	case validateFZ("223fz") == false:
		t.Error("Error validate '223fz'")
	case validateFZ("44fz") == false:
		t.Error("Error validate '44fz'")
	case validateFZ("com") == false:
		t.Error("Error validate 'com'")
	case validateFZ("atom") == false:
		t.Error("Error validate 'atom'")
	case validateFZ("223FZ") == true:
		t.Error("Error validate '223FZ'")
	case validateFZ("44FZ") == true:
		t.Error("Error validate '44FZ'")
	case validateFZ("COM") == true:
		t.Error("Error validate 'COM'")
	case validateFZ("ATOM") == true:
		t.Error("Error validate 'ATOM'")
	case validateFZ("some") == true:
		t.Error("Error validate 'some'")
	case validateFZ("") == true:
		t.Error("Error validate ''")
	case validateFZ("223") == true:
		t.Error("Error validate '223'")
	case validateFZ("44") == true:
		t.Error("Error validate '44'")
	}
}

func TestValidateOkpd2Code(t *testing.T) {
	switch {
	case validateOkpd2Code("10.1") == false:
		t.Errorf("Error validate '10.1'")
	case validateOkpd2Code("10.10") == false:
		t.Errorf("Error validate '10.10'")
	case validateOkpd2Code("10.12.12.100") == false:
		t.Errorf("Error validate '10.12.12.100'")
	case validateOkpd2Code("10.12.12.1000") == true:
		t.Errorf("Error validate '10.12.12.1000'")
	case validateOkpd2Code("") == true:
		t.Errorf("Error validate ''")
	case validateOkpd2Code("10.111.2") == true:
		t.Errorf("Error validate '10.111.2'")
	case validateOkpd2Code("10.12.") == true:
		t.Errorf("Error validate '10.12.'")
	case validateOkpd2Code("1") == true:
		t.Errorf("Error validate '1'")
	case validateOkpd2Code("10,1") == true:
		t.Errorf("Error validate '10,1'")
	case validateOkpd2Code("aaa") == true:
		t.Errorf("Error validate 'aaa'")
	}
}

func TestPrepareOkpd2Code(t *testing.T) {
	switch {
	case prepareOkpd2Code("11.11.10.000") != "11.11.1":
		t.Error()
	case prepareOkpd2Code("11.11.11.2") != "11.11.11.200":
		t.Error("")
	case prepareOkpd2Code("11.11.10.020") != "11.11.10.020":
		t.Error("")
	case prepareOkpd2Code("10.00.0") != "10":
		t.Error("")
	case prepareOkpd2Code("01.12.10.000") != "01.12.1":
		t.Error("")
	}
}

func TestPrepareOkpd2Codes(t *testing.T) {
	okpd2_codes := []string{
		"11.11.10.000",
		"11.11.11.2",
		"11.11.10.020",
		"10.00.0",
		"01.12.10.000",
	}
	prepared_okpd2_codes := prepareOkpd2Codes(okpd2_codes)
	for i := 0; i < len(okpd2_codes); i++ {
		if prepared_okpd2_code := prepareOkpd2Code(okpd2_codes[i]); prepared_okpd2_code != prepared_okpd2_codes[i] {
			t.Errorf("Error on prepareOkpd2Codes %s != %s", prepared_okpd2_code, okpd2_codes[i])
		}
	}
}
