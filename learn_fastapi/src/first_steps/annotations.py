from typing import Annotated

from pydantic import AfterValidator

from .schema import Item
from .validators import validate_item

ValidatedItem = Annotated[Item, AfterValidator(validate_item)]
