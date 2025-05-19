import streamlit as st
import google.generativeai as genai
import time

# 초등학생 기준 안전 설정
safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}

]

# 페르소나 설정
personas = {
    "이순신": {
        "persona": """
            당신은 조선 시대의 명장 이순신 장군입니다. 임진왜란 때 조선을 지키기 위해 바다에서 일본 군대를 막아낸 훌륭한 해군 장군입니다.

            다음과 같은 성격과 말투를 가지고 대화합니다:

            1. 조국 사랑: 조선과 백성을 누구보다 아끼며, 나라를 위해 싸운 영웅입니다.
            2. 책임감: 어려운 상황에서도 끝까지 포기하지 않고 책임을 다합니다.
            3. 지혜로움: 전쟁에서 여러 가지 전략을 잘 세워서 적을 이긴 경험이 많습니다.
            4. 정직함: 항상 바른 길을 가려고 노력하며, 거짓말을 싫어합니다.
            5. 격식 있는 말투: 조선 시대답게 고운 존댓말을 사용합니다.

            장군님은 백성의 안전과 나라의 평화를 위해 항상 마음을 씁니다. 아이들과도 따뜻하고 친절하게 이야기합니다.
        """,
        "example_questions": [
            "가장 힘들었던 전투는 무엇이었나요?",
            "거북선을 어떻게 만들게 되셨나요?",
            "전쟁 중 가장 기억에 남는 순간은 언제인가요?"
        ],
        "display_name": "이순신"
    },
    "세종대왕": {
        "persona": """
            당신은 조선의 제4대 임금, 세종대왕입니다. 훈민정음을 만들어 백성들이 쉽게 글을 읽고 쓸 수 있도록 도와주신 위대한 왕입니다.

            다음과 같은 성격과 말투를 가지고 대화합니다:

            1. 백성 사랑: 힘든 사람들을 잘 보살피고, 백성이 편하게 살도록 여러 가지 제도를 만들었습니다.
            2. 똑똑함: 과학, 음악, 농사, 의학 등 여러 분야에 관심이 많아 훌륭한 학자들과 함께 많은 것을 발전시켰습니다.
            3. 겸손함: 왕이지만 항상 겸손한 자세로 신하들과 이야기하며, 좋은 의견을 잘 들어줍니다.
            4. 공정함: 옳고 그름을 잘 판단하고, 누구에게나 공평하게 대합니다.
            5. 따뜻한 말투: 백성을 사랑하는 마음으로 따뜻하고 정중한 말을 씁니다.

            세종대왕은 어린이들에게도 글과 배움을 소중히 여기라고 말해줍니다. 언제든 친절하게 질문에 답해줍니다.
        """,
        "example_questions": [
            "한글을 만드시시게 된 이유가 무엇인가요?",
            "과학에도 관심이 많으셨다는데 어떤 걸 발명하셨나요?",
            "백성을 사랑하는 마음과 관련된 일화가 있나요?"
        ],
        "display_name": "세종대왕"
    },
    "신사임당": {
        "persona": """
            당신은 조선 중기의 여성 예술가이자 교육자인 신사임당입니다. 자녀 교육에 힘쓰며, 시와 그림, 바느질, 살림까지 잘하는 현명한 어머니였습니다.

            다음과 같은 성격과 말투를 가지고 대화합니다:

            1. 따뜻함: 아이들을 보듬고 사랑으로 가르칩니다.
            2. 슬기로움: 가정과 예술, 공부의 균형을 잘 잡습니다.
            3. 성실함: 언제나 부지런히 하루를 살아갑니다.
            4. 온화한 말투로 대화하며, 삶의 지혜를 쉽게 전해줍니다.

            배움은 어렵지 않으며, 마음을 다해 노력하면 누구든지 훌륭한 사람이 될 수 있다고 알려줍니다.
        """,
        "example_questions": [
            "아이들을 어떻게 가르치셨나요?",
            "어떤 그림을 그리셨는지 궁금해요!",
            "가정생활에서 가장 중요하게 생각한 것은 무엇인가요?"
        ],
        "display_name": "신사임당"
    }
}

st.title('역사 속 인물 챗봇')
# API 키 입력
if 'api_key_configured' not in st.session_state:
    st.session_state.api_key_configured = False

if not st.session_state.api_key_configured:
    api_key = st.text_input("API 키", type="password")
    if st.button("API 키 설정", icon="🔑"):
        if api_key:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-pro')
                model.generate_content("test")
                st.session_state.api_key = api_key
                st.session_state.api_key_configured = True
                st.success("API 키 설정 완료!")
                st.rerun()
            except Exception as e:
                st.error(f"API 키 오류: {str(e)}")
        else:
            st.warning("API 키를 입력하세요.")
    st.stop()


# 인물 선택
selected_figure = st.sidebar.selectbox("채팅할 인물:", list(personas.keys()))

# 챗봇 초기화
if 'chat_bot' not in st.session_state:
    st.session_state.chat_bot = genai.GenerativeModel(
        'gemini-1.5-pro', safety_settings=safety_settings
    ).start_chat(history=[])

if 'messages' not in st.session_state:
    st.session_state.messages = []

# 페르소나 설정
persona_text = personas[selected_figure]["persona"]
character_name = personas[selected_figure]["display_name"]
example_questions = personas[selected_figure].get("example_questions", [])


# 응답 생성 함수
def generate_response(persona, character_name, user_input):
    try:
        prompt = f"""{persona}

사용자: {user_input}

{character_name}으로서 응답:"""
        response = st.session_state.chat_bot.send_message(prompt, stream=False)
        return response.text if response.text else None
    except Exception as e:
        st.error(f"오류 발생: {str(e)}")
        return None

# 재시도 포함 함수
def generate_response_with_retry(persona, character_name, user_input, max_retries=3):
    for attempt in range(max_retries):
        response = generate_response(persona, character_name, user_input)
        if response:
            return response
        time.sleep((attempt + 1) * 2)
    return None


# 예시 질문 표시
st.sidebar.write("예시 질문:")
for idx, question in enumerate(example_questions):
    if st.sidebar.button(question, key=f"q{idx}"):
        st.session_state.messages.append({"role": "사용자", "content": question})
        with st.chat_message("나"):
            st.write(question)
        with st.chat_message(character_name):
            response = generate_response_with_retry(persona_text, character_name, question)
            if response:
                st.session_state.messages.append({"role": character_name, "content": response})
            st.rerun()

# 채팅 출력
for message in st.session_state.messages:
    with st.chat_message("나" if message["role"] == "사용자" else message["role"]):
        st.write(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "사용자", "content": prompt})
    with st.chat_message("나"):
        st.write(prompt)
    with st.chat_message(character_name):
        response = generate_response_with_retry(persona_text, character_name, prompt)
        if response:
            st.session_state.messages.append({"role": character_name, "content": response})
            st.write(response)
