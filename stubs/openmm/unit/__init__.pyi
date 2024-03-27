class Unit:
    pass

class Quantity:
    @property
    def unit(self) -> Unit: ...

    def value_in_unit(self, unit: Unit) -> float:
        ...
