"""JSON Schemas describing the API contract. A field that is renamed, retyped or dropped fails the tests."""

PRODUCT = {
    "type": "object",
    "required": ["id", "sku", "name", "category", "price_cents", "stock", "in_stock", "description"],
    "additionalProperties": False,
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "sku": {"type": "string", "pattern": "^[A-Z]{2}-\\d{3}$"},
        "name": {"type": "string", "minLength": 1},
        "category": {"type": "string", "enum": ["Electronics", "Books", "Home", "Accessories"]},
        "price_cents": {"type": "integer", "minimum": 0},
        "stock": {"type": "integer", "minimum": 0},
        "in_stock": {"type": "boolean"},
        "description": {"type": "string"},
    },
}

PRODUCT_LIST = {
    "type": "object",
    "required": ["count", "items"],
    "properties": {
        "count": {"type": "integer", "minimum": 0},
        "items": {"type": "array", "items": PRODUCT},
    },
}

TOKEN = {
    "type": "object",
    "required": ["token", "token_type", "expires_in"],
    "properties": {
        "token": {"type": "string", "minLength": 20},
        "token_type": {"const": "Bearer"},
        "expires_in": {"type": "integer", "minimum": 1},
    },
}

CART = {
    "type": "object",
    "required": ["items", "subtotal_cents", "tax_cents"],
    "properties": {
        "subtotal_cents": {"type": "integer", "minimum": 0},
        "tax_cents": {"type": "integer", "minimum": 0},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["product_id", "sku", "name", "quantity", "unit_price_cents", "line_total_cents"],
                "properties": {"quantity": {"type": "integer", "minimum": 1}},
            },
        },
    },
}

ORDER = {
    "type": "object",
    "required": ["id", "status", "full_name", "email", "subtotal_cents", "tax_cents", "total_cents", "created_at", "items"],
    "properties": {
        "id": {"type": "integer"},
        "status": {"enum": ["PLACED", "SHIPPED", "CANCELLED"]},
        "total_cents": {"type": "integer", "minimum": 0},
        "items": {"type": "array", "minItems": 1},
    },
}

ERROR = {
    "type": "object",
    "required": ["error"],
    "properties": {"error": {"type": "string", "minLength": 1}},
}
