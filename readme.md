# ctf 사이트 만들기

bob12 보안제품개발트랙 황제현

### 주제 - dns 스푸핑을 피해 gilgil.net의 진짜 ip주소 알아내기

## 실행 메뉴얼

1. Linux 환경에서 압축파일을 풀거나 git clone을 받은 뒤, app.py가 있는 경로에서 app.py를 실행합니다.

2. 웹 브라우저에서 서버의 5000번 포트로 접속합니다.

3. ifconfig, ping, tcpdump, nslookup, cat, curl을 활용하여 gilgil.net의 진짜 ip주소를 찾아냅니다.

4. 사이트 하단의 [정답 입력] 버튼을 누르면 주소 입력 창이 나타납니다. 해당 창에 gilgil.net의 ip주소를 입력하면 flag를 획득합니다.

### app_real_dnsspoof.py

- app.py는 dns 스푸핑을 당한 상황에서 나타나는 각종 설정값을 임의로 보여주는 가상 환경입니다.

- 실제 dns 스푸핑이 이루어지는 환경을 구축하면, app_real_dnsspoof.py를 실행하여 ctf 환경을 구축할 수 있습니다.

- 실행 방법은 app.py와 동일하지만, 모든 명령어에 대해 실제 실행 결과를 출력하기 때문에 실제 dns 스푸핑이 발생한 환경에서의 ctf가 가능합니다.
