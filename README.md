openff-models
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/mattwthompson/openff-models/workflows/ci/badge.svg)](https://github.com/mattwthompson/openff-models/actions?query=workflow%3Aci)
[![codecov](https://codecov.io/gh/mattwthompson/openff-models/branch/master/graph/badge.svg)](https://codecov.io/gh/mattwthompson/openff-models/branch/master)


Helper classes for Pydantic compatibility in the OpenFF stack

### Getting started

```python
import pprint
import json

from openff.models.models import DefaultModel
from openff.models.types import ArrayQuantity, FloatQuantity
from openff.units import unit


class Atom(DefaultModel):
    mass: FloatQuantity["atomic_mass_constant"]
    charge: FloatQuantity["elementary_charge"]
    some_array: ArrayQuantity["nanometer"]


atom = Atom(
    mass=12.011 * unit.atomic_mass_constant,
    charge=0.0 * unit.elementary_charge,
    some_array=unit.Quantity([4, -1, 0], unit.nanometer),
)

print(atom.dict())
# {'mass': <Quantity(12.011, 'atomic_mass_constant')>, 'charge': <Quantity(0.0, 'elementary_charge')>, 'some_array': <Quantity([ 4 -1  0], 'nanometer')>}

# Note that unit-bearing fields use custom serialization into a dict with separate key-val pairs for
# the unit (as a string) and unitless quantities (in whatever shape the data is)
print(atom.json())
# {"mass": "{\"val\": 12.011, \"unit\": \"atomic_mass_constant\"}", "charge": "{\"val\": 0.0, \"unit\": \"elementary_charge\"}", "some_array": "{\"val\": [4, -1, 0], \"unit\": \"nanometer\"}"}

# The same thing, just more human-readable
pprint.pprint(json.loads(atom.json()))
# {'charge': '{"val": 0.0, "unit": "elementary_charge"}',
#  'mass': '{"val": 12.011, "unit": "atomic_mass_constant"}',
#  'some_array': '{"val": [4, -1, 0], "unit": "nanometer"}'}

# Can also roundtrip through these representations
assert Atom(**atom.dict()).charge.m == 0.0
assert Atom.parse_raw(atom.json()).charge.m == 0.0
### Copyright
```

Copyright (c) 2022, Matt Thompson


#### Acknowledgements

Project based on the
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.6.
