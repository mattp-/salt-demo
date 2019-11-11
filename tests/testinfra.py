from __future__ import absolute_import, print_function

import itertools
import json
import logging
import pytest
import six
import sys
import testinfra
import time

from testinfra.modules.base import InstanceModule

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

# extend and fix salt cli based interaction in a testinfra
class Salt(InstanceModule):
    """ Run salt runner functions """
    def _decode_output(self, output):
        decoded_stdout = six.ensure_str(output.stdout).strip()
        calltype = type(self).__name__
        try:
            if calltype == "Salt":
                returns = {}
                for response in decoded_stdout.split("\n"):
                    try:
                        ret = json.loads(response)
                        # we flatten to a single minion->ret dict
                        if isinstance(ret, dict):
                            returns.update(ret)
                    except Exception as exc:
                        return response
                return returns

            out = json.loads(decoded_stdout)

            out_data = out["local"] if calltype == "SaltCall" else out
            return out_data

        except Exception as exc:
            log.exception(exc)
            return decoded_stdout


    def __call__(self, *args, **kwargs):
        args = args or []
        if isinstance(args, six.string_types):
            args = [args]

        calltype = type(self).__name__
        if calltype == "Salt":
            cmd = "salt"
        elif calltype == "SaltRun":
            cmd = "salt-run"
        elif calltype == "SaltCall":
            cmd = "salt-call"
        else:
            raise Exception("Found unexpected calltype {}".format(cmd))

        cmd_args = []
        cmd += " --out=json --out-indent=-1"
        cmd += len(args) * " %s"

        for arg in args:
            if isinstance(arg, six.string_types):
                cmd_args.append(arg)
            else:
                cmd_args.append(json.dumps(arg))

        for k, v in kwargs.items():
            cmd += " %s"
            if isinstance(v, six.string_types):
                cmd_args.append("{0}={1}".format(k, v))
            else:
                cmd_args.append("{0}={1}".format(k, json.dumps(v).strip()))

        output = self.run(cmd, *cmd_args)
        return self._decode_output(output)

    def __repr__(self):
        return type(self).__name__


class SaltRun(Salt):
    """ Run salt remote localclient functions """
    pass


class SaltCall(Salt):
    """ Run salt-call local functions """
    pass

# make testinfra aware of the above
# note, this replaces the poorly named salt module from upstream
testinfra.modules.modules["salt_run"] = "salt_run:SaltRun"
testinfra.modules.modules["salt"] = "salt:Salt"
testinfra.modules.modules["salt_call"] = "salt_call:SaltCall"

sys.modules["testinfra.modules.salt"] = sys.modules[__name__]
sys.modules["testinfra.modules.salt_run"] = sys.modules[__name__]
sys.modules["testinfra.modules.salt_call"] = sys.modules[__name__]
