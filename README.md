# Survey Grid Library

A library for interacting with the Survey systems used within Western Canada. This library is now implemented in Python and has no dependencies on other libraries or databases in order to function.

## Types provided:

BcNtsGridSystem
DlsSystem
FederalPermitSystem
UniqueWellIdentifier

## Capabilities 

With this library it is possible to convert between geographic coordinates (lat/long) and DLS Grid / BC NTS Grid positions. These conversions are made without referencing an external database.

## Installation

To install the library, use pip:

```bash
pip install survey-grid-library
```

## Usage

Here are some examples of how to use the library:

### Converting DLS to LatLong

```python
from survey_grid_library.dls_system import DlsSystem

dls = DlsSystem(legal_subdivision=1, section=1, township=1, range=1, meridian=4)
lat_long = dls.to_lat_long()
print(lat_long)
```

### Converting LatLong to DLS

```python
from survey_grid_library.lat_long_coordinate import LatLongCoordinate
from survey_grid_library.dls_system_converter import DlsSystemConverter

lat_long = LatLongCoordinate(latitude=50.0, longitude=-110.0)
dls = DlsSystemConverter.from_lat_long_coordinate(lat_long)
print(dls)
```

### Converting BC NTS to LatLong

```python
from survey_grid_library.bc_nts_grid_system import BcNtsGridSystem

bc_nts = BcNtsGridSystem(quarter_unit='A', unit=1, block='A', series=82, map_area='A', sheet=1)
lat_long = bc_nts.to_lat_long()
print(lat_long)
```

### Converting LatLong to BC NTS

```python
from survey_grid_library.lat_long_coordinate import LatLongCoordinate
from survey_grid_library.bc_nts_grid_system_converter import BcNtsGridSystemConverter

lat_long = LatLongCoordinate(latitude=50.0, longitude=-110.0)
bc_nts = BcNtsGridSystemConverter.from_lat_long_coordinates(lat_long)
print(bc_nts)
```

### Converting Federal Permit System to LatLong

```python
from survey_grid_library.federal_permit_system import FederalPermitSystem

federal_permit = FederalPermitSystem(unit='A', section=1, lat_degrees=50, lat_minutes=0, lon_degrees=110, lon_minutes=0)
lat_long = federal_permit.to_lat_long()
print(lat_long)
```

### Converting LatLong to Federal Permit System

```python
from survey_grid_library.lat_long_coordinate import LatLongCoordinate
from survey_grid_library.federal_permit_system_converter import FederalPermitSystemConverter

lat_long = LatLongCoordinate(latitude=50.0, longitude=-110.0)
federal_permit = FederalPermitSystemConverter.from_lat_long_coordinates(lat_long)
print(federal_permit)
```

### Running Python Unit Tests

To run the Python unit tests using `unittest`, follow these steps:

1. Navigate to the `UnitTestPython` directory:
```bash
cd UnitTestPython
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Run the tests:
```bash
python -m unittest discover
```
