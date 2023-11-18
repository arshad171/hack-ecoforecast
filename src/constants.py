from enum import Enum


REGIONS = [
    "HU",
    "IT",
    "PO",
    "SP",
    "UK",
    "DE",
    "DK",
    "SE",
    "NE",
]

# all renewable energy sources
# refer: https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_psrtype
GREEN_SOURCES = [
    "B01",  # biomass
    "B09",  # geothermal
    "B10",  # hydro pumped
    "B11",  # hydro run-of-river
    "B12",  # hydro water
    "B13",  # marine
    "B15",  # other renewable
    "B16",  # solar
    "B17",  # waste
    "B18",  # wind
    "B19",  # wind
]
