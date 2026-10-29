"""Invoice oracle recomputed from the pinned records with pure integer arithmetic."""
from .checks import result, read_receipt
from contract import Tool

BATCHES = ("mixed", "refunds", "empty")

def arithmetic(invoices, payments):
    totals = {}
    for invoice in invoices:
        if (not invoice.invoice_id or invoice.invoice_id in totals or invoice.charge_cents < 0):
            return None
        totals[invoice.invoice_id] = invoice.charge_cents
    for payment in payments:
        if payment.invoice_id not in totals:
            return None
        totals[payment.invoice_id] -= payment.amount_cents
    return totals

def balances_ok(rows, expected):
    actual = {}
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"invoice_id", "balance_cents"}:
            return False
        key, val = row['invoice_id'], row['balance_cents']
        if not isinstance(key, str) or key in actual or type(val) is not int:
            return False
        actual[key] = val
    return actual == expected

def verify_input(tool, value):
    if tool in (Tool.PIN, Tool.READ):
        return result(value.batch in BATCHES, "known batch" if value.batch in BATCHES else "unknown batch")
    ok = value.batch in BATCHES and len(value.balances) <= 500
    return result(ok, "report input accepted" if ok else "invalid report input")

def verify_output(tool, input_value, output_value, workspace):
    if tool == Tool.READ:
        ok = output_value.batch == input_value.batch and arithmetic(output_value.invoices, output_value.payments) is not None
        return result(ok, "read data valid" if ok else "read data invalid")
    if tool == Tool.PIN:
        expected = arithmetic(output_value.invoices, output_value.payments)
        ok = output_value.batch == input_value.batch and expected is not None and balances_ok(
            [{"invoice_id": v.invoice_id, "balance_cents": v.balance_cents} for v in output_value.expected], expected)
        return result(ok, "reference consistent" if ok else "reference inconsistent")
    record, problem = read_receipt(workspace, output_value)
    expected = {"batch": input_value.batch, "balances": [
        {"invoice_id": row.invoice_id, "balance_cents": row.balance_cents} for row in input_value.balances]}
    ok = not problem and output_value.batch == input_value.batch and output_value.count == len(input_value.balances) and record == expected
    return result(ok, "candidate saved" if ok else problem or "saved artifact differs from submitted candidate")

def verify_task(arguments, output, reference, workspace):
    if reference is None or reference.batch != arguments.batch or output.batch != arguments.batch:
        return result(False, "missing or mismatched pinned reference")
    expected = arithmetic(reference.invoices, reference.payments)
    if expected is None or not balances_ok([{"invoice_id": row.invoice_id, "balance_cents": row.balance_cents} for row in reference.expected], expected):
        return result(False, "invalid reference arithmetic")
    record, problem = read_receipt(workspace, output)
    if problem:
        return result(False, problem)
    if record.get('batch') != arguments.batch or not isinstance(record.get('balances'), list):
        return result(False, "wrong batch or missing balances")
    if output.count != len(record['balances']):
        return result(False, "count does not match saved balances")
    if not balances_ok(record['balances'], expected):
        return result(False, "incorrect, omitted, extra, or duplicate invoice balance", expected=expected)
    return result(True, "all invoice balances independently verified", invoices=len(expected))
