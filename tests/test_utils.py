from tcg_extract.utils import clean_str

def test_clean_str():
    assert clean_str("  Hello   World  ") == "Hello World"
    assert clean_str("Line1\nLine2\t\tLine3") == "Line1 Line2 Line3"
    assert clean_str("\t \n     \t", empty_val="N/A") == "N/A"
    assert clean_str("", empty_val="") == ""