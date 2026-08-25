"""Make pip usable on this host.

platform.mac_ver() returns empty strings here (Python 3.14 on darwin 25), which
crashes pip's truststore import before any download starts. Reporting a
plausible version restores it; nothing else depends on the value.
"""

import platform

if platform.system() == "Darwin" and not platform.mac_ver()[0]:
    platform.mac_ver = lambda: ("15.0.0", ("", "", ""), platform.machine())
