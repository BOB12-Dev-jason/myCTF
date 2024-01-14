from flask import Flask, render_template, request, jsonify
import re # 정규표현식
import time
import subprocess
import random

# flask 객체
app = Flask(__name__)


# 허용할 명령어 정의
allowed_command_list = [
    "ifconfig",
    "ping",
    "tcpdump",
    "nslookup",
    "cat",
    "curl"
]

resolv_conf_text = """
# This file is managed by man:systemd-resolved(8). Do not edit.
#
# This is a dynamic resolv.conf file for connecting local clients to the
# internal DNS stub resolver of systemd-resolved. This file lists all
# configured search domains.
#
# Run "resolvectl status" to see details about the uplink DNS servers
# currently in use.
#
# Third party programs must not access this file directly, but only through the
# symlink at /etc/resolv.conf. To manage man:resolv.conf(5) in a different way,
# replace this symlink by a static file or a different symlink.
#
# See man:systemd-resolved.service(8) for details about the supported modes of
# operation for /etc/resolv.conf.

nameserver 8.8.8.8
options edns0 trust-ad
"""

ifconfig_text = """
ens32: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.30.1.30  netmask 255.255.255.0  broadcast 172.30.1.255
        inet6 fe80::8a44:d440:84bb:4fb3  prefixlen 64  scopeid 0x20<link>
        ether 00:0c:29:3d:03:69  txqueuelen 1000  (Ethernet)
        RX packets 24  bytes 3279 (3.2 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 69  bytes 7576 (7.5 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 127  bytes 10522 (10.5 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 127  bytes 10522 (10.5 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
"""

spoofed_nslookup_text = """
Server:		8.8.8.8
Address:	8.8.8.8#53

Non-authoritative answer:
Name:	gilgil.net
Address: 192.168.11.23
"""

gilgil_ping_text = """
PING gilgil.net (192.168.11.23) 56(84) bytes of data.
64 바이트 (192.168.11.23 (192.168.11.23)에서): icmp_seq=1 ttl=52 시간=7.41 ms
64 바이트 (192.168.11.23 (192.168.11.23)에서): icmp_seq=2 ttl=52 시간=9.88 ms
64 바이트 (192.168.11.23 (192.168.11.23)에서): icmp_seq=3 ttl=52 시간=9.40 ms
64 바이트 (192.168.11.23 (192.168.11.23)에서): icmp_seq=4 ttl=52 시간=10.6 ms
64 바이트 (192.168.11.23 (192.168.11.23)에서): icmp_seq=5 ttl=52 시간=8.49 ms

--- gilgil.net 핑 통계 ---
5 패킷이 전송되었습니다, 5 수신되었습니다, 0% 패킷 손실, 시간 4007ms
rtt 최소/평균/최대/표준편차 = 7.410/9.157/10.607/1.111 ms
"""


gilgil_curl_text = """
<html>
<head><title>!!##$$$$ gilgil 사이트 $$$$##!!</title></head>
<body>
<center><h1>나 gilgil인데 여기 gilgil.net 맞다</h1></center>
<hr><center> 길길멘토님은 그런 말투 안써요 </center>
</body>
</html>
"""


dns_spoof_dump = """
19:33:10.762612 IP 172.30.1.30.53576 > dns.google.domain: 5679+ A? gilgil.net. (28)
19:33:10.763037 IP 172.30.1.30.51484 > dns.google.domain: 65499+ [1au] PTR? 8.8.8.8.in-addr.arpa. (49)
19:33:10.977962 IP dns.google.domain > 172.30.1.30.53576: 5679 1/0/0 A 192.168.11.23 (44)
19:33:10.979146 IP 172.30.1.30.48627 > dns.google.domain: 36458+ AAAA? gilgil.net. (28)
19:33:13.386065 IP dns.google.domain > 172.30.1.30.55168: 32715 NXDomain 0/0/1 (53)"""

dns_normal_dump = """
19:33:11.233379 IP 172.30.1.30.53576 > dns.google.domain: 5679+ A? gilgil.net. (28)
19:33:11.251240 IP 172.30.1.30.51484 > dns.google.domain: 65499+ [1au] PTR? 8.8.8.8.in-addr.arpa. (49)
19:33:11.251362 IP 172.30.1.30.48627 > dns.google.domain: 36458+ AAAA? gilgil.net. (28)
19:33:11.274142 IP dns.google.domain > 172.30.1.30.53576: 5679 1/0/0 A 175.116.97.147 (44)
19:33:13.386065 IP dns.google.domain > 172.30.1.30.55168: 32715 NXDomain 0/0/1 (53)"""


############# functions

def is_allowed_command(command):
    for pattern in allowed_command_list:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def exec_cmd(command, timeout=None):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True) # 오류도 stdout으로 가져온다.
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"
    return result


def generate_dns_dump():
    dns_dump = ""
    for _ in range(0, 5):
        num = random.randrange(0, 10)
        if num < 4:
            dns_dump += dns_normal_dump
        else:
            dns_dump += dns_spoof_dump
    return dns_dump


def get_ifconfig_result(command):
    if command.strip() == "ifconfig" or command.strip() == "ifconfig -a":
        # return ifconfig_text
        return exec_cmd(command)
    else:
        return "허용되지 않는 명령어입니다."


def get_ping_result(command):
    if "gilgil.net" in command: # gilgil.net에 대한 ping은 5초 기다린 후 미리 만들어진 ping 결과를 보여준다.
        time.sleep(5)
        return gilgil_ping_text
    else:
        return exec_cmd("timeout 5 " +command)


def get_tcpdump_result(command):
    if "udp port 53" in command:
        time.sleep(10)
        return generate_dns_dump()
    return exec_cmd("timeout 10 " + command)


def get_nslookup_result(command):
    if "gilgil.net" in command:
        return spoofed_nslookup_text
    else:
        return exec_cmd(command)


def get_cat_result(command):
    if "/etc/resolv.conf" in command:
        return resolv_conf_text
    # elif "/etc" in command:
    #     return "허용되지 않는 명령어입니다."
    else:
        return exec_cmd(command)
    

def get_curl_result(command):
    if "gilgil.net" in command:
        return gilgil_curl_text
    else:
        return exec_cmd(command)


# 웹에 입력하는 명령어들 처리
def do_simulation(command):
    if "ifconfig" in command:
        return get_ifconfig_result(command)
    
    elif "ping" in command:
        result = "** ping은 5초 동안만 실행됩니다.\n"
        return result + get_ping_result(command)
    
    elif "tcpdump" in command:
        result = "** tcpdump는 10초 동안만 실행됩니다.\n"
        return result + get_tcpdump_result(command)
    
    elif "nslookup" in command:
        return get_nslookup_result(command)
    
    elif "cat" in command:
        return get_cat_result(command)
    
    elif "curl" in command:
        return get_curl_result(command)



################ routes

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/simulate", methods=["POST"])
def simulate():
    command = request.form['command']
    # print("입력 명령어:", command)
    if is_allowed_command(command):
        result = do_simulation(command)
    else:
        result="허용되지 않는 명령어입니다."

    return render_template("index.html", command=command, result=result)



correct_answer = "175.116.97.147"
@app.route("/answer", methods=['POST'])
def check_answer():
    user_input = request.form.get('ipAddress', '')
    # print("user_input:",user_input)
    if user_input == correct_answer:
        return jsonify({'result': '정답입니다. flag는 ytrYR2ZHb9 입니다.'})
    else:
        return jsonify({'result': '오답입니다.'})


# debug모드: 파일 저장하면 알아서 서버 다시 띄워줌, 배포 시 당연히 꺼야함.
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True) # 웹서버 띄운거임. 기본 포트 5000, debug모드 on
    # app.run(host="0.0.0.0", debug=True) -> 어디서든 접속 가능하도록 설정

    
