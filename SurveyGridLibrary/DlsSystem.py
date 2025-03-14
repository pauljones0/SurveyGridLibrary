import re
from SurveyGridLibrary.CoordinateParseException import CoordinateParseException
from SurveyGridLibrary.LatLongCoordinate import LatLongCoordinate
from SurveyGridLibrary.DlsSystemConverter import DlsSystemConverter

class DlsSystem:
    def __init__(self, legal_subdivision, section, township, range, meridian):
        if legal_subdivision < 1 or legal_subdivision > 16:
            raise ValueError("Legal sub division must be in the range 1-16")
        if section < 1 or section > 36:
            raise ValueError("Section must be in the range 1-36")
        if township < 1 or township > 127:
            raise ValueError("Township must be in the range 1-127")
        if range < 1 or range > 34:
            raise ValueError("Range must be in the range 1-34")
        if meridian < 1 or meridian > 6:
            raise ValueError("Meridian must be in the range 1-6")

        self.legal_subdivision = legal_subdivision
        self.section = section
        self.township = township
        self.range = range
        self.meridian = meridian

    @property
    def quarter(self):
        if self.legal_subdivision in [1, 2, 7, 8]:
            return "SE"
        if self.legal_subdivision in [3, 4, 5, 6]:
            return "SW"
        if self.legal_subdivision in [9, 10, 15, 16]:
            return "NE"
        if self.legal_subdivision in [11, 12, 13, 14]:
            return "NW"
        return None

    def to_string(self):
        return f"{self.legal_subdivision:02}-{self.section:02}-{self.township:03}-{self.range:02}W{self.meridian}"

    @staticmethod
    def parse(location, options=None):
        if location is None:
            raise CoordinateParseException("Can not parse a null location.")

        if not location.strip():
            raise CoordinateParseException("Can not parse an empty location.")

        location = location.upper()

        if location.endswith("M"):
            location = location[:-1]

        direction_index = location.rfind('W')
        if direction_index == -1:
            direction_index = location.rfind('E')
            if direction_index == -1:
                raise CoordinateParseException("DLS location must contain at least one direction as 'W' or 'E'.")

        direction = location[direction_index]

        mer_buff = '\0'
        for y in range(direction_index + 1, len(location)):
            mer_buff = location[y]
            if mer_buff.isdigit() or mer_buff == 'P':
                break

        if mer_buff == 'P':
            mer = 1
        else:
            mer = int(mer_buff)
            if not mer:
                raise CoordinateParseException(f"Meridian {mer_buff} is not a valid number")

        if direction == 'W' and (mer < 1 or mer > 8):
            raise CoordinateParseException("Meridian must be in the range 1 to 8.")

        if direction == 'E':
            raise CoordinateParseException("East Meridian is not supported.")

        location = location[:direction_index]

        parts = list(DlsSystem.split_string(location))
        if len(parts) < 4:
            raise CoordinateParseException("DLS location must have range/twp/sec/lsd.")

        rng = int(parts[0].strip())
        if mer != 1 and (rng < 1 or rng > 30):
            raise CoordinateParseException("Rng must be in the range 1 to 30.")
        if mer == 1 and (rng < 1 or rng > 34):
            raise CoordinateParseException("Rng must be in the range 1 to 34.")

        twp = int(parts[1].strip())
        if twp < 1 or twp > 126:
            raise CoordinateParseException("Township must be in the range 1 to 126.")

        sec = int(parts[2].strip())
        if sec < 1 or sec > 36:
            raise CoordinateParseException("Section must be in the range 1 to 36.")

        lsd_string = parts[3].strip()
        lsd = int(lsd_string) if lsd_string.isdigit() else 0
        if not lsd:
            if options and "AllowQuarters" in options:
                if lsd_string == "NW":
                    lsd = 11
                elif lsd_string == "NE":
                    lsd = 10
                elif lsd_string == "SW":
                    lsd = 6
                elif lsd_string == "SE":
                    lsd = 7

            if not lsd:
                for b in range(16, 0, -1):
                    if str(b) in lsd_string:
                        lsd = b
                        break

                if not lsd:
                    raise CoordinateParseException(f"Legal Subdivision {parts[3]} is not valid.")

        if lsd < 1 or lsd > 16:
            raise CoordinateParseException("Legal Subdivision must be in the range 1 to 16.")

        return DlsSystem(lsd, sec, twp, rng, mer)

    @staticmethod
    def split_string(location):
        buff = ''
        for c in reversed(location):
            if c.isdigit() or c.isalpha():
                buff = c + buff
            else:
                if buff:
                    yield buff
                    buff = ''
        if buff:
            yield buff

    def to_lat_long(self):
        return DlsSystemConverter.to_lat_long(self)

    def equals(self, other):
        if not isinstance(other, DlsSystem):
            return False
        return self == other

    def get_hash_code(self):
        return hash((self.legal_subdivision, self.section, self.township, self.range, self.meridian))

    def __eq__(self, other):
        if not isinstance(other, DlsSystem):
            return False
        return (self.legal_subdivision == other.legal_subdivision and
                self.section == other.section and
                self.township == other.township and
                self.range == other.range and
                self.meridian == other.meridian)

    def __ne__(self, other):
        return not self.__eq__(other)
