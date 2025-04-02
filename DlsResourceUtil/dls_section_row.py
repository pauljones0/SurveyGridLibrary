from dataclasses import dataclass
from typing import Optional

@dataclass
class DlsSectionRow:
    """
    Represents a row from the DLSSections.csv file, 
    containing coordinate data for a specific section.
    """
    Meridian: int
    Range: int
    Township: int
    Section: int
    SELat: Optional[float] = None
    SELon: Optional[float] = None
    SWLat: Optional[float] = None
    SWLon: Optional[float] = None
    NWLat: Optional[float] = None
    NWLon: Optional[float] = None
    NELat: Optional[float] = None
    NELon: Optional[float] = None 