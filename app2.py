import streamlit as st
import requests
import datetime

# 세션 상태 초기화 (제출 상태 추적)
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

# Streamlit UI
st.title("PLC 차량 등록 🚗")
st.write("아래 폼에 이름과 차량 번호를 입력해주세요.")

# 입력 폼
name = st.text_input("이름:", placeholder="예: 홍길동")
car_number = st.text_input("차량 번호:", placeholder="예: 12가 3456")

# 제출 버튼 (이미 제출된 경우 비활성화)
submit = st.button("제출", disabled=st.session_state.submitted)

if submit and not st.session_state.submitted:
    if name and car_number:
        # Google Apps Script로 데이터 전송
        response = requests.post(
            "https://script.google.com/macros/s/AKfycbwCPyjV8cUAvopipzo9B2L-fU5zh2EwmUQ2nApPyurw8zQns5hT5_NeCbBWQW_8RDEITg/exec",
            json={"name": name, "carNumber": car_number, "timestamp": str(datetime.datetime.now())},
        )
        if response.status_code == 200:
            st.success("정보가 성공적으로 저장되었습니다! 🎉")
            st.session_state.submitted = True  # 제출 상태를 True로 변경
        else:
            st.error("저장에 실패했습니다. 다시 시도해주세요.")
    else:
        st.warning("모든 필드를 채워주세요.")

# 제출 완료 후 메시지 표시
if st.session_state.submitted:
    st.info("이미 제출이 완료되었습니다. 추가 제출이 필요한 경우 페이지를 새로고침해주세요.")
