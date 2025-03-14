import math
from survey_grid_library.coordinate_conversion_exception import CoordinateConversionException
from survey_grid_library.lat_long_coordinate import LatLongCoordinate

class BcNtsGridSystemConverter:
    LatPq = {
        82: 48,
        83: 52,
        92: 48,
        93: 52,
        94: 56,
        102: 48,
        103: 52,
        104: 56,
        114: 56
    }

    LngPq = {
        82: 112,
        83: 112,
        92: 120,
        93: 120,
        94: 120,
        102: 128,
        103: 128,
        104: 128,
        114: 136
    }

    LatLq = {
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'E': 1,
        'F': 1,
        'G': 1,
        'H': 1,
        'I': 2,
        'J': 2,
        'K': 2,
        'L': 2,
        'M': 3,
        'N': 3,
        'O': 3,
        'P': 3
    }

    LngLq = {
        'A': 0,
        'B': 2,
        'C': 4,
        'D': 6,
        'E': 6,
        'F': 4,
        'G': 2,
        'H': 0,
        'I': 0,
        'J': 2,
        'K': 4,
        'L': 6,
        'M': 6,
        'N': 4,
        'O': 2,
        'P': 0
    }

    LatSix = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0.25,
        6: 0.25,
        7: 0.25,
        8: 0.25,
        9: 0.5,
        10: 0.5,
        11: 0.5,
        12: 0.5,
        13: 0.75,
        14: 0.75,
        15: 0.75,
        16: 0.75
    }

    LngSix = {
        1: 0,
        2: 0.5,
        3: 1,
        4: 1.5,
        5: 1.5,
        6: 1,
        7: 0.5,
        8: 0,
        9: 0,
        10: 0.5,
        11: 1,
        12: 1.5,
        13: 1.5,
        14: 1,
        15: 0.5,
        16: 0
    }

    LatZn = {
        'A': 0,
        'B': 0,
        'C': 0,
        'D': 0,
        'E': 1 / 12.0,
        'F': 1 / 12.0,
        'G': 1 / 12.0,
        'H': 1 / 12.0,
        'I': 1 / 6.0,
        'J': 1 / 6.0,
        'K': 1 / 6.0,
        'L': 1 / 6.0
    }

    LngZn = {
        'A': 0,
        'B': 1 / 8.0,
        'C': 1 / 4.0,
        'D': 3 / 8.0,
        'E': 3 / 8.0,
        'F': 1 / 4.0,
        'G': 1 / 8.0,
        'H': 0,
        'I': 0,
        'J': 1 / 8.0,
        'K': 1 / 4.0,
        'L': 3 / 8.0
    }

    LatQtr = {
        'A': 0,
        'B': 1 / 20.0,
        'C': 1 / 20.0,
        'D': 0
    }

    LngQtr = {
        'A': 0,
        'B': 1 / 20.0,
        'C': 1 / 20.0,
        'D': 0
    }

    @staticmethod
    def to_lat_long(bc_nts):
        try:
            latitude = BcNtsGridSystemConverter.LatPq[bc_nts.series]
            longitude = BcNtsGridSystemConverter.LngPq[bc_nts.series]

            latitude += BcNtsGridSystemConverter.LatLq[bc_nts.map_area]
            longitude += BcNtsGridSystemConverter.LngLq[bc_nts.map_area]

            latitude += BcNtsGridSystemConverter.LatSix[bc_nts.sheet]
            longitude += BcNtsGridSystemConverter.LngSix[bc_nts.sheet]

            latitude += BcNtsGridSystemConverter.LatZn[bc_nts.block]
            longitude += BcNtsGridSystemConverter.LngZn[bc_nts.block]

            y = math.ceil((bc_nts.unit - 0.5 - 10.0) / 10.0)
            latitude += y * (1 / 12.0 / 10)
            x = bc_nts.unit - y * 10 - 1
            longitude += x * (1 / 8.0 / 10)

            latitude += BcNtsGridSystemConverter.LatQtr[bc_nts.quarter_unit] + (1 / 12.0 / 10 / 2)
            longitude += BcNtsGridSystemConverter.LngQtr[bc_nts.quarter_unit] + (1 / 8.0 / 10 / 2)

            return LatLongCoordinate(latitude, -longitude)
        except Exception:
            raise CoordinateConversionException("Error while converting BcNtsGridSystem to lat long.")

    @staticmethod
    def from_lat_long_coordinates(coordinate):
        longitude = abs(coordinate.longitude)
        latitude = abs(coordinate.latitude)

        pq = 0
        for key, value in BcNtsGridSystemConverter.LatPq.items():
            if latitude >= value and latitude < value + 4 and longitude >= BcNtsGridSystemConverter.LngPq[key] and longitude < BcNtsGridSystemConverter.LngPq[key] + 8:
                pq = key
                break

        if pq == 0:
            raise CoordinateConversionException("The geographic location is not in a BC primary quadrant.")

        lat = latitude - BcNtsGridSystemConverter.LatPq[pq]
        lng = longitude - BcNtsGridSystemConverter.LngPq[pq]

        lq = '\0'
        for key in BcNtsGridSystemConverter.LatLq.keys():
            if lat >= BcNtsGridSystemConverter.LatLq[key] and lat < BcNtsGridSystemConverter.LatLq[key] + 1 and lng >= BcNtsGridSystemConverter.LngLq[key] and lng < BcNtsGridSystemConverter.LngLq[key] + 2:
                lq = key
                break

        if lq == '\0':
            raise CoordinateConversionException("lq is invalid.")

        lat -= BcNtsGridSystemConverter.LatLq[lq]
        lng -= BcNtsGridSystemConverter.LngLq[lq]

        six = 0
        for key in BcNtsGridSystemConverter.LatSix.keys():
            if lat >= BcNtsGridSystemConverter.LatSix[key] and lat < BcNtsGridSystemConverter.LatSix[key] + 0.25 and lng >= BcNtsGridSystemConverter.LngSix[key] and lng < BcNtsGridSystemConverter.LngSix[key] + 0.5:
                six = key
                break

        if six == 0:
            raise CoordinateConversionException("six is invalid")

        lat -= BcNtsGridSystemConverter.LatSix[six]
        lng -= BcNtsGridSystemConverter.LngSix[six]

        zn = '\0'
        for key in BcNtsGridSystemConverter.LatZn.keys():
            if lat >= BcNtsGridSystemConverter.LatZn[key] and lat < BcNtsGridSystemConverter.LatZn[key] + (1 / 12.0) and lng >= BcNtsGridSystemConverter.LngZn[key] and lng < BcNtsGridSystemConverter.LngZn[key] + (1 / 8.0):
                zn = key
                break

        if zn == '\0':
            raise CoordinateConversionException("Zone is invalid")

        lat -= BcNtsGridSystemConverter.LatZn[zn]
        lng -= BcNtsGridSystemConverter.LngZn[zn]

        y = math.floor(120 * lat)
        x = math.floor(lng / 0.0125)
        unit = x + 1 + y * 10

        lat -= y / 120.0
        lng -= x * 0.0125

        qtr = '\0'
        for key in BcNtsGridSystemConverter.LatQtr.keys():
            if lat >= BcNtsGridSystemConverter.LatQtr[key] and lat < BcNtsGridSystemConverter.LatQtr[key] + (1 / 12.0 / 10 / 2) and lng >= BcNtsGridSystemConverter.LngQtr[key] and lng < BcNtsGridSystemConverter.LngQtr[key] + (1 / 8.0 / 10 / 2):
                qtr = key
                break

        if qtr == '\0':
            raise CoordinateConversionException("Quarter is invalid.")

        return BcNtsGridSystem(qtr, unit, zn, pq, lq, six)
