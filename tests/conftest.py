import pytest
import testinfra
import time
import logging
log = logging.getLogger()

pytest_plugins = [
    'tests.testinfra',
    'docker_compose',
]

# Invoking this fixture: 'function_scoped_container_getter' starts all services
@pytest.fixture(scope='function')
def wait_for_service(function_scoped_container_getter):
    '''Wait for the api from my_api_service to become responsive'''
    minion_id = function_scoped_container_getter.get('minion').short_id
    master_id = function_scoped_container_getter.get('master').short_id
    master = testinfra.get_host(master_id, connection='docker')

    while True:
        time.sleep(1)
        ret = master.salt('*', 'test.ping')

        if not isinstance(ret, dict):
            continue

        if all(ret.get(minion_id, False) is True for minion_id in [minion_id]):
            break

    return True
