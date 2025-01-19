import streamlit as st
import requests
import datetime
from datetime import timedelta
import pytz
import re
from PIL import Image

# 페이지 기본 설정
st.set_page_config(page_title="PLC 주차 등록", layout="wide")

# CSS 스타일 정의
st.markdown("""
<style>
    /* 전체 페이지 배경색 설정 */
    .stApp {
        background-color: #323648 !important;
    }
    
    /* 모든 div 요소에 대한 배경색 설정 */
    div.stMarkdown,
    div.stButton,
    div.stTextInput,
    div.row-widget,
    div.stAlert,
    div[data-testid="stMarkdownContainer"],
    div[data-testid="stVerticalBlock"] {
        background-color: #323648 !important;
    }
    
    /* 로고 컨테이너 */
    .logo-container {
        text-align: center;
        padding: 20px 0;
        background-color: #323648 !important;
    }
    
    /* 입력 필드 스타일 */
    .stTextInput > div > div > input {
        background-color: #4F6380 !important;
        color: white !important;
    }
    
    /* 버튼 스타일 */
    .stButton > button {
        background-color: #4F6380 !important;
        color: white !important;
    }
    
    /* 경고/성공 메시지 스타일 */
    .stAlert {
        background-color: #4F6380 !important;
        color: white !important;
    }
    
    /* 기타 텍스트 색상 */
    .stMarkdown {
        color: white !important;
    }
    
    /* 제목 스타일 */
    .title {
        color: white !important;
        font-size: 42px;
        font-weight: bold;
        padding: 20px 0;
        text-align: center;
        background-color: #4F6380 !important;
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    /* iframe 배경색 설정 */
    iframe {
        background-color: #323648 !important;
    }
</style>
""", unsafe_allow_html=True)

# 로고 추가
try:
    logo = Image.open('PLC logo.png')
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image(logo, width=500, use_container_width=False)  # 로고 크기를 300에서 500으로 증가
    st.markdown('</div>', unsafe_allow_html=True)
except Exception as e:
    st.error("로고 이미지를 불러오는데 실패했습니다.")

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

# 차량번호 표준화 및 검증 함수
def validate_car_number(number):
    # 모든 공백 제거
    number = re.sub(r'\s+', '', number)
    
    # 차량번호 패턴 검사 (7자리 또는 8자리)
    pattern = r'^(\d{2,3}[가-힣]\d{4})$'
    if not re.match(pattern, number):
        return False, number, "올바른 차량번호 형식이 아닙니다. 예시: 12가3456 또는 123가4567"
    
    # 길이 검사
    if len(number) not in [7, 8]:
        return False, number, "차량번호는 7자리(예: 12가3456) 또는 8자리(예: 123가4567)여야 합니다."
    
    return True, number, "유효한 차량번호입니다."

# 세션 상태 초기화
if 'admin_mode' not in st.session_state:
    st.session_state.admin_mode = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'processing' not in st.session_state:
    st.session_state.processing = False

# 운영 시간 설정
MORNING_START = datetime.time(9, 0)   # 오전 9시
MORNING_END = datetime.time(13, 0)    # 오후 1시
AFTERNOON_START = datetime.time(14, 30)  # 오후 2시 30분
AFTERNOON_END = datetime.time(17, 0)   # 오후 5시

# 현재 한국 시간 가져오기
current_time = datetime.datetime.now(KST).time()
is_morning_hours = MORNING_START <= current_time <= MORNING_END
is_afternoon_hours = AFTERNOON_START <= current_time <= AFTERNOON_END
is_operating_hours = is_morning_hours or is_afternoon_hours

# 현재 시간 표시
st.write(f"현재 시간: {current_time.strftime('%H:%M')} (KST)")

# 운영 시간이 아니고 관리자 모드가 아닐 경우 안내 메시지 표시
if not is_operating_hours and not st.session_state.admin_mode:
    st.title("주차 등록 불가 시간 ⚠️")
    st.write("지금은 주차등록 시간대가 아닙니다. 아래의 시간대에 접속해서 등록을 해주시기 바랍니다.")
    st.write("")
    st.write("오전등록: 09시-13시")
    st.write("오후등록: 14시30분-17시")
    st.write("")
    st.write("오전과 오후 중 한 번만 등록 가능합니다.")
    st.write("등록 시 주차 3시간 무료제공됩니다.")

# 모든 UI 요소 이후에 빈 공간 추가
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")
st.write("")

# 구분선 추가
st.markdown("---")

# 관리자 모드 UI를 완전 최하단에 배치
col1, col2, col3 = st.columns([6, 2, 2])
with col3:
    if st.button("관리자 모드" if not st.session_state.admin_mode else "일반 모드로 전환"):
        if not st.session_state.admin_mode:
            admin_password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
            if admin_password == "2580":
                st.session_state.admin_mode = True
                st.experimental_rerun()
            elif admin_password:
                st.error("비밀번호가 올바르지 않습니다.")
        else:
            st.session_state.admin_mode = False
            st.experimental_rerun()

# 관리자 모드 활성화 표시를 버튼 옆에 배치
with col2:
    if st.session_state.admin_mode:
        st.warning("⚠️ 관리자 모드 활성화됨")

# 운영 시간이 아닐 경우 여기서 중단
if not is_operating_hours and not st.session_state.admin_mode:
    st.stop()

# Streamlit UI
st.title("PLC 차량 등록 🚗")
# 여기서 관리자 모드 경고 제거
# if st.session_state.admin_mode:
#     st.warning("⚠️ 관리자 모드 활성화됨")

st.write("아래 폼에 이름과 차량 번호를 입력해주세요.")

# 입력 폼
name = st.text_input("이름:", placeholder="예: 홍길동")
car_number = st.text_input("차량 번호:", placeholder="예: 12가3456 또는 123가4567")

# 제출 버튼과 안내 문구를 나란히 배치
col1, col2 = st.columns([1, 4])
with col1:
    submit = st.button("등록", disabled=st.session_state.submitted or st.session_state.processing)
with col2:
    st.write("⚠️ 등록 버튼을 누르신 후 5초 가량 기다리시면 '차량이 등록되었습니다'라는 문구가 뜰 때까지 기다려주세요.")
    st.write("등록 시 주차 3시간 무료제공됩니다.")

# 차량번호 입력 안내 메시지
st.write("✔️ 차량번호 입력 예시:")
st.write("- 7자리: 12가3456 (2006년 개정 번호판)")
st.write("- 8자리: 123가4567 (2019 개정 번호판)")

if submit and not st.session_state.submitted and not st.session_state.processing:
    if name and car_number:
        # 차량번호 검증
        is_valid, standardized_number, message = validate_car_number(car_number)
        if not is_valid:
            st.error(message)
            st.stop()
            
        try:
            # 처리 중 상태로 설정
            st.session_state.processing = True
            
            # 중복 체크 요청
            try:
                check_response = requests.get(
                    "https://script.google.com/macros/s/AKfycbwCPyjV8cUAvopipzo9B2L-fU5zh2EwmUQ2nApPyurw8zQns5hT5_NeCbBWQW_8RDEITg/exec",
                    params={"action": "checkDuplicate", "carNumber": standardized_number}
                )
                
                if check_response.status_code == 200:
                    try:
                        response_text = check_response.text
                        # 스프레드시트가 비어있는 경우 (첫 번째 등록인 경우)
                        if "Exception: The number of rows in the range must be at least 1" in response_text:
                            # 첫 번째 등록이므로 중복 체크를 통과하고 계속 진행
                            pass
                        else:
                            try:
                                check_data = check_response.json()
                                if check_data.get("isDuplicate", False):
                                    st.error("이미 등록된 차량번호입니다. 중복 등록은 불가능합니다.")
                                    st.session_state.processing = False
                                    st.stop()
                            except requests.exceptions.JSONDecodeError:
                                if "Error" in response_text and not "rows in the range" in response_text:
                                    st.error(f"서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                                    st.session_state.processing = False
                                    st.stop()
                    except requests.exceptions.JSONDecodeError:
                        st.error(f"서버 응답을 처리하는 중 오류가 발생했습니다. 응답: {response_text}")
                        st.session_state.processing = False
                        st.stop()
                else:
                    st.error(f"서버 오류가 발생했습니다 (상태 코드: {check_response.status_code})")
                    st.session_state.processing = False
                    st.stop()
            
            except requests.exceptions.RequestException as e:
                st.error(f"서버 연결 중 오류가 발생했습니다: {str(e)}")
                st.session_state.processing = False
                st.stop()

            # 중복이 아닌 경우 데이터 전송
            try:
                response = requests.post(
                    "https://script.google.com/macros/s/AKfycbwCPyjV8cUAvopipzo9B2L-fU5zh2EwmUQ2nApPyurw8zQns5hT5_NeCbBWQW_8RDEITg/exec",
                    json={
                        "name": name, 
                        "carNumber": standardized_number,
                        "timestamp": str(datetime.datetime.now(KST))
                    }
                )
                if response.status_code == 200:
                    response_text = response.text
                    if "Error" not in response_text:
                        st.success("차량이 등록되었습니다! 🎉")
                        st.session_state.submitted = True
                    else:
                        st.error(f"등록 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
                else:
                    st.error(f"등록에 실패했습니다 (상태 코드: {response.status_code}). 다시 시도해주세요.")
            except requests.exceptions.RequestException as e:
                st.error(f"데이터 전송 중 오류가 발생했습니다: {str(e)}")
        finally:
            # 처리가 완료되면 processing 상태를 False로 변경
            st.session_state.processing = False
    else:
        st.warning("모든 필드를 채워주세요.")

# 제출 완료 후 메시지 표시
if st.session_state.submitted:
    st.info("이미 제출이 완료되었습니다. 추가 제출이 필요한 경우 페이지를 새로고침해주세요.")
