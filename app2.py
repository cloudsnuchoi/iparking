import streamlit as st
import requests
import datetime

# Streamlit UI
st.title("차량 정보 입력 시스템 🚗")
st.write("아래 폼에 이름과 차량 번호를 입력해주세요.")

# 입력 폼
name = st.text_input("이름:")
car_number = st.text_input("차량 번호:")
submit = st.button("제출")

if submit:
    if name and car_number:
        # Google Apps Script로 데이터 전송
        response = requests.post(
            "https://script.google.com/macros/s/AKfycbwCPyjV8cUAvopipzo9B2L-fU5zh2EwmUQ2nApPyurw8zQns5hT5_NeCbBWQW_8RDEITg/exec",
            json={"name": name, "carNumber": car_number, "timestamp": str(datetime.datetime.now())},
        )
        if response.status_code == 200:
            st.success("정보가 성공적으로 저장되었습니다! 🎉")
        else:
            st.error("저장에 실패했습니다. 다시 시도해주세요.")
    else:
        st.warning("모든 필드를 채워주세요.")
