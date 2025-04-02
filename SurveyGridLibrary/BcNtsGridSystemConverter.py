import math
from CoordinateConversionException import CoordinateConversionException
from LatLongCoordinate import LatLongCoordinate
from BcNtsGridSystem import BcNtsGridSystem

class BcNtsGridSystemConverter:
    # Define constants for grid dimensions, mirroring the C# version
    BlockHeight = 1 / 12.0
    BlockWidth = 1 / 8.0
    UnitHeight = BlockHeight / 10
    UnitWidth = BlockWidth / 10
    QuarterUnitHeight = UnitHeight / 2
    QuarterUnitWidth = UnitWidth / 2
    
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
        'E': BlockHeight,
        'F': BlockHeight,
        'G': BlockHeight,
        'H': BlockHeight,
        'I': BlockHeight * 2,
        'J': BlockHeight * 2,
        'K': BlockHeight * 2,
        'L': BlockHeight * 2
    }

    LngZn = {
        'A': 0,
        'B': BlockWidth,
        'C': BlockWidth * 2,
        'D': BlockWidth * 3,
        'E': BlockWidth * 3,
        'F': BlockWidth * 2,
        'G': BlockWidth,
        'H': 0,
        'I': 0,
        'J': BlockWidth,
        'K': BlockWidth * 2,
        'L': BlockWidth * 3
    }

    LatQtr = {
        'A': 0,
        'B': 0,
        'C': QuarterUnitHeight,
        'D': QuarterUnitHeight
    }

    LngQtr = {
        'A': 0,
        'B': QuarterUnitWidth,
        'C': QuarterUnitWidth,
        'D': 0
    }

    @staticmethod
    def to_lat_long(bc_nts: BcNtsGridSystem) -> LatLongCoordinate:
        """
        Approximates the LatLongCoordinate for a given BcNtsGridSystem instance.
        :param bc_nts: The BcNtsGridSystem object to convert.
        :return: A LatLongCoordinate object.
        :raises CoordinateConversionException: If an error occurs during conversion.
        """
        try:
            # Start with the base coordinates from the Series
            latitude = BcNtsGridSystemConverter.LatPq[bc_nts.series]
            longitude = BcNtsGridSystemConverter.LngPq[bc_nts.series]

            # Refine by Map Area
            latitude += BcNtsGridSystemConverter.LatLq[bc_nts.map_area]
            longitude += BcNtsGridSystemConverter.LngLq[bc_nts.map_area]

            # Refine by Sheet
            latitude += BcNtsGridSystemConverter.LatSix[bc_nts.sheet]
            longitude += BcNtsGridSystemConverter.LngSix[bc_nts.sheet]

            # Refine by Block
            latitude += BcNtsGridSystemConverter.LatZn[bc_nts.block]
            longitude += BcNtsGridSystemConverter.LngZn[bc_nts.block]

            # Refine by Unit
            # Calculate the row (y) and column (x) within the block based on the unit number
            y = math.ceil((bc_nts.unit - 0.5 - 10.0) / 10.0) # C# equivalent logic needs verification/adjustment in Python if needed
            latitude += y * BcNtsGridSystemConverter.UnitHeight 
            x = bc_nts.unit - y * 10 - 1
            longitude += x * BcNtsGridSystemConverter.UnitWidth

            # Refine by Quarter Unit and offset to the center
            latitude += BcNtsGridSystemConverter.LatQtr[bc_nts.quarter_unit] + (BcNtsGridSystemConverter.QuarterUnitHeight / 2)
            longitude += BcNtsGridSystemConverter.LngQtr[bc_nts.quarter_unit] + (BcNtsGridSystemConverter.QuarterUnitWidth / 2)

            # Return the final coordinate, inverting the longitude
            return LatLongCoordinate(latitude, -longitude)
        except KeyError as e: # Catch specific key errors from dictionary lookups
             raise CoordinateConversionException(f"Invalid NTS component provided: {e}")
        except Exception as e: # Catch any other unexpected errors
            # Consider logging the original exception e if needed
            raise CoordinateConversionException("Error while converting BcNtsGridSystem to lat long.")

    @staticmethod
    def from_lat_long_coordinates(coordinate: LatLongCoordinate) -> BcNtsGridSystem:
        """
        Converts a LatLongCoordinate instance to a BC NTS location.
        :param coordinate: The LatLongCoordinate object to convert.
        :return: A BcNtsGridSystem object.
        :raises CoordinateConversionException: If the coordinate is outside the BC NTS grid or conversion fails.
        """
        longitude = abs(coordinate.longitude)
        latitude = abs(coordinate.latitude)

        # Find Primary Quadrant (Series)
        pq = 0
        for key, value in BcNtsGridSystemConverter.LatPq.items():
            # Check if the coordinate falls within the bounds of this series
            if latitude >= value and latitude < value + 4 and \
               longitude >= BcNtsGridSystemConverter.LngPq[key] and longitude < BcNtsGridSystemConverter.LngPq[key] + 8:
                pq = key
                break

        if pq == 0:
            raise CoordinateConversionException("The geographic location is not in a BC primary quadrant.")

        # Calculate relative latitude and longitude within the series
        lat = latitude - BcNtsGridSystemConverter.LatPq[pq]
        lng = longitude - BcNtsGridSystemConverter.LngPq[pq]

        # Find Map Area (Letter Quadrant)
        lq = '\0'
        for key in BcNtsGridSystemConverter.LatLq.keys():
             # Check if the relative coordinate falls within the bounds of this map area
            if lat >= BcNtsGridSystemConverter.LatLq[key] and lat < BcNtsGridSystemConverter.LatLq[key] + 1 and \
               lng >= BcNtsGridSystemConverter.LngLq[key] and lng < BcNtsGridSystemConverter.LngLq[key] + 2:
                lq = key
                break

        if lq == '\0':
            # This should theoretically not happen if pq was found correctly, but added for robustness
            raise CoordinateConversionException("Could not determine BC NTS Map Area (lq).")

        # Update relative latitude and longitude within the map area
        lat -= BcNtsGridSystemConverter.LatLq[lq]
        lng -= BcNtsGridSystemConverter.LngLq[lq]

        # Find Sheet (16-unit grid)
        six = 0
        for key in BcNtsGridSystemConverter.LatSix.keys():
            # Check if the relative coordinate falls within the bounds of this sheet
            if lat >= BcNtsGridSystemConverter.LatSix[key] and lat < BcNtsGridSystemConverter.LatSix[key] + 0.25 and \
               lng >= BcNtsGridSystemConverter.LngSix[key] and lng < BcNtsGridSystemConverter.LngSix[key] + 0.5:
                six = key
                break

        if six == 0:
            raise CoordinateConversionException("Could not determine BC NTS Sheet (six).")

        # Update relative latitude and longitude within the sheet
        lat -= BcNtsGridSystemConverter.LatSix[six]
        lng -= BcNtsGridSystemConverter.LngSix[six]

        # Find Block (Zone A-L)
        zn = '\0'
        for key in BcNtsGridSystemConverter.LatZn.keys():
             # Check if the relative coordinate falls within the bounds of this block
            if lat >= BcNtsGridSystemConverter.LatZn[key] and lat < BcNtsGridSystemConverter.LatZn[key] + BcNtsGridSystemConverter.BlockHeight and \
               lng >= BcNtsGridSystemConverter.LngZn[key] and lng < BcNtsGridSystemConverter.LngZn[key] + BcNtsGridSystemConverter.BlockWidth:
                zn = key
                break

        if zn == '\0':
            raise CoordinateConversionException("Could not determine BC NTS Block (Zone).")

        # Update relative latitude and longitude within the block
        lat -= BcNtsGridSystemConverter.LatZn[zn]
        lng -= BcNtsGridSystemConverter.LngZn[zn]

        # Find Unit (1-100)
        # Calculate row (y) and column (x) based on relative lat/lng within the block
        y = math.floor(lat / BcNtsGridSystemConverter.UnitHeight)
        # Prevent y from being 10 if lat is exactly BlockHeight due to floating point precision
        y = min(y, 9)
        x = math.floor(lng / BcNtsGridSystemConverter.UnitWidth)
         # Prevent x from being 10 if lng is exactly BlockWidth
        x = min(x, 9)
        
        # Calculate unit number (1-100) based on row/column
        unit = int(x + 1 + y * 10) # Cast to int for clarity

        # Update relative latitude and longitude within the unit
        lat -= y * BcNtsGridSystemConverter.UnitHeight
        lng -= x * BcNtsGridSystemConverter.UnitWidth

        # Find Quarter Unit (A-D)
        qtr = '\0'
        for key in BcNtsGridSystemConverter.LatQtr.keys():
            # Check if the relative coordinate falls within the bounds of this quarter unit
            # Use a small epsilon for floating point comparisons on the boundaries
            epsilon = 1e-9 
            if lat >= BcNtsGridSystemConverter.LatQtr[key] - epsilon and lat < BcNtsGridSystemConverter.LatQtr[key] + BcNtsGridSystemConverter.QuarterUnitHeight + epsilon and \
               lng >= BcNtsGridSystemConverter.LngQtr[key] - epsilon and lng < BcNtsGridSystemConverter.LngQtr[key] + BcNtsGridSystemConverter.QuarterUnitWidth + epsilon:
                qtr = key
                break

        if qtr == '\0':
             # This might occur due to floating point inaccuracies near boundaries if not handled carefully
            raise CoordinateConversionException("Could not determine BC NTS Quarter Unit.")
            
        # Construct and return the BcNtsGridSystem object
        # Ensure BcNtsGridSystem exists and accepts these parameters in this order.
        return BcNtsGridSystem(quarter_unit=qtr, unit=unit, block=zn, series=pq, map_area=lq, sheet=six)
