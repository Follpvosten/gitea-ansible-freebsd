#!/usr/bin/python

__metaclass__ = type

import traceback

from datetime import datetime

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native


def main():
    module = AnsibleModule(
        argument_spec=dict(
            force=dict(type='bool', default=False),
            boot_env=dict(type='bool', default=False),
        ),
        supports_check_mode=False,
    )

    result = dict(
        changed=False,
        original_message='',
        message=''
    )

    force = module.params.get("force")
    boot_env = module.params.get("boot_env")

    hbsd_update_bin = module.get_bin_path("hbsd-update", True)

    if force:
        # Ignore version check, ignore everything
        cmd = [hbsd_update_bin, '-i']
        try:
            rc, _out, _err = module.run_command(cmd)
        except Exception as e:
            module.fail_json(msg=to_native(
                e), exception=traceback.format_exc())
        # If we got this far...
        if rc == 0:
            # ...and the command was successful, we have definitely changed the system.
            result['changed'] = True
            module.exit_json(**result)
        else:
            module.fail_json(msg='hbsd-update failed')
    else:
        # Check first
        cmd = [hbsd_update_bin, '-C']
        try:
            rc, out, _err = module.run_command(cmd)
        except Exception as e:
            module.fail_json(msg=to_native(
                e), exception=traceback.format_exc())
        if rc != 0:
            module.fail_json(msg='hbsd-update failed')

        lines = out.splitlines()[1:]
        for i in range(2):
            lines[i] = lines[i].split(' ')[3]

        local_version, remote_version = lines
        if local_version == remote_version:
            module.exit_json(**result)

        cmd = [hbsd_update_bin]
        if boot_env:
            now = datetime.now()
            boot_env_name = now.strftime('update-%y-%m-%d')
            cmd.extend(('-b', boot_env_name))

        try:
            rc, _out, _err = module.run_command(cmd)
        except Exception as e:
            module.fail_json(msg=to_native(
                e), exception=traceback.format_exc())
        # If we got this far...
        if rc == 0:
            # ...and the command was successful, we have definitely changed the system.
            result['changed'] = True
            module.exit_json(**result)
        else:
            module.fail_json(msg='hbsd-update failed')


if __name__ == "__main__":
    main()
