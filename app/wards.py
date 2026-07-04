"""Nakuru County wards, grouped by sub-county (constituency).

Source: IEBC / Nakuru County ward listings. Used at signup so a citizen
registers their exact home ward and only gets alerts relevant to it.
"""

WARDS_BY_SUBCOUNTY = {
    "Nakuru Town East": ["Biashara", "Kivumbini", "Flamingo", "Menengai", "Nakuru East"],
    "Nakuru Town West": ["Barut", "London", "Kaptembwo", "Kapkures", "Rhoda", "Shabab"],
    "Naivasha": ["Biashara (Naivasha)", "Hells Gate", "Lakeview", "Maiella",
                 "Mai Mahiu", "Olkaria", "Naivasha East", "Viwandani"],
    "Gilgil": ["Gilgil", "Elementaita", "Mbaruk/Eburu", "Malewa West", "Murindati"],
    "Kuresoi North": ["Kiptagich", "Tinet", "Kamara", "Sirikwa", "Nyota"],
    "Kuresoi South": ["Amalo", "Keringet", "Kiptororo", "Tendwet"],
    "Molo": ["Mariashoni", "Elburgon", "Turi", "Molo"],
    "Njoro": ["Mau Narok", "Mauche", "Kihingo", "Nessuit", "Lare", "Njoro"],
    "Rongai": ["Menengai West", "Soin", "Visoi", "Mosop", "Solai"],
    "Subukia": ["Subukia", "Waseges", "Kabazi"],
    "Bahati": ["Dundori", "Kabatini", "Kiamaina", "Lanet/Umoja", "Bahati"],
}


def wards_for(sub_county: str) -> list[str]:
    return WARDS_BY_SUBCOUNTY.get(sub_county, [])
