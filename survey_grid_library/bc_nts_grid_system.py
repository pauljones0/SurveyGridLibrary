class BcNtsGridSystem:
    def __init__(self, quarter_unit, unit, block, series, map_area, sheet):
        if (quarter_unit < 'A' or quarter_unit > 'D') and (quarter_unit < 'a' or quarter_unit > 'd'):
            raise ValueError("Quarter unit must be in the range A-D")
        if unit < 1 or unit > 100:
            raise ValueError("Unit must be in the range 1-100")
        if (block < 'A' or block > 'L') and (block < 'a' or block > 'l'):
            raise ValueError("Block must be in the range A-L")
        if series < 82 or series > 114:
            raise ValueError("Series must be in the range 82-114")
        if (map_area < 'A' or map_area > 'P') and (map_area < 'a' or map_area > 'p'):
            raise ValueError("Map Area must be in the range A-P")
        if sheet < 1 or sheet > 16:
            raise ValueError("Sheet must be in the range 1-16")

        self.quarter_unit = quarter_unit.upper()
        self.unit = unit
        self.block = block.upper()
        self.series = series
        self.map_area = map_area.upper()
        self.sheet = sheet

    def equals(self, other):
        if not isinstance(other, BcNtsGridSystem):
            return False
        return (self.quarter_unit == other.quarter_unit and
                self.unit == other.unit and
                self.block == other.block and
                self.series == other.series and
                self.map_area == other.map_area and
                self.sheet == other.sheet)

    def get_hash_code(self):
        return (hash(self.block) ^
                hash(self.map_area) ^
                hash(self.quarter_unit) ^
                hash(self.series) ^
                hash(self.sheet) ^
                hash(self.unit))

    def to_string(self):
        return f"{self.quarter_unit}-{self.unit:03d}-{self.block}/{self.series:03d}-{self.map_area}-{self.sheet:02d}"

    @staticmethod
    def parse(location):
        if location is None:
            raise ValueError("Can not parse a null location.")
        if not location.strip():
            raise ValueError("Can not parse an empty location.")

        fields = location.upper().strip().split('/')
        if len(fields) == 1:
            list_fields = BcNtsGridSystem.split_location(fields[0])
            if len(list_fields) == 6:
                first_half = "-".join(list_fields[:3])
                second_half = "-".join(list_fields[3:])
            elif len(list_fields) == 7:
                first_half = "-".join(list_fields[:4])
                second_half = "-".join(list_fields[4:])
            else:
                raise ValueError("BC nts location must have two fields separated by a '/'.")
        elif len(fields) == 2:
            first_half = fields[0].strip()
            second_half = fields[1].strip()
        else:
            raise ValueError("Location has too many parts separated by a '/'")

        second_parts = BcNtsGridSystem.split_location(second_half)
        if len(second_parts) < 3:
            raise ValueError("BC nts must have Map/sheet/area.")

        series = int(second_parts[0])
        pq_values = [82, 83, 92, 93, 94, 102, 103, 104]
        if series not in pq_values:
            raise ValueError(f"Series must be one of {pq_values}.")

        if len(second_parts[1]) != 1:
            raise ValueError(f"Map Area '{second_parts[1]}' is an invalid length, expect one character.")
        map_area = second_parts[1][0]
        if map_area == '0':
            map_area = 'O'
        if map_area == '1':
            map_area = 'I'
        if map_area < 'A' or map_area > 'P':
            raise ValueError("Map area must be in the range A to P.")

        if second_parts[2] == "I":
            second_parts[2] = "1"
        map_sheet = int(second_parts[2])
        if map_sheet < 1 or map_sheet > 16:
            raise ValueError("Map sheet must be between 1 and 16.")

        first_parts = BcNtsGridSystem.split_location(first_half)
        if len(first_parts) < 3:
            raise ValueError("BC nts must have Quarter Unit Block.")

        first_parts.reverse()
        block = first_parts[0][0]
        if block == '1':
            block = 'I'
        if block < 'A' or block > 'L':
            raise ValueError("Block must be from A to L.")

        unit = int(first_parts[1])
        if unit < 1 or unit > 100:
            raise ValueError("Unit must be in the range 1 to 100.")

        quarter_index = 2
        if len(first_parts) == 4 and first_parts[2] and first_parts[2][0].isalpha():
            quarter_index = 3

        q = first_parts[quarter_index]
        if not q:
            raise ValueError("Quarter must be supplied.")
        quarter = q[-1]
        if quarter < 'A' or quarter > 'D':
            raise ValueError("Quarter must be from A to D.")

        return BcNtsGridSystem(quarter, unit, block, series, map_area, map_sheet)

    @staticmethod
    def split_location(location):
        block_type = None
        buff = ""
        for c in location:
            if '0' <= c <= '9':
                new_block_type = 'D'
            elif 'A' <= c <= 'P':
                new_block_type = 'L'
            else:
                new_block_type = 'S'

            if new_block_type != block_type:
                if buff:
                    yield buff
                    buff = ""
                block_type = new_block_type

            if new_block_type in ('D', 'L'):
                buff += c

        if buff:
            yield buff

    def to_lat_long(self):
        return BcNtsGridSystemConverter.to_lat_long(self)

    @staticmethod
    def to_lat_long(system):
        return BcNtsGridSystemConverter.to_lat_long(system)
