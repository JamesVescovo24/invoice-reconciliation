"""Invoice reconciliation: all task and tool contracts; declarations only."""
from dataclasses import dataclass
from enum import Enum
from typing import Annotated
from slimconfig import Output

class Tool(Enum):
    PIN = "pin_invoice_truth"
    READ = "read_invoice_batch"
    SAVE = "save_balances"

class Task(Enum):
    MAIN = "reconcile-invoices"

@dataclass
class BatchInput(Output):
    batch: Annotated[str, "Fixture batch: mixed, refunds, or empty"]

@dataclass
class Invoice(Output):
    invoice_id: str
    charge_cents: int

@dataclass
class Payment(Output):
    invoice_id: str
    amount_cents: int

@dataclass
class Balance(Output):
    invoice_id: str
    balance_cents: int

@dataclass
class ReadOutput(Output):
    batch: str
    invoices: list[Invoice]
    payments: list[Payment]
    rules: str

@dataclass
class ReferenceOutput(Output):
    batch: str
    invoices: list[Invoice]
    payments: list[Payment]
    expected: list[Balance]

@dataclass
class SaveInput(Output):
    batch: str
    balances: Annotated[list[Balance], "One entry for every invoice, including zero and negative balances; order irrelevant"]

@dataclass
class SaveOutput(Output):
    batch: str
    path: str
    digest: Annotated[str, "SHA256 of the saved report file"]
    count: int

TOOLS = {Tool.PIN: (BatchInput, ReferenceOutput), Tool.READ: (BatchInput, ReadOutput), Tool.SAVE: (SaveInput, SaveOutput)}
TASKS = {Task.MAIN: (BatchInput, SaveOutput)}
