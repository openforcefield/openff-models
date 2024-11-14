openff-models
==============================
[//]: # (Badges)
[![GitHub Actions Build Status](https://github.com/openforcefield/openff-models/workflows/ci/badge.svg)](https://github.com/openforcefield/openff-models/actions?query=workflow%3Aci)
[![codecov](https://codecov.io/gh/openforcefield/openff-models/branch/main/graph/badge.svg)](https://codecov.io/gh/openforcefield/openff-models/branch/main)

Helper classes for Pydantic compatibility in the OpenFF stack

As of Interchange 0.4, the features of this package are provided directly in Interchange. Below are samples of how to get previous functionality with the new classes.

### Getting started

```python
import pprint
import json

from openff.interchange.pydantic import _BaseModel
from openff.interchange._annotations import _ElementaryChargeQuantity, _DistanceQuantity, _Quantity
from openff.units import unit, Quantity

class Atom(_BaseModel):
    mass: _Quantity
    charge: _ElementaryChargeQuantity
    some_array: _DistanceQuantity


atom = Atom(
    mass=12.011 * unit.atomic_mass_constant,
    charge=0.0 * unit.elementary_charge,
    some_array=Quantity([4, -1, 0], "nanometer"),
)

print(atom.model_dump())
# {'mass': {'val': 12.011, 'unit': 'atomic_mass_constant'}, 'charge': {'val': 0.0, 'unit': 'elementary_charge'}, 'some_array': {'val': [4, -1, 0], 'unit': 'nanometer'}}

# Note that unit-bearing fields use custom serialization into a dict with separate key-val pairs for
# the unit (as a string) and unitless quantities (in whatever shape the data is)
print(atom.model_dump_json())
# {"mass":{"val":12.011,"unit":"atomic_mass_constant"},"charge":{"val":0.0,"unit":"elementary_charge"},"some_array":{"val":[4,-1,0],"unit":"nanometer"}}

# The same thing, just more human-readable
pprint.pprint(json.loads(atom.model_dump_json()))
# {'charge': {'unit': 'elementary_charge', 'val': 0.0},
#  'mass': {'unit': 'atomic_mass_constant', 'val': 12.011},
#  'some_array': {'unit': 'nanometer', 'val': [4, -1, 0]}}

# Can also roundtrip through these representations
assert Atom.model_validate(atom.model_dump()).charge.m == 0.0
assert  Atom.model_validate_json(atom.model_dump_json()).mass.m == 12.011
```

The recommendation is that, at minimum, models are defined with `_Quantity` from `openff.interchange._annotations`. This ensures keeps serialization functionality but does not pick up the validaiton features of the custom types, i.e. dimensionality validation or checking for specific units.

```python
import json

from openff.units import Quantity
from openff.interchange.pydantic import _BaseModel


class Atom(_BaseModel):
    mass: _Quantity = Quantity(0.0, "amu")

json.loads(Atom(mass=12.011 * unit.atomic_mass_constant).model_dump_json())
# {'mass': '{"val": 12.011, "unit": "atomic_mass_constant"}'}

# This model does not have instructions to keep masses in mass units
json.loads(Atom(mass=12.011 * unit.nanometer).model_dump_json())
# {'mass': '{"val": 12.011, "unit": "nanometer"}'}
```

### Copyright

Copyright (c) 2022, Open Force Field Initiative

#### Acknowledgements

Project based on the
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.6.
