## AWS Session Manager 슬랙 알람

### 동작
- 서버에서 cronjob으로 1분마다 실행
- 마지막 60.1초 동안 생성되었던 session에 대해 slack 알람
- tag로 특정 서버만 지정
