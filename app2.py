import streamlit as st
import requests
import datetime

# 운영 시간 설정
MORNING_START = datetime.time(9, 0)   # 오전 9시
MORNING_END = datetime.time(13, 0)    # 오후 1시
AFTERNOON_START = datetime.time(14, 30)  # 오후 2시 30분
AFTERNOON_END = datetime.time(17, 0)   # 오후 5시

# 현재 시간이 운영 시간 내인지 확인
current_time = datetime.datetime.now().time()
is_morning_hours = MORNING_START <= current_time <= MORNING_END
is_afternoon_hours = AFTERNOON_START <= current_time <= AFTERNOON_END
is_operating_hours = is_morning_hours or is_afternoon_hours

# 운영 시간이 아닐 경우 안내 메시지 표시
if not is_operating_hours:
    st.title("주차 등록 불가 시간 ⚠️")
    st.write("지금은 주차등록 시간대가 아닙니다. 아래의 시간대에 접속해서 등록을 해주시기 바랍니다.")
    st.write("")
    st.write("오전등록: 09시-13시")
    st.write("오후등록: 14시30분-17시")
    st.write("")
    st.write("오전과 오후 중 한 번만 등록 가능합니다.")
    st.write("중복 등록 안 됩니다.")
    st.write("등록하셔도 시간 추가되지 않습니다.")
    st.stop()  # 여기서 앱 실행을 중단

# 세션 상태 초기화 (제출 상태 및 처리 중 상태 추적)
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'processing' not in st.session_state:
    st.session_state.processing = False

# Streamlit UI
st.title("PLC 차량 등록 🚗")
st.write("아래 폼에 이름과 차량 번호를 입력해주세요.")

# 입력 폼
name = st.text_input("이름:", placeholder="예: 홍길동")
car_number = st.text_input("차량 번호:", placeholder="예: 12가 3456")

# 제출 버튼과 안내 문구를 나란히 배치
col1, col2 = st.columns([1, 4])
with col1:
    submit = st.button("등록", disabled=st.session_state.submitted or st.session_state.processing)
with col2:
    st.write("⚠️ 등록 버튼을 누르신 후 2초 가량 기다리시면 '차량이 등록되었습니다'라는 문구가 뜰 때까지 기다려주세요.")

if submit and not st.session_state.submitted and not st.session_state.processing:
    if name and car_number:
        try:
            # 처리 중 상태로 설정
            st.session_state.processing = True
            
            # Google Apps Script로 데이터 전송
            response = requests.post(
                "https://script.google.com/macros/s/AKfycbwCPyjV8cUAvopipzo9B2L-fU5zh2EwmUQ2nApPyurw8zQns5hT5_NeCbBWQW_8RDEITg/exec",
                json={"name": name, "carNumber": car_number, "timestamp": str(datetime.datetime.now())},
            )
            if response.status_code == 200:
                st.success("차량이 등록되었습니다! 🎉")
                st.session_state.submitted = True
            else:
                st.error("등록에 실패했습니다. 다시 시도해주세요.")
        finally:
            # 처리가 완료되면 processing 상태를 False로 변경
            st.session_state.processing = False
    else:
        st.warning("모든 필드를 채워주세요.")

# 제출 완료 후 메시지 표시
if st.session_state.submitted:
    st.info("이미 제출이 완료되었습니다. 추가 제출이 필요한 경우 페이지를 새로고침해주세요.")
