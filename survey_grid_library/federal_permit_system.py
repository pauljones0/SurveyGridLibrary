class FederalPermitSystem:
    def __init__(self, permit_number, location):
        self.permit_number = permit_number
        self.location = location

    def to_lat_long(self):
        # Convert the Federal Permit System location to latitude and longitude
        pass

    def equals(self, other):
        if isinstance(other, FederalPermitSystem):
            return self.permit_number == other.permit_number and self.location == other.location
        return False

    def get_hash_code(self):
        return hash((self.permit_number, self.location))

    @staticmethod
    def parse(permit_string):
        # Parse the permit string to create a FederalPermitSystem object
        pass

    def to_string(self):
        return f"Permit Number: {self.permit_number}, Location: {self.location}"
