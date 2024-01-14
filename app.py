from flask import Flask, render_template, request, jsonify
import re # 정규표현식
import time
import subprocess

# flask 객체
app = Flask(__name__)


# 허용할 명령어 정의
allowed_command_list = [
    "ifconfig",
    "ping",
    "tcpdump",
    "nslookup",
    "cat"
]


############# functions

def is_allowed_command(command):
    for pattern in allowed_command_list:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def exec_cmd(command, timeout=None):
    try:
        # result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True) # 오류도 stdout으로 가져온다.
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        result, error = process.communicate(timeout=timeout)
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"
    return result


def get_ifconfig_result():
    return """
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


def get_ping_result(command):
    # result = exec_cmd(f"ping -n 5 {ipAddress}")
    result = exec_cmd(command)
    # ping은 5번만 띄워줌
    return result


def get_tcpdump_result(command):
    return "tcpdump 미구현"


def get_nslookup_result(command):
    return "nslookup 미구현"


def get_cat_result(command):
    return "cat 미구현"


# 웹에 입력하는 명령어들 처리
def do_simulation(command):
    if "ifconfig" in command:
        return get_ifconfig_result()
    elif "ping" in command:
        # ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b') # 1.2.3.4 패턴 찾기
        # match = ip_pattern.search(command)
        # if match:
        #     ipAddress = match.group()
        #     # print("match.group():",ipAddress) # test code
        #     return get_ping_result(ipAddress)
        # else:
        #     return "ip주소를 입력하세요."
        return get_ping_result(command, 5)
    elif "tcpdump" in command:
        return get_tcpdump_result()
    elif "nslookup" in command:
        return get_nslookup_result()
    elif "cat" in command:
        return get_cat_result()



################ routes

@app.route("/")
def home():
    return render_template("index.html")



@app.route("/simulate", methods=["POST"])
def simulate():
    command = request.form['command']
    print("입력 명령어:", command)
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
        return jsonify({'result': '정답입니다. flag는 000입니다.'})
    else:
        return jsonify({'result': '오답입니다.'})


# debug모드: 파일 저장하면 알아서 서버 다시 띄워줌, 배포 시 당연히 꺼야함.
if __name__ == "__main__":
    app.run(debug=True) # 웹서버 띄운거임. 기본 포트 5000, debug모드 on
    # app.run(host="0.0.0.0", debug=True) -> 어디서든 접속 가능하도록 설정




# time.sleep(2) # arp 명령을 2초 딜레이 시키고 싶은 경우
        # return get_arp_result()
    
