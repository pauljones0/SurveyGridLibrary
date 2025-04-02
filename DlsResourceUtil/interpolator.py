"""Contains functions to interpolate missing section corner coordinates."""

SECTION_HEIGHT_IN_DEGREES = 0.014398614  # Geodetic height of one section's latitude in degrees

def _interpolate(x0: float, y0: float, x1: float, y1: float, z: float) -> float:
    """Linear interpolation between two points."""
    # Avoid division by zero if x0 == x1
    if x0 == x1:
        return y0 # Or y1, they should be the same or close if x0 == x1
    return (z - x1) * y0 / (x0 - x1) + (z - x0) * y1 / (x1 - x0)

def _get_section_width_in_degrees(township: int) -> float:
    """
    Calculate the (east-west) width of a section in decimal degrees.

    Estimates the width by interpolating based on known widths at 
    townships 10 and 80.
    """
    # Reference points: (township, width_in_degrees)
    return _interpolate(10, -0.02255, 80, -0.026093, township)


# block is [SELat, SELon, SWLat, SWLon, NWLat, NWLon, NELat, NELon]

def interpolate3(block: list[float]) -> list[float]:
    """Interpolates coordinates when 3 out of 4 corners are known."""
    has_se = block[0] != 0.0 or block[1] != 0.0
    has_sw = block[2] != 0.0 or block[3] != 0.0
    has_nw = block[4] != 0.0 or block[5] != 0.0
    has_ne = block[6] != 0.0 or block[7] != 0.0

    latlong = [0.0] * 8

    if has_se and has_sw and has_nw:  # Missing NE
        latlong[0], latlong[1] = block[0], block[1] # SE
        latlong[2], latlong[3] = block[2], block[3] # SW
        latlong[4], latlong[5] = block[4], block[5] # NW
        latlong[6] = latlong[0] + latlong[4] - latlong[2]  # Interpolate NELat
        latlong[7] = latlong[1] + latlong[5] - latlong[3]  # Interpolate NELon
    elif has_se and has_sw and has_ne: # Missing NW
        latlong[0], latlong[1] = block[0], block[1] # SE
        latlong[2], latlong[3] = block[2], block[3] # SW
        latlong[6], latlong[7] = block[6], block[7] # NE
        latlong[4] = latlong[2] + latlong[6] - latlong[0]  # Interpolate NWLat
        latlong[5] = latlong[3] + latlong[7] - latlong[1]  # Interpolate NWLon
    elif has_sw and has_nw and has_ne: # Missing SE
        latlong[2], latlong[3] = block[2], block[3] # SW
        latlong[4], latlong[5] = block[4], block[5] # NW
        latlong[6], latlong[7] = block[6], block[7] # NE
        latlong[0] = latlong[2] + latlong[6] - latlong[4]  # Interpolate SELat
        latlong[1] = latlong[3] + latlong[7] - latlong[5]  # Interpolate SELon
    elif has_se and has_nw and has_ne: # Missing SW
        latlong[0], latlong[1] = block[0], block[1] # SE
        latlong[4], latlong[5] = block[4], block[5] # NW
        latlong[6], latlong[7] = block[6], block[7] # NE
        latlong[2] = latlong[0] + latlong[4] - latlong[6]  # Interpolate SWLat
        latlong[3] = latlong[1] + latlong[5] - latlong[7]  # Interpolate SWLon
    else:
         # Should not happen if called correctly with 3 points
         # Keep original block or raise error?
         # Raising an error might be safer depending on expected guarantees
         # For now, return potentially incomplete block to match C# behavior implicitly
         return block 

    return latlong


def interpolate2(township: int, block: list[float]) -> list[float]:
    """Interpolates coordinates when 2 out of 4 corners are known."""
    has_se = block[0] != 0.0 or block[1] != 0.0
    has_sw = block[2] != 0.0 or block[3] != 0.0
    has_nw = block[4] != 0.0 or block[5] != 0.0
    has_ne = block[6] != 0.0 or block[7] != 0.0

    latlong = [0.0] * 8
    section_longitude_width = _get_section_width_in_degrees(township)

    # Matrix layout: NW(4,5) NE(6,7) / SW(2,3) SE(0,1)

    if has_ne and has_nw: # Known North edge
        latlong[6], latlong[7] = block[6], block[7] # NE
        latlong[4], latlong[5] = block[4], block[5] # NW
        latlong[0] = latlong[6] - SECTION_HEIGHT_IN_DEGREES # SE Lat
        latlong[2] = latlong[4] - SECTION_HEIGHT_IN_DEGREES # SW Lat
        latlong[1] = latlong[7] # SE Lon
        latlong[3] = latlong[5] # SW Lon
    elif has_ne and has_se: # Known East edge
        latlong[6], latlong[7] = block[6], block[7] # NE
        latlong[0], latlong[1] = block[0], block[1] # SE
        latlong[4] = latlong[6] # NW Lat
        latlong[2] = latlong[0] # SW Lat
        latlong[5] = latlong[7] + section_longitude_width # NW Lon
        latlong[3] = latlong[1] + section_longitude_width # SW Lon
    elif has_ne and has_sw: # Known diagonal NE-SW
        latlong[6], latlong[7] = block[6], block[7] # NE
        latlong[2], latlong[3] = block[2], block[3] # SW
        latlong[4] = latlong[6] # NW Lat
        latlong[0] = latlong[2] # SE Lat
        latlong[5] = latlong[7] + section_longitude_width # NW Lon
        latlong[1] = latlong[3] - section_longitude_width # SE Lon
    elif has_nw and has_sw: # Known West edge
        latlong[4], latlong[5] = block[4], block[5] # NW
        latlong[2], latlong[3] = block[2], block[3] # SW
        latlong[6] = latlong[4] # NE Lat
        latlong[0] = latlong[2] # SE Lat
        latlong[7] = latlong[5] - section_longitude_width # NE Lon
        latlong[1] = latlong[3] - section_longitude_width # SE Lon
    elif has_nw and has_se: # Known diagonal NW-SE
        latlong[4], latlong[5] = block[4], block[5] # NW
        latlong[0], latlong[1] = block[0], block[1] # SE
        latlong[6] = latlong[0] + SECTION_HEIGHT_IN_DEGREES # NE Lat
        latlong[2] = latlong[4] - SECTION_HEIGHT_IN_DEGREES # SW Lat
        latlong[7] = latlong[5] - section_longitude_width # NE Lon
        latlong[3] = latlong[1] + section_longitude_width # SW Lon
    elif has_sw and has_se: # Known South edge
        latlong[2], latlong[3] = block[2], block[3] # SW
        latlong[0], latlong[1] = block[0], block[1] # SE
        latlong[6] = latlong[0] + SECTION_HEIGHT_IN_DEGREES # NE Lat
        latlong[4] = latlong[2] + SECTION_HEIGHT_IN_DEGREES # NW Lat
        latlong[7] = latlong[1] # NE Lon
        latlong[5] = latlong[3] # NW Lon
    else:
        # Should not happen if called correctly with 2 points
        # Return potentially incomplete block
        return block

    return latlong


def interpolate1(township: int, block: list[float]) -> list[float]:
    """Interpolates coordinates when only 1 corner is known."""
    has_se = block[0] != 0.0 or block[1] != 0.0
    has_sw = block[2] != 0.0 or block[3] != 0.0
    has_nw = block[4] != 0.0 or block[5] != 0.0
    has_ne = block[6] != 0.0 or block[7] != 0.0

    latlong = [0.0] * 8
    section_longitude_width = _get_section_width_in_degrees(township)

    if has_ne:
        latlong[6], latlong[7] = block[6], block[7] # NE
        latlong[4] = latlong[6] # NW Lat
        latlong[5] = latlong[7] + section_longitude_width # NW Lon
        latlong[0] = latlong[6] - SECTION_HEIGHT_IN_DEGREES # SE Lat
        latlong[1] = latlong[7] # SE Lon
        latlong[2] = latlong[0] # SW Lat = SE Lat
        latlong[3] = latlong[5] # SW Lon = NW Lon
    elif has_nw:
        latlong[4], latlong[5] = block[4], block[5] # NW
        latlong[6] = latlong[4] # NE Lat
        latlong[7] = latlong[5] - section_longitude_width # NE Lon
        latlong[2] = latlong[4] - SECTION_HEIGHT_IN_DEGREES # SW Lat
        latlong[3] = latlong[5] # SW Lon
        latlong[0] = latlong[2] # SE Lat = SW Lat
        latlong[1] = latlong[7] # SE Lon = NE Lon
    elif has_se:
        latlong[0], latlong[1] = block[0], block[1] # SE
        latlong[6] = latlong[0] + SECTION_HEIGHT_IN_DEGREES # NE Lat
        latlong[7] = latlong[1] # NE Lon
        latlong[2] = latlong[0] # SW Lat
        latlong[3] = latlong[1] + section_longitude_width # SW Lon
        latlong[4] = latlong[6] # NW Lat = NE Lat
        latlong[5] = latlong[3] # NW Lon = SW Lon
    elif has_sw:
        latlong[2], latlong[3] = block[2], block[3] # SW
        latlong[4] = latlong[2] + SECTION_HEIGHT_IN_DEGREES # NW Lat
        latlong[5] = latlong[3] # NW Lon
        latlong[0] = latlong[2] # SE Lat
        latlong[1] = latlong[3] - section_longitude_width # SE Lon
        latlong[6] = latlong[4] # NE Lat = NW Lat
        latlong[7] = latlong[1] # NE Lon = SE Lon
    else:
         # Should not happen if called correctly with 1 point
         # Return potentially incomplete block
        return block

    return latlong 