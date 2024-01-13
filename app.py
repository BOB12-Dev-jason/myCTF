from flask import Flask, render_template, request, jsonify
import re # 정규표현식
import time
import subprocess

# flask 객체
app = Flask(__name__)


# 허용할 명령어 정의
allowed_command_list = [
    "ifconfig",
    "arp",
    "ping",
    "arping",
    "icmp"
]


############# functions

def is_allowed_command(command):
    for pattern in allowed_command_list:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def exec_cmd(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True) # 오류도 stdout으로 가져온다.
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"
    return result


def get_ifconfig_result():
    return """
lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        inet6 ::1  prefixlen 128  scopeid 0x10<host>
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 308694  bytes 1101664835 (1.1 GB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 308694  bytes 1101664835 (1.1 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0


enp0s5: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 192.168.1.10  netmask 255.255.255.0  broadcast 192.168.1.255
        inet6 fe80::fcb1:2d4d:5c7b:b6cf  prefixlen 64  scopeid 0x20<link>
        ether 97:63:8c:da:42:2b  txqueuelen 1000  (Ethernet)
        RX packets 32505950  bytes 42529149851 (42.5 GB)
        RX errors 0  dropped 9  overruns 0  frame 0
        TX packets 14224107  bytes 3710812520 (3.7 GB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
"""


def get_arp_result():
    return "arp 결과 구현예정"


# 웹에 입력하는 명령어들 처리
def do_simulation(command):
    if "ifconfig" in command:
        return get_ifconfig_result()
    elif "arp" in command:
        # time.sleep(2) # arp 명령을 2초 딜레이 시키고 싶은 경우
        # return get_arp_result()
        return exec_cmd('arp -a')





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



correct_answer = "1.1.1.1"
@app.route("/answer", methods=['POST'])
def check_answer():
    user_input = request.form.get('macAddress', '')
    # print("user_input:",user_input)
    if user_input == correct_answer:
        return jsonify({'result': '정답입니다. flag는 000입니다.'})
    else:
        return jsonify({'result': '오답입니다.'})


# debug모드: 파일 저장하면 알아서 서버 다시 띄워줌, 배포 시 당연히 꺼야함.
if __name__ == "__main__":
    app.run(debug=True) # 웹서버 띄운거임. 기본 포트 5000, debug모드 on
    # app.run(host="0.0.0.0", debug=True) -> 어디서든 접속 가능하도록 설정


