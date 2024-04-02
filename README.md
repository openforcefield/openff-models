openff-models
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/openforcefield/openff-models/workflows/ci/badge.svg)](https://github.com/openforcefield/openff-models/actions?query=workflow%3Aci)
[![codecov](https://codecov.io/gh/openforcefield/openff-models/branch/main/graph/badge.svg)](https://codecov.io/gh/openforcefield/openff-models/branch/main)


Helper classes for Pydantic compatibility in the OpenFF stack

### Getting started

```python
from pprint import pprint
import json

from openff.models.models import DefaultModel
from openff.models.dimension_types import LengthQuantity
from openff.models.unit_types import (
    OnlyAMUQuantity,
    OnlyElementaryChargeQuantity,
)
from openff.units import Quantity, unit


class Atom(DefaultModel):
    mass: OnlyAMUQuantity
    charge: OnlyElementaryChargeQuantity
    some_array: LengthQuantity


atom = Atom(
    mass=Quantity(12.011, "atomic_mass_constant"),
    charge=0.0 * unit.elementary_charge,
    some_array=Quantity([4, -1, 0], "nanometer"),
)

pprint(atom.dict())
# {'charge': <Quantity(0.0, 'elementary_charge')>,
#  'mass': <Quantity(12.011, 'unified_atomic_mass_unit')>,
#  'some_array': <Quantity([ 4 -1  0], 'nanometer')>}
#

# Note that unit-bearing fields use custom serialization into a dict with separate key-val pairs for
# the unit (as a string) and unitless quantities (in whatever shape the data is)
pprint(atom.json())
# ('{"mass":"{\\"val\\": 12.011, \\"unit\\": '
#  '\\"unified_atomic_mass_unit\\"}","charge":"{\\"val\\": 0.0, \\"unit\\": '
#  '\\"elementary_charge\\"}","some_array":"{\\"val\\": [4, -1, 0], \\"unit\\": '
#  '\\"nanometer\\"}"}')

# The same thing, just more human-readable
pprint(json.loads(atom.json()))
# {'charge': '{"val": 0.0, "unit": "elementary_charge"}',
#  'mass': '{"val": 12.011, "unit": "unified_atomic_mass_unit"}',
#  'some_array': '{"val": [4, -1, 0], "unit": "nanometer"}'}

# Can also roundtrip through dict/JSON representations
assert Atom(**atom.dict()).charge.m == 0.0
assert Atom.parse_raw(atom.json()).charge.m == 0.0
```

Currently, models can also be defined with a simple `unit.Quantity` annotation. This keeps serialization functionality but does not pick up the validaiton features of the custom types, i.e. dimensionality validation.

```python
import json

from openff.units import unit
from openff.models.models import DefaultModel


class Atom(DefaultModel):
    mass: unit.Quantity = unit.Quantity(0.0, unit.amu)


json.loads(Atom(mass=12.011 * unit.atomic_mass_constant).json())
# {'mass': '{"val": 12.011, "unit": "atomic_mass_constant"}'}

# This model does have instructions to keep masses in mass units
json.loads(Atom(mass=12.011 * unit.nanometer).json())
# {'mass': '{"val": 12.011, "unit": "nanometer"}'}
```

### Copyright

Copyright (c) 2022, Open Force Field Initiative


#### Acknowledgements

Project based on the
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.6.
