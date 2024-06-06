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

`openff-models` ships a number of these annotated types by default, covering common dimensions and units. For those that aren't covered, there are helper classes to construct them.

```python
from openff.units import Quantity

from openff.models.models import DefaultModel
from openff.models.types.dimension_types import build_dimension_type, LengthQuantity

BondForceConstant = build_dimension_type("kilocalorie / mole / angstrom ** 2")


class BondParameter(DefaultModel):
    length: LengthQuantity
    k: BondForceConstant


BondParameter(
    length=Quantity("1.35 angstrom"),
    k=Quantity("400 kilocalorie_per_mole / angstrom **2"),
).model_dump()
# {'length': 1.35 <Unit('angstrom')>,
#  'k': 400.0 <Unit('kilocalorie_per_mole / angstrom ** 2')>}
```

Currently, models can also be defined with a simple `Quantity` annotation. This keeps serialization functionality but does not pick up the validaiton features of the custom types, i.e. dimensionality or unit validation, duck-typing from `str` or other types that can be coerced into `Quantity`.

```python
import json

from pydantic import ValidationError

from openff.units import Quantity
from openff.models.models import DefaultModel


class Atom(DefaultModel):
    mass: Quantity


# Works fine if given a Quantity
Atom(mass=Quantity("0 amu")).model_dump()
# {'mass': 0 <Unit('unified_atomic_mass_unit')>}

# Won't automagically convert str, whereas MassQuantity or other annotated types would
try:
    Atom(mass="0 amu").model_dump()
except ValidationError as error:
    print(error)
# ValidationError: 1 validation error for Atom
# mass
#   Input should be an instance of Quantity [type=is_instance_of, input_value='0 amu', input_type=str]
#     For further information visit https://errors.pydantic.dev/2.6/v/is_instance_of

# And it will gladly accept a Quantity with incompatible units,
# which may lead to surprising results
Atom(mass=Quantity("0 nanometer")).model_dump()
# {'mass': 0 <Unit('nanometer')>}
```

### Copyright

Copyright (c) 2022, Open Force Field Initiative


#### Acknowledgements

Project based on the
[Computational Molecular Science Python Cookiecutter](https://github.com/molssi/cookiecutter-cms) version 1.6.
