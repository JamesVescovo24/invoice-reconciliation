"""Success, error, missing, malformed and boundary-case verification tests."""
import json
from pathlib import Path
import pytest
from contract import BatchInput, SaveInput, Balance, SaveOutput
from plugin.logic import read_dataset, pin_reference, save_candidate
from plugin.storage import REPORT_PATH
from verifier import verify_input, verify_output, verify_task

@pytest.mark.parametrize('batch', ['mixed', 'refunds', 'empty'])
def test_gold(tmp_path, batch):
    given = BatchInput(batch)
    reference = pin_reference(given, tmp_path)
    read = read_dataset(given, tmp_path)
    assert verify_output('read_invoice_batch', given, read, str(tmp_path))['valid']
    assert verify_output('pin_invoice_truth', given, reference, str(tmp_path))['valid']
    payload = SaveInput(batch, reference.expected)
    saved = save_candidate(payload, tmp_path)
    assert verify_input('save_balances', payload)['valid']
    assert verify_output('save_balances', payload, saved, str(tmp_path))['valid']
    assert verify_task('reconcile-invoices', given, saved, reference, str(tmp_path))['valid']

@pytest.mark.parametrize('wrong', [
    [Balance('INV-A', 6000), Balance('INV-B', 0), Balance('INV-C', 0), Balance('INV-D', -1200)],
    [Balance('INV-A', 5000), Balance('INV-B', 0), Balance('INV-C', 0)],
    [Balance('INV-A', 5000), Balance('INV-B', 0), Balance('INV-C', 0), Balance('INV-D', -1200), Balance('EXTRA', 0)],
    [Balance('INV-A', 5000), Balance('INV-A', 5000), Balance('INV-C', 0), Balance('INV-D', -1200)],
])
def test_reject_wrong_rows(tmp_path, wrong):
    given = BatchInput('mixed')
    candidate = save_candidate(SaveInput('mixed', wrong), tmp_path)
    assert not verify_task('reconcile-invoices', given, candidate, pin_reference(given, tmp_path), str(tmp_path))['valid']

def test_reject_tamper_and_missing(tmp_path):
    given = BatchInput('mixed')
    reference = pin_reference(given, tmp_path)
    output = save_candidate(SaveInput('mixed', reference.expected), tmp_path)
    (tmp_path/REPORT_PATH).write_text('{"made":"up"}')
    assert not verify_task('reconcile-invoices', given, output, reference, str(tmp_path))['valid']
    (tmp_path/REPORT_PATH).unlink()
    assert not verify_task('reconcile-invoices', given, output, reference, str(tmp_path))['valid']

def test_reject_wrong_reference_and_unknown_batch(tmp_path):
    assert not verify_input('read_invoice_batch', BatchInput('invalid'))['valid']
    given = BatchInput('mixed')
    saved = save_candidate(SaveInput('mixed', pin_reference(given,tmp_path).expected), tmp_path)
    assert not verify_task('reconcile-invoices', given, saved, pin_reference(BatchInput('refunds'),tmp_path), str(tmp_path))['valid']

def test_malformed_json_and_count(tmp_path):
    given = BatchInput('empty')
    output = save_candidate(SaveInput('empty',[]), tmp_path)
    (tmp_path/REPORT_PATH).write_text('{broken json')
    import hashlib
    corrupt = SaveOutput('empty', REPORT_PATH, hashlib.sha256(b'{broken json').hexdigest(),0)
    assert not verify_task('reconcile-invoices', given,corrupt,pin_reference(given,tmp_path),str(tmp_path))['valid']
    output = save_candidate(SaveInput('empty',[]), tmp_path)
    output.count = 10
    assert not verify_task('reconcile-invoices', given,output,pin_reference(given,tmp_path),str(tmp_path))['valid']
