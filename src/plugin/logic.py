"""Read a batch, calculate the hidden reference, and save candidate reports."""
from __future__ import annotations
from pathlib import Path
from dataclasses import asdict
from contract import BatchInput, Invoice, Payment, Balance, ReadOutput, ReferenceOutput, SaveInput, SaveOutput
from plugin.datasets import FIXTURES, RULES
from plugin.storage import store

def _batch(name: str) -> dict:
    if name not in FIXTURES:
        raise ValueError(f"unknown batch {name!r}; choose mixed, refunds, empty")
    return FIXTURES[name]

def read_dataset(given: BatchInput, workspace: Path) -> ReadOutput:
    data = _batch(given.batch)
    return ReadOutput(given.batch, [Invoice(**row) for row in data['invoices']],
                      [Payment(**row) for row in data['payments']], RULES)

def pin_reference(given: BatchInput, workspace: Path) -> ReferenceOutput:
    read = read_dataset(given, workspace)
    totals = {row.invoice_id: row.charge_cents for row in read.invoices}
    for payment in read.payments:
        totals[payment.invoice_id] -= payment.amount_cents
    expected = [Balance(key, totals[key]) for key in sorted(totals)]
    return ReferenceOutput(given.batch, read.invoices, read.payments, expected)

def save_candidate(given: SaveInput, workspace: Path) -> SaveOutput:
    _batch(given.batch)
    if len(given.balances) > 500:
        raise ValueError("too many balances")
    payload = {"batch": given.batch, "balances": [asdict(row) for row in given.balances]}
    path, digest = store(workspace, payload)
    return SaveOutput(given.batch, path, digest, len(given.balances))
