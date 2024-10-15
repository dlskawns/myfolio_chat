import os
import streamlit as st
from PIL import Image
from utils.prepare import (
    get_logger,
    DEFAULT_OPENAI_API_KEY,
    GEMINI_API_KEY
)
from utils.query_parsing import parse_query
from components.llm import CallbackHandlerDDGStreamlit
from utils.chat_state import ChatState
from utils.streamlit.prepare import prepare_app
from utils.helpers import (
    DELIMITER,
    GREETING_MESSAGE_KOR,
    GREETING_MESSAGE_ENG,
    VERSION,
    WALKTHROUGH_TEXT,
)
from agents.dbmanager import (
    get_user_facing_collection_name,
)
from utils.type_utils import (
    ChatMode
)
from utils.streamlit.helpers import (
    mode_options,
    career_options,
    STAND_BY_FOR_INGESTION_MESSAGE,
    status_config,
    show_sources,
    show_downloader,
    fix_markdown,    
    show_uploader,
    just_chat_status_config,
)
from streamlit_modal import Modal
from tamla import get_bot_response

# 로그 설정 
logger = get_logger()

# Show title and description.
st.logo(logo := "/Users/david/Downloads/창사챗봇/Img_Logo.png")
st.set_page_config(page_title="Tamla's Flavor", page_icon=logo)

# HTML and CSS for the logo size customization.
st.markdown("""
    <style>
        [alt=Logo] {
            height: 3rem;
        }
        code {
            color: #005F26;
            overflow-wrap: break-word;
            font-weight: 600;
        }
        [data-testid=stSidebar] {
        background-color: #f0f0f0;
        }   
        .stButton > button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
        }
        .stButton > button:hover {
            background-color: #f0f0f0;
            color: #4F8BF9;
        }
    </style>
    """, unsafe_allow_html=True) # text color for dark theme: e6e6e6

# seesion management (api key, query parameters, ...)
ss = st.session_state
if "chat_state" not in ss:
    # Run just once
    prepare_app()
    # Need to reference is_env_loaded to avoid unused import being removed
    is_env_loaded = True  # more info at the end of docdocgo.py

chat_state: ChatState = ss.chat_state

def open_ai_chat(parsed_query=None, eng_flag=False):
    if "messages" not in ss:
        ss.messages = []

    for message in ss.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat 입력창 설명 
    if eng_flag == True:
        temp_prompt = st.chat_input("How can I assist you?")
    else:
        temp_prompt = st.chat_input("무엇을 도와드릴까요?")

    if prompt := temp_prompt:
        ss.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)

        parsed_query.message = prompt
        parsed_query.chat_mode = ChatMode.JUST_CHAT_COMMAND_ID
        chat_state.update(parsed_query=parsed_query)

        with st.chat_message("assistant", avatar="🦖"):
            try:
                chat_mode = parsed_query.chat_mode
                status = st.status(status_config[chat_mode]["thinking.header"])
                status.write(status_config[chat_mode]["thinking.body"])
            except KeyError:
                status = None

            # Prepare container and callback handler for showing streaming response
            message_placeholder = st.empty()

            cb = CallbackHandlerDDGStreamlit(
                message_placeholder,
                end_str=STAND_BY_FOR_INGESTION_MESSAGE
            )
            chat_state.callbacks[1] = cb
            chat_state.add_to_output = lambda x: cb.on_llm_new_token(x, run_id=None)                

            response = get_bot_response(chat_state)
            answer = response["answer"]


            # Display the "complete" status - custom or default
            if status:
                default_status = status_config.get(chat_mode, just_chat_status_config)
                status.update(
                    label=response.get("status.header", default_status["complete.header"]),
                    state="complete",
                )
                status.write(response.get("status.body", default_status["complete.body"]))


            # Add the response to the chat history
            chat_state.chat_history.append((prompt, answer))


            message_placeholder.markdown(answer)
        ss.messages.append({"role": "assistant", "content": answer})
    # else:
    #     st.info("OpenAI API 키를 입력해주세요.", icon="🗝️")

def user_id_setting(): 
    user_id = st.sidebar.text_input("User ID", 
                                    label_visibility='visible',
                                    disabled=False,
                                    placeholder="홍길동")
    # 양쪽 공백 제거
    user_id = user_id.strip()

    if user_id == "":
        chat_state.user_id = None
    else:
        chat_state.user_id = user_id
        chat_state.chat_history.append(("사용자 이름: ", "앞으로 내 이름을 언급하면서, 친절하게 답변해줘. 내 이름: "+user_id))

def career():
    # 세션 상태 초기화
    # if 'selected_career_groups' not in chat_state:
    # chat_state.selected_career_groups = [list(career_options.keys())[1]]

    # Default mode
    with st.expander("희망 진로 선택", expanded=True):
        selected_career_groups = st.multiselect(
            "희망 진로 복수 선택 가능", # 더 맞춤형 서비스를 제공해드리겠습니다. 
            options=list(career_options.keys()),
            default=chat_state.selected_career_groups,
            key="career_multiselect"
        )
        
        # 선택된 진로 저장
        chat_state.selected_career_groups = selected_career_groups
        
        if selected_career_groups:
            cmd_prefixes = []
            cmd_prefix_explainers = []
            for career_group in selected_career_groups:
                cmd_prefix, cmd_prefix_explainer, _ = career_options[career_group]
                cmd_prefixes.append(cmd_prefix)
                cmd_prefix_explainers.append(cmd_prefix_explainer)
            
            st.caption("선택된 진로:")
            for career_group, explainer in zip(selected_career_groups, cmd_prefix_explainers):
                st.caption(f"• {career_group}: {explainer}")
        else:
            st.caption("진로를 선택해주세요.")
    

    # 선택된 진로 확인 (디버깅용)
    # st.write("현재 선택된 진로:", chat_state.selected_career_groups)

def counsel_type():
    # 세션 상태 초기화
    # if 'counsel_type' not in chat_state:
        # chat_state.counsel_type = None

    # 사이드바에 상담 유형 선택 버튼 추가
    with st.expander("상담 유형 선택", expanded=True):

        col1, col2 = st.columns(2)
        
        # 남성 버튼
        if col1.button("진학", key="school", 
                    use_container_width=True,
                    type="primary" if chat_state.counsel_type == "진학" else "secondary"):
            if chat_state.counsel_type == "진학":
                chat_state.counsel_type = None  # 이미 선택된 경우 취소
            else:
                chat_state.counsel_type = "진학"
        
        # 여성 버튼
        if col2.button("진로", key="career", 
                    use_container_width=True,
                    type="primary" if chat_state.counsel_type == "진로" else "secondary"):
            if chat_state.counsel_type == "진로":
                chat_state.counsel_type = None  # 이미 선택된 경우 취소
            else:
                chat_state.counsel_type = "진로"


def user_type():
    # 사이드바에 유저타입 선택 버튼 추가
    with st.expander("분류 선택", expanded=True):
        # st.write("## 성별 선택")
        col1, col2, col3 = st.columns(3)
        
        # 학생 버튼
        if col1.button("학생", key="s", 
                    use_container_width=True,

                    type="primary" if chat_state.user_type == "s" else "secondary"):
            chat_state.user_type = "학생"

        # 학부모 버튼
        if col2.button("학부모", key="p", 
                    use_container_width=True,
                    type="primary" if chat_state.user_type == "p" else "secondary"):
            chat_state.user_type = "학부모"
        # 교사 버튼
        if col3.button("교사", key="t", 
                    use_container_width=True,
                    type="primary" if chat_state.user_type == "t" else "secondary"):
            chat_state.user_type = "교사"


def food_selection():
    # 음식 종류 리스트
    food_types = ["한식", "일식", "중식", "양식", "멕시코 음식", "기타"]

    # 세션 상태 초기화
    # if 'selected_foods' not in st.session_state:
        # chat_state.selected_foods = []

    with st.expander("음식 종류 선택", expanded=True):
        st.write("어떤 음식을 드시고 싶으신가요? (복수 선택 가능)")
        
        cols = st.columns(3)  # 3열로 나누어 표시
        for i, food in enumerate(food_types):
            col = cols[i % 3]
            if col.button(
                food,
                key=f"food_{food}",
                help=f"{food} 선택",
                type="primary" if food in chat_state.selected_foods else "secondary"
            ):
                if food in chat_state.selected_foods:
                    chat_state.selected_foods.remove(food)
                else:
                    chat_state.selected_foods.append(food)
        
        if chat_state.selected_foods:
            st.write("선택된 음식 종류:")
            st.write(", ".join(chat_state.selected_foods))
        else:
            st.write("아직 선택된 음식이 없습니다.")

def price():
    # Settings
    with st.expander("가격대 설정", expanded=True):
        # 가격대 슬라이더
        price_range = st.slider(
            "1인 기준 가격대를 선택해주세요",
            min_value=5000,
            max_value=100000,
            value=(5000, 50000),  # Default range
            step=5000,
            format="₩%d",
        )

    # st.write(f"선택된 가격대: ₩{price_range[0]} ~ ₩{price_range[1]}")
        

def ref_dropdown():
    # Default mode
    with st.expander("진로 선택", expanded=False):
        ss.default_mode = st.selectbox(
            "진로를 선택해주시면 더 맞춤형 서비스를 제공해드리겠습니다.",
            mode_options,
            index=0,
            # label_visibility="collapsed",
        )
        cmd_prefix, cmd_prefix_explainer, _ = career_options[ss.default_mode]
        st.caption(cmd_prefix_explainer)
        
def side_bar():
    ####### Sidebar #######
    with st.sidebar:
        st.subheader("Myfolio 상담 봇 " + VERSION)

        # chat_state 설정 
        chat_state.selected_career_groups = [list(career_options.keys())[1]]
        chat_state.counsel_type = None
        chat_state.selected_foods = []


        # user 이름 설정
        user_id_setting()

        # 멘트 추가 
        st.write("아래에서 원하시는 항목을 선택해주시면, 더 맞춤형 서비스를 제공해드리겠습니다.")  # 설명을 별도로 추가

        # 차 여부 
        user_type() 

        # 성별 설정 
        counsel_type()

        # 진로 설정 
        career()

        # 가격대 설정 
        price()

        # food_selection
        food_selection()
    
def title_header(logo, title):
    # 이미지와 제목을 포함한 컨테이너 생성
    header = st.container()

    with header:
        # 두 열로 나누기
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # 첫 번째 열에 로고 이미지 표시
            st.image(logo, width=300)  # 너비를 조절하여 크기 조정
        
        with col2:
            # 두 번째 열에 제목 텍스트 표시
            st.markdown(f"# {title}")  # 큰 글씨로 제목 표시
        #fff3e0
def format_robot_response(message):
    return f'''<div style="background-color: #f0f0f0; padding: 15px; border-radius: 8px; border: 1px solid #ffb74d; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #e65100; box-shadow: 0 4px 8px rgba(0,0,0,0.1); font-size: 16px;">
        <strong>🍊:</strong> {message} </div>'''
        
def main():
    if tmp := os.getenv("STREAMLIT_WARNING_NOTIFICATION"):
        st.warning(tmp)    

    side_bar()

    # # 로고 이미지 로드
    # logo = Image.open("media/탐라logo_w_horizon.png")

    parsed_query = parse_query("")

    # 세션 상태에 페이지 상태 초기화
    if 'page' not in ss:
        ss.page = 'user_select'
    
    # 언어 선택 페이지
    if ss.page == 'user_select':
        st.title("환영합니다 / Welcome!")
        st.write("안녕하세요! 마이폴리오 chat입니다. 상담을 원하시면 아래 상담시작 버튼을 눌러주세요!")
        
        col1= st.columns(1)[0]
        
        with col1:
            if st.button("상담 시작!", use_container_width=True):
                ss.language = "상담 시작!"
                ss.page = 'main_app'
                st.rerun()
        
        # with col2:
        #     if st.button("학부모", use_container_width=True):
        #         ss.language = "학부모"
        #         ss.page = 'main_app'
        #         st.rerun()

        # with col3:
        #     if st.button("교사", use_container_width=True):
        #         ss.language = "교사"
        #         ss.page = 'main_app'
        #         st.rerun()


    # 메인 앱 페이지
    elif ss.page == 'main_app':
        if ss.language == "English":
            title_header(logo, "")
            st.title("Welcome to the Culinary Journey with Tamna's Flavor AI!")
            # English content here
            st.markdown(GREETING_MESSAGE_ENG)

            # 날씨, 시간에 따른 인사말을 세션 상태에 저장
            if 'greeting_message' not in ss:
                parsed_query.chat_mode = ChatMode.JUST_CHAT_GREETING_ID
                chat_state.flag = "영어로"
                chat_state.update(parsed_query=parsed_query)
                ss.greeting_message = get_bot_response(chat_state)
            
            # 사용자 ID에 따른 전체 메시지 생성 
            if chat_state.user_id is not None:
                full_message = f"{chat_state.user_id}님 {ss.greeting_message}"
            else: 
                full_message = ss.greeting_message
            
            # 채팅 히스토리에 메시지 추가 (필요한 경우)
            if full_message not in [msg for msg, _ in chat_state.chat_history]:
                chat_state.chat_history.append((full_message, ""))
                chat_state.chat_history_all.append((None, full_message))
                chat_state.sources_history.append(None)

            st.markdown(format_robot_response(full_message), unsafe_allow_html=True)
            
            # st.write(
            #     "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
            #     "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
            # )

            # Show sample queries
            clicked_sample_query = None
            for _ in range(2):
                st.write("")
            for i, (btn_col, sample_query) in enumerate(zip(st.columns(2), ss.sample_queries)):
                with btn_col:
                    if st.button(sample_query, key=f"query{i}"):
                        clicked_sample_query = sample_query
            
            open_ai_chat(parsed_query=parsed_query, eng_flag=True)
        
        else:
            title_header(logo, "")
            st.title("Myfolio의 AI 봇과 함께하는 진로/진학 상담 서비스입니다.")
            # Korean content here
            st.markdown(GREETING_MESSAGE_KOR)

            # 날씨, 시간에 따른 인사말을 세션 상태에 저장
            if 'greeting_message' not in ss:
                parsed_query.chat_mode = ChatMode.JUST_CHAT_GREETING_ID
                chat_state.flag = ""
                chat_state.update(parsed_query=parsed_query)
                ss.greeting_message = get_bot_response(chat_state)
            
            # 사용자 ID에 따른 전체 메시지 생성 
            if chat_state.user_id is not None:
                full_message = f"{chat_state.user_id}님 {ss.greeting_message}"
            else: 
                full_message = ss.greeting_message
            
            # 채팅 히스토리에 메시지 추가 (필요한 경우)
            if full_message not in [msg for msg, _ in chat_state.chat_history]:
                chat_state.chat_history.append((full_message, ""))
                chat_state.chat_history_all.append((None, full_message))
                chat_state.sources_history.append(None)

            st.markdown(format_robot_response(full_message), unsafe_allow_html=True)

            # Show sample queries
            clicked_sample_query = None
            for _ in range(2):
                st.write("")
            for i, (btn_col, sample_query) in enumerate(zip(st.columns(2), ss.sample_queries_kor)):
                with btn_col:
                    if st.button(sample_query, key=f"query{i}"):
                        clicked_sample_query = sample_query   


            open_ai_chat(parsed_query=parsed_query)


if __name__ == '__main__':
    main()  
