#!/usr/bin/env python3
import argparse
import csv
import subprocess


def get_ipmi_sensor(ip, user, password):
    command = (
        "/usr/bin/ipmitool "
        "-I lan "
        f"-H {ip} "
        f"-U {user} "
        f"-P {password} "
        "sdr"
    )
    ipmi_output = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
    return ipmi_output.stdout

def parse_ipmi_sensor(ipmi_sensor_output: str):
    csv_reader = csv.reader(ipmi_sensor_output.splitlines(), delimiter='|')
    points = []

    for i, row in enumerate(csv_reader):
        # Ignore value if senor/device not present
        if row[2].strip() == "ns":
            continue

        # Sensor status
        status = '1' if row[2].strip().lower() == 'ok' else '0'

        field = 'status=' + status

        # Sensor name
        sensor_name = row[0].strip()

        tag = 'sensor=' + sensor_name.replace(' ', '\ ')  # Format for Influx

	# Sensor value and unit
        data = row[1].strip().split(" ")
        value = data[0]
        if len(data) == 3:
            # Temperature
            unit = data[2]
        elif value.startswith("0x"):
            continue
        else:
            unit = data[1]

        if unit == "Volts":
            unit = "V"

        field += ',value=' + value
        field += ',unit="{}"'.format(unit)

        points.append('smc_ipmi,{} {}'.format(tag, field))
    return points


def get_pminfo(ip, user, password):
    command = (
        "/usr/bin/ipmitool "
        "-I lan "
        f"-H {ip} "
        f"-U {user} "
        f"-P {password} "
        "dcmi power reading"
    )
    pminfo_output = subprocess.run(command, capture_output=True, universal_newlines=True, shell=True)
    return pminfo_output.stdout


def parse_pminfo(pm_output: str):
    points = []
    value = None
    unit = None
    state = None

    for line in pm_output.splitlines():
        if line.strip().startswith("Instantaneous"):
            value = line.split(":")[1].split()[0]
            unit = "W"
        elif line.strip().startswith("Power reading state is"):
            if line.split(":")[1] == "activated":
                state = 1
        else:
            continue

    tag = "sensor=DCMI_Power"
    field = f"status={state},value={value},unit=\"{unit}\""
    points.append('smc_ipmi,{} {}'.format(tag, field))
    return points


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='SMCIpmi input plugin')
    parser.add_argument('ip', help='IP address of Supermicro host')
    parser.add_argument('user', help='Username')
    parser.add_argument('password', help='Password')

    args = parser.parse_args()

    ipmi_out = get_ipmi_sensor(args.ip, args.user, args.password)
    pminfo_out = get_pminfo(args.ip, args.user, args.password)

    ipmi_points = parse_ipmi_sensor(ipmi_out)
    pmbus_points = parse_pminfo(pminfo_out)

    points = ipmi_points + pmbus_points

    print(*points, sep='\n')
