import iso3166

def check_type(x):
    return int(x) in (-1, 0, 1)

def check_region(x):
    return x.upper() in iso3166.countries_by_alpha2
