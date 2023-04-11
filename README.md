# smc_ipmi Telegraf input plugin
Python scripts to parse the output of [SMCIPMITool](https://www.supermicro.com/en/solutions/management-software/ipmi-utilities) or [ipmitool](https://github.com/ipmitool/ipmitool) into the [InfluxDB line protocol](https://docs.influxdata.com/influxdb/latest/reference/syntax/line-protocol/). Intended to be run via Telegraf's [exec](https://github.com/influxdata/telegraf/tree/master/plugins/inputs/exec) input plugin.

## Requirements
The SMCIPMITool [[download]](https://www.supermicro.com/SwDownload/SwSelect_Free.aspx?cat=IPMI) must be installed on the Telegraf host.

## Why?
The value of this vs the Telegraf [IPMI input](https://github.com/influxdata/telegraf/blob/release-1.26/plugins/inputs/ipmi_sensor/README.md) is gathering the PMBus details. The SMCIPMITool solution will give you more information about the state of the power supplies as well as the ability to use F temperatures if you prefer. The ipmitool solution gives most of the same data as the Telegraf plugin but also adds in the DCMI power information.

The biggest disadvantage of either of these solutions is performance; the host where this is running will have a more significant performance impact due to using Python (and Java as well when using SMCIPMITool) instead of the built in plugin.

## Install
Clone this repo to the Telegraf host and configure Telegraf as shown below.

## Configuration

### SMCIPMITool solution
This solution is much slower and much more CPU intensive but it collects more power information and per-PSU metrics

`/etc/telegraf/telegraf.conf`
```
[[inputs.exec]]
   commands = ["/path/to/smc_ipmi.py /path/to/SCMIPMITool '192.168.1.2' 'ipmi_user' 'ipmi_pw' 'F'"]

   data_format = "influx"
   
   timeout = "9s" # Optional: This keeps the system from waiting up to 30s for metrics

  # Optional: This will add a hostname tag rather than referencing the metrics by IP.
  [inputs.exec.tags]
    hostname = "myhostname"
```

### ipmitool solution
This solution is significantly faster but only collects total system power in watts instead of detailed per-PSU metrics. Also dropped support for temperature unit selection as the IMPI direct calls provide only C.

On my monitoring VM (4 cores of Xeon CPU E5-2689 under ESXi 8) this solution reduced the metrics collection time from 5.5s to 0.5s and dropped CPU utilization (remotely monitoring 4 systems over IPMI) from 25% to 1%.

`/etc/telegraf/telegraf.conf`
```
[[inputs.exec]]
   commands = ["/path/to/smc_ipmi_ipmitool.py '192.168.1.2' 'ipmi_user' 'ipmi_pw'"]

   data_format = "influx"
   
   timeout = "9s" # Optional: This keeps the system from waiting up to 30s for metrics

  # Optional: This will add a hostname tag rather than referencing the metrics by IP.
  [inputs.exec.tags]
    hostname = "myhostname"
```

## Usage
```
usage: smc_ipmi.py [-h] path ip user password {C,F}

SMCIpmi input plugin

positional arguments:
  path        Path to SMCIpmi utility
  ip          IP address of Supermicro host
  user        Username
  password    Password
  {C,F}       Temperature unit to use

optional arguments:
  -h, --help  show this help message and exit
```

```
usage: smc_ipmi_ipmitool.py [-h] ip user password

SMCIpmi input plugin

positional arguments:
  ip          IP address of Supermicro host
  user        Username
  password    Password

optional arguments:
  -h, --help  show this help message and exit
  ```
