"""Original static invoice fixtures, packaged with the plugin."""
FIXTURES = {
    "mixed": {
        "invoices": [
            {"invoice_id": "INV-A", "charge_cents": 10000},
            {"invoice_id": "INV-B", "charge_cents": 5000},
            {"invoice_id": "INV-C", "charge_cents": 0},
            {"invoice_id": "INV-D", "charge_cents": 3000},
        ],
        "payments": [
            {"invoice_id": "INV-A", "amount_cents": 4000},
            {"invoice_id": "INV-A", "amount_cents": 1000},
            {"invoice_id": "INV-B", "amount_cents": 5000},
            {"invoice_id": "INV-D", "amount_cents": 4200},
        ],
    },
    "refunds": {
        "invoices": [
            {"invoice_id": "001", "charge_cents": 12000},
            {"invoice_id": "002", "charge_cents": 200},
            {"invoice_id": "010", "charge_cents": 700},
        ],
        "payments": [
            {"invoice_id": "001", "amount_cents": 10000},
            {"invoice_id": "001", "amount_cents": -2500},
            {"invoice_id": "002", "amount_cents": 400},
            {"invoice_id": "010", "amount_cents": 600},
            {"invoice_id": "010", "amount_cents": 100},
        ],
    },
    "empty": {"invoices": [], "payments": []},
}
RULES = (
    "For each invoice, balance_cents = charge_cents minus the sum of its signed amount_cents payments. "
    "Negative payments are refunds; negative balances (overpayments) are valid. "
    "Include ALL invoices, even fully paid ones; do not duplicate, add or omit invoice IDs. "
    "Use integer cents, not floating-point dollars. Output order is irrelevant."
)
