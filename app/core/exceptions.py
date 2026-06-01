class NotFoundError(Exception):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, resource_id: str):
        self.resource = resource
        self.resource_id = resource_id
        super().__init__(f"{resource} with id '{resource_id}' not found")


class DuplicateSKUError(Exception):
    """Raised when a product with the same SKU already exists."""

    def __init__(self, sku: str):
        self.sku = sku
        super().__init__(f"Product with SKU '{sku}' already exists")


class DuplicateEmailError(Exception):
    """Raised when a customer with the same email already exists."""

    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Customer with email '{email}' already registered")


class InsufficientStockError(Exception):
    """Raised when a product does not have enough stock for an order."""

    def __init__(self, sku: str, requested: int, available: int):
        self.sku = sku
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient stock for product '{sku}': "
            f"requested {requested}, available {available}"
        )


class InvalidQuantityError(Exception):
    """Raised when an invalid quantity is provided."""

    def __init__(self):
        super().__init__("Quantity must be greater than 0")
