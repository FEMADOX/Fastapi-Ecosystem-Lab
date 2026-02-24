# TODO (FEMADOX): This file is not longer necessary, but it is left here for demonstration purposes.
#   It shows how to use Pydantic's `Annotated` type to apply a validator to a Pydantic model.
#   In this case, we define a `ValidatedItem` type that is an `Item` with the `validate_item` function applied as an after-validator.
#   This allows us to ensure that any `ValidatedItem` instances are validated according to the rules defined in `validate_item`.
from typing import Annotated

from pydantic import AfterValidator

from .schema import Item
from .validators import validate_item

ValidatedItem = Annotated[Item, AfterValidator(validate_item)]
