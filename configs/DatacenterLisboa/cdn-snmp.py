import subprocess
import pprint


def calc_percentage_utilization(ip):
    # cpmCPUTotal5secRev (.1.3.6.1.4.1.9.9.109.1.1.1.1.6):
    # The overall CPU busy percentage in the last five-second period.
    # This object deprecates the object cpmCPUTotal5sec and increases the value range to (0..100).

    cmd = "snmpwalk -v3 -u user1 -A authpass -X encpassword -l authpriv " + ip + " .1.3.6.1.4.1.9.9.109.1.1.1.1.6"
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

    cpu_utilization = int(output.replace("iso.3.6.1.4.1.9.9.109.1.1.1.1.6.1 = Gauge32: ", ""))
    return cpu_utilization


if __name__ == '__main__':
    routers = {
        "aveiro": {
            "router_ip": "10.0.10.3",
            "datacenter_ip": "10.2.2.2",
            "cpu": 0,
            "file": "/etc/bind/aracdn.com-aveiro.db"
        },
        "oeiras": {
            "router_ip": "10.0.10.4",
            "datacenter_ip": "10.2.3.2",
            "cpu": 0,
            "file": "/etc/bind/aracdn.com-oeiras.db"
        },
        "lisboa2": {
            "router_ip": "10.0.10.2",
            "datacenter_ip": "10.2.1.2",
            "cpu": 0,
            "file": "/etc/bind/aracdn.com-other.db"
        }
    }

    for key in routers:
        routers[key]["cpu"] = calc_percentage_utilization(routers[key]["router_ip"])

    # define threshould
    # 0-100
    # set to 2 if want to show something
    threshould = 10
    print("threshould: %d" % threshould)

    # get the min cpu usage
    min_cpu_key = "aveiro"

    for key in routers:
        if routers[key] < routers[min_cpu_key]:
            min_cpu_key = key

    # utilization decision
    for key in routers:
        if routers[key]["cpu"] > threshould:
            # send answer to the min server
            routers[key]["datacenter_ip"] = routers[min_cpu_key]["datacenter_ip"]

    # write DNS file
    for key in routers:
        line_number = 10
        f = open(routers[key]["file"], "r")
        contents = f.readlines()
        f.close()

        contents[line_number-1] = "    IN A " + routers[key]["datacenter_ip"] + "\n"

        f = open(routers[key]["file"], "w")
        contents = "".join(contents)
        f.write(contents)
        f.close()

        # named-checkzone aracdn.com
        cmd = "named-checkzone aracdn.com " + routers[key]["file"]
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        p_status = p.wait()
        print(output)

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(routers)