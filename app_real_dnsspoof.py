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


def get_ifconfig_result(command):
    if command.strip() == "ifconfig" or command.strip() == "ifconfig -a":
        # return ifconfig_text
        return exec_cmd(command)
    else:
        return "허용되지 않는 명령어입니다."


def get_ping_result(command):
    return exec_cmd("timeout 5 " +command)


def get_tcpdump_result(command):
    return exec_cmd("timeout 10 " + command)


def get_nslookup_result(command):
    return exec_cmd(command)


def get_cat_result(command):
    return exec_cmd(command)
    

def get_curl_result(command):
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


