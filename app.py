import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="짠테크 요정 키우기", page_icon="🌱", layout="centered")

# 2. Secrets API 키 검증 및 클라이언트 생성
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다.")
    st.stop()

try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.error(f"Gemini 클라이언트 초기화 실패: {e}")
    st.stop()

# 3. 게임 시스템 변수 및 채팅 기록 세션 초기화
if "char_exp" not in st.session_state:
    st.session_state.char_exp = 0
if "char_level" not in st.session_state:
    st.session_state.char_level = 1
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "안녕! 나는 네 절약 에너지를 먹고 자라는 '돈 아끼 요정'이야. 오늘 어떤 돈을 아꼈는지 말해줘! 푼돈도 대환영이야! 🌱"}
    ]

# 캐릭터 상태 업데이트 함수
def add_exp(amount):
    # 아낀 금액에 비례하여 경험치 지급 (예: 1,000원당 10 EXP, 최소 10 EXP)
    gained_exp = max(10, int(amount // 100))
    st.session_state.char_exp += gained_exp
    
    # 레벨업 로직 (100 EXP마다 레벨업)
    if st.session_state.char_exp >= 100:
        st.session_state.char_level += st.session_state.char_exp // 100
        st.session_state.char_exp %= 100
        return f"🎉 **레벨 업!** 요정이 더 멋지게 자라났습니다! (현재 Lv.{st.session_state.char_level})"
    return f"✨ 요정이 경험치를 {gained_exp} 획득했습니다!"

# 캐릭터 외형 결정
def get_character_emoji(lvl):
    if lvl >= 5: return "👑 진화 완료! 경제적 자유의 신"
    elif lvl >= 4: return "🧚 대천사 요정 (저축 마스터)"
    elif lvl >= 3: return "🌿 무럭무럭 자란 나무 요정"
    elif lvl >= 2: return "🌱 귀여운 새싹 요정"
    else: return "🥚 알 형태의 아기 요정"

# 4. UI 레이아웃 (상단 대시보드)
st.title("🌱 짠테크 요정 키우기")
st.caption("돈을 아낀 스토리를 쓰면 캐릭터가 성장하는 AI 대화방")

st.info(f"**현재 캐릭터 상태:** {get_character_emoji(st.session_state.char_level)} (Lv.{st.session_state.char_level})")
# 경험치 바 표시
st.progress(min(st.session_state.char_exp / 100, 1.0), text=f"EXP: {st.session_state.char_exp}/100")

st.divider()

# 5. 채팅 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 6. 유저 입력 및 AI 반응 처리
if prompt := st.chat_input("예: 오늘 커피값 5000원 아끼고 텀블러 썼어!"):
    # 유저 메시지 화면 표시 및 저장
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # 캐릭터 컨셉을 주입하는 시스템 프롬프트 작성
            system_instruction = (
                f"당신은 사용자가 돈을 아낀 행동을 칭찬하고 격려해 주는 '절약 요정' 캐릭터입니다. "
                f"현재 당신의 레벨은 Lv.{st.session_state.char_level}입니다. 레벨에 맞는 말투를 사용해 주세요. "
                f"(Lv.1~2: 귀여운 아기 말투, Lv.3~4: 든든한 조력자 말투, Lv.5 이상: 지혜로운 경제 전문가 말투)\n"
                f"사용자가 돈을 아낀 내용을 이야기하면 폭풍 칭찬을 해주고, 대화 마지막에는 "
                f"[SYSTEM_GOLD: 아낀금액] 형식으로 대략 얼마를 아낀 것 같은지 숫자로 추정해 적어주세요. "
                f"예를 들어 5000원을 아꼈다면 대답 맨 끝에 [SYSTEM_GOLD: 5000]을 붙여야 합니다. 금액 추정이 어려우면 [SYSTEM_GOLD: 1000]으로 통일하세요."
            )
            
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7,
            )
            
            # Gemini 2.5 Flash-Lite 스트리밍 호출
            response_stream = client.models.generate_content_stream(
                model='gemini-2.5-flash-lite',
                contents=prompt,
                config=config
            )
            
            for chunk in response_stream:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
            
            # 후처리: 시스템 명령어([SYSTEM_GOLD: XXXX]) 파싱 및 UI 분리
            saved_money = 1000 # 기본값
            if "[SYSTEM_GOLD:" in full_response:
                try:
                    parts = full_response.split("[SYSTEM_GOLD:")
                    clean_response = parts[0].strip()
                    gold_amount = int(parts[1].replace("]", "").strip())
                    saved_money = gold_amount
                    full_response = clean_response # 유저에게는 명령어가 안 보이게 처리
                except:
                    pass
            
            message_placeholder.markdown(full_response)
            
            # 경험치 정산 및 레벨업 체크 후 알림 추가
            lvl_msg = add_exp(saved_money)
            st.toast(f"💰 {saved_money}원 절약 인정! {lvl_msg}")
            
            # 세션에 최종 대화 저장 (다음 리런 시 상태 반영을 위해 앱 리런)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            st.rerun()

        except APIError as ae:
            error_msg = f"🚫 Gemini API 오류가 발생했습니다: {ae.message}"
            message_placeholder.markdown(error_msg)
        except Exception as e:
            error_msg = f"🚫 오류가 발생했습니다: {str(e)}"
            message_placeholder.markdown(error
