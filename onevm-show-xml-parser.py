#!/usr/bin/env python3
# onevm-show-xml-parser.py - Utility for "onevm show --xml <VM_ID>"
# output parsing, this version supports OpenNebula 5.8

import xml.etree.ElementTree as ET
from enum import Enum
from subprocess import run, PIPE
from sys import argv, stderr

# Next 2 enums are from:
# https://github.com/OpenNebula/one/blob/one-5.8/include/VirtualMachine.h
class VmState(Enum):
    PENDING         = 1
    HOLD            = 2
    ACTIVE          = 3
    STOPPED         = 4
    SUSPENDED       = 5
    DONE            = 6
    #FAILED          = 7
    POWEROFF        = 8
    UNDEPLOYED      = 9
    CLONING         = 10
    CLONING_FAILURE = 11
    def __str__(self):
        return self.name

class LcmState(Enum):
    LCM_INIT = 0
    PROLOG = 1
    BOOT = 2
    RUNNING = 3
    MIGRATE = 4
    SAVE_STOP = 5
    SAVE_SUSPEND = 6
    SAVE_MIGRATE = 7
    PROLOG_MIGRATE = 8
    PROLOG_RESUME = 9
    EPILOG_STOP = 10
    EPILOG = 11
    SHUTDOWN = 12
    #CANCEL = 13
    #FAILURE = 14
    CLEANUP_RESUBMIT = 15
    UNKNOWN = 16
    HOTPLUG = 17
    SHUTDOWN_POWEROFF = 18
    BOOT_UNKNOWN = 19
    BOOT_POWEROFF = 20
    BOOT_SUSPENDED = 21
    BOOT_STOPPED = 22
    CLEANUP_DELETE = 23
    HOTPLUG_SNAPSHOT = 24
    HOTPLUG_NIC = 25
    HOTPLUG_SAVEAS = 26
    HOTPLUG_SAVEAS_POWEROFF = 27
    HOTPLUG_SAVEAS_SUSPENDED = 28
    SHUTDOWN_UNDEPLOY = 29
    EPILOG_UNDEPLOY = 30
    PROLOG_UNDEPLOY = 31
    BOOT_UNDEPLOY = 32
    HOTPLUG_PROLOG_POWEROFF = 33
    HOTPLUG_EPILOG_POWEROFF = 34
    BOOT_MIGRATE = 35
    BOOT_FAILURE = 36
    BOOT_MIGRATE_FAILURE = 37
    PROLOG_MIGRATE_FAILURE = 38
    PROLOG_FAILURE = 39
    EPILOG_FAILURE = 40
    EPILOG_STOP_FAILURE = 41
    EPILOG_UNDEPLOY_FAILURE = 42
    PROLOG_MIGRATE_POWEROFF = 43
    PROLOG_MIGRATE_POWEROFF_FAILURE = 44
    PROLOG_MIGRATE_SUSPEND = 45
    PROLOG_MIGRATE_SUSPEND_FAILURE = 46
    BOOT_UNDEPLOY_FAILURE = 47
    BOOT_STOPPED_FAILURE = 48
    PROLOG_RESUME_FAILURE = 49
    PROLOG_UNDEPLOY_FAILURE = 50
    DISK_SNAPSHOT_POWEROFF = 51
    DISK_SNAPSHOT_REVERT_POWEROFF = 52
    DISK_SNAPSHOT_DELETE_POWEROFF = 53
    DISK_SNAPSHOT_SUSPENDED = 54
    DISK_SNAPSHOT_REVERT_SUSPENDED = 55
    DISK_SNAPSHOT_DELETE_SUSPENDED = 56
    DISK_SNAPSHOT = 57
    #DISK_SNAPSHOT_REVERT = 58
    DISK_SNAPSHOT_DELETE = 59
    PROLOG_MIGRATE_UNKNOWN = 60
    PROLOG_MIGRATE_UNKNOWN_FAILURE = 61
    DISK_RESIZE = 62
    DISK_RESIZE_POWEROFF = 63
    DISK_RESIZE_UNDEPLOYED = 64
    def __str__(self):
        return self.name

class disks_ide(Enum):
    none = 0
    present = 1

class disks_raw(Enum):
    none = 0
    present = 1

ONEVM_COMMAND = "onevm"
SEPARATOR = ","

for i in range(1,len(argv)):
    id = argv[i]
    # https://www.edureka.co/blog/python-xml-parser-tutorial/#xml.etree
    # xmltree = ET.parse("data/" + id + ".xml")
    # xmlroot = xmltree.getroot()
    p = run([ONEVM_COMMAND, "show", "--xml", id], stdout=PIPE, stderr=PIPE)
    if p.returncode != 0:
        print("Error: ", p.stderr.decode(), file=stderr)
        continue
    xmlroot = ET.fromstring(p.stdout.decode())
    name = xmlroot.find("NAME").text
    owner = xmlroot.find("UNAME").text
    state = VmState(int(xmlroot.find("STATE").text))
    lcm_state = LcmState(int(xmlroot.find("LCM_STATE").text))
    ide = disks_ide.none
    raw = disks_raw.none
    for disk in xmlroot.find("TEMPLATE").findall("DISK"):
        if disk.find("TYPE").text != "CDROM":
            if disk.find("DEV_PREFIX").text == "hd" or disk.find("DEV_PREFIX").text == "sd":
                ide = disks_ide.present
            driver = disk.find("DRIVER")
            if driver == None or driver.text == "raw":
                raw = disks_raw.present
    row = [owner, id, name, state.__str__(), lcm_state.__str__(), ide.__str__(), raw.__str__()]
    print(SEPARATOR.join(row))
