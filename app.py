import streamlit as st

st.set_page_config(
    page_title="연애 코칭 앱",
    page_icon="💖",
    layout="centered"
)

st.title("💖 AI 연애 코칭 앱")

st.write("현재 상황을 입력하면 연애 조언을 제공합니다.")

situation = st.text_area(
    "연애 고민 입력",
    placeholder="예: 썸 타는 사람이 답장이 느려요..."
)

if st.button("조언 받기"):

    if situation.strip() == "":
        st.warning("연애 고민을 입력해주세요.")
    else:

        text = situation.lower()

        if "답장" in text:
            advice = """
            📱 답장이 느린 경우

            너무 조급하게 재촉하지 않는 것이 중요합니다.
            상대의 생활 패턴을 존중하면서 여유 있게 대화해보세요.
            """

        elif "고백" in text:
            advice = """
            ❤️ 고백 고민

            완벽한 타이밍보다 솔직한 마음이 더 중요합니다.
            부담 없는 분위기에서 진심을 전해보세요.
            """

        elif "헤어" in text:
            advice = """
            💔 이별 고민

            감정을 억누르기보다 충분히 받아들이는 시간이 필요합니다.
            자신을 돌보는 것이 가장 우선입니다.
            """

        else:
            advice = """
            🌸 연애 조언

            상대를 바꾸려고 하기보다,
            서로의 감정을 이해하려는 태도가 가장 중요합니다.
            """

        st.success("코칭 결과")
        st.write(advice)
