import re
from survey_grid_library.coordinate_parse_exception import CoordinateParseException
from survey_grid_library.lat_long_coordinate import LatLongCoordinate
from survey_grid_library.federal_permit_system import FederalPermitSystem
from survey_grid_library.bc_nts_grid_system import BcNtsGridSystem
from survey_grid_library.dls_system import DlsSystem

class UniqueWellIdentifier:
    def __init__(self, identifier):
        self.identifier = identifier

    @staticmethod
    def parse(identifier):
        if identifier is None:
            raise CoordinateParseException("Cannot parse a null identifier.")
        if not identifier.strip():
            raise CoordinateParseException("Cannot parse an empty identifier.")
        
        if re.match(r'^\d{2}/\d{2}-\d{2}-\d{3}-\d{2}W\d$', identifier):
            return UniqueWellIdentifier.parse_dls(identifier)
        elif re.match(r'^[A-P]-\d{2}/\d{2}-\d{2}-\d{3}-\d{2}$', identifier):
            return UniqueWellIdentifier.parse_federal(identifier)
        elif re.match(r'^[A-D]-\d{3}-[A-L]/\d{3}-[A-P]-\d{2}$', identifier):
            return UniqueWellIdentifier.parse_nts(identifier)
        else:
            raise CoordinateParseException("Unknown identifier format.")

    @staticmethod
    def parse_geodetic(identifier):
        return LatLongCoordinate.from_convertible_string(identifier)

    @staticmethod
    def parse_federal(identifier):
        return FederalPermitSystem.parse(identifier)

    @staticmethod
    def parse_nts(identifier):
        return BcNtsGridSystem.parse(identifier)

    @staticmethod
    def parse_dls(identifier):
        return DlsSystem.parse(identifier)

    def to_lat_long_coordinate(self):
        if isinstance(self.identifier, LatLongCoordinate):
            return self.identifier
        elif isinstance(self.identifier, FederalPermitSystem):
            return self.identifier.to_lat_long()
        elif isinstance(self.identifier, BcNtsGridSystem):
            return self.identifier.to_lat_long()
        elif isinstance(self.identifier, DlsSystem):
            return self.identifier.to_lat_long()
        else:
            raise CoordinateParseException("Unknown identifier type.")

    def extract_federal_permit_system(self):
        if isinstance(self.identifier, FederalPermitSystem):
            return self.identifier
        return None

    def extract_bc_nts_grid_system(self):
        if isinstance(self.identifier, BcNtsGridSystem):
            return self.identifier
        return None

    def extract_dls_system(self):
        if isinstance(self.identifier, DlsSystem):
            return self.identifier
        return None

    def geodetic_to_lat_long(self):
        if isinstance(self.identifier, LatLongCoordinate):
            return self.identifier
        raise CoordinateParseException("Identifier is not a geodetic coordinate.")

    def equals(self, other):
        if not isinstance(other, UniqueWellIdentifier):
            return False
        return self.identifier == other.identifier

    def get_hash_code(self):
        return hash(self.identifier)

    def to_string(self):
        return str(self.identifier)
