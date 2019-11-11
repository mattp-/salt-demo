import pytest
import testinfra
import logging

log = logging.getLogger()

def test_pkg_orch(function_scoped_container_getter, wait_for_service):
    master_id = function_scoped_container_getter.get('master').short_id
    minion_id = function_scoped_container_getter.get('minion').short_id
    master = testinfra.get_host(master_id, connection='docker')

    ret = master.salt_run(
        'state.orchestrate',
        'orch.pkg',
        pillar={'tgt': minion_id, 'pkg': 'bash'},
    )

    assert ret['retcode'] is 0
