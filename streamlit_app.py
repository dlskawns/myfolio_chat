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
import math
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
import ast
from dotenv import load_dotenv

load_dotenv()
def display_store_info_major(data):
    # 관련자격 (링크 추가)
# newlist = [x for x in mylist if math.isnan(x) == False]
    subject_name = data.get('subject_name', '').split(', ') if data.get('subject_name', '') else ''
    linked_subject = []
    for subject in subject_name:
        # 괄호로 URL을 분리
        if '(' in subject and ')' in subject and subject:
            name, url = subject.split('(')
            url = url.replace(")", "").strip()
            linked_subject.append(f"<a href='{url}' target='_blank' style='text-decoration: none; color: #007bff;'>{name.strip()}</a>")
        else:
            linked_subject.append(subject.strip())
    content = "<div style='font-family: sans-serif; padding: 10px;'>"

    # 직업명
    content += "<p><b>🔍 연봉 정보</b></p>"
    content += f"<p>평균 월 {int(data.get('salary', ''))}만원</p>"
    
    content += f"<br>"

    # 관련직업명
    content += "<p><b>🔍 분야</b></p>"
    content += f"<p>{data.get('department', '') if data.get('department', '') else ''}</p>"
    
    content += f"<br>"

    # 요약능력
    content += "<p><b>🔑 자격 및 면허</b></p>"
    content += f"<p>{data.get('qualifications', '') if data.get('qualifications', '') else ''}</p>"

    content += f"<br>"

    # 적성 및 흥미
    content += "<p><b>💡 적성 및 흥미</b></p>"
    content += f"<p><b>적성:</b> {data.get('property', '') if data.get('property', '') else ''}</p>"
    content += f"<p><b>흥미:</b> {data.get('interest', '') if data.get('interest', '') else ''}</p>"

    content += f"<br>"

    # subject
    content += "<p><b>🔍 이수 과목</b></p>"
    content += f"<p>{data.get('subject_name', '') if data.get('subject_name', '') else ''}</p>"
    content += f"<br>"

    return content

def isNaN(num):
    return num != num

def display_store_info(data):
    
    # 관련자격 (링크 추가)
    certificates = data.get('certificates', '').split(', ') if not isNaN(data.get('certificates', '')) else ''

    linked_certificates = []
    # certificate = None
    for certificate in certificates:
        # 괄호로 URL을 분리
        if 'https' in certificate:
            print(certificate)
            certificate = certificate.split('(https') 
            name = certificate[0]
            url = certificate[1]
            url = url.replace(")", "").strip()
            url = 'https'+url
            linked_certificates.append(f"<a href='{url}' target='_blank' style='text-decoration: none; color: #007bff;'>{name.strip()}</a>")
        else:
            linked_institute.append(certificate.strip())
    institutes = data.get('job_rel_orgs', '').split(', ') if not isNaN(data.get('job_rel_orgs', '')) else ''
    linked_institute = []
    # institute = None
    for institute in institutes:
        # 괄호로 URL을 분리
        if 'https' in institute:
            # print('뭐길래',institute)
            institute = institute.split('(https')
            name = institute[0]
            url = institute[1]
            url = url.replace(")", "").strip()
            url = 'https'+url
            linked_institute.append(f"<a href='{url}' target='_blank' style='text-decoration: none; color: #007bff;'>{name.strip()}</a>")
        else:
            linked_institute.append(institute.strip())

    content = "<div style='font-family: sans-serif; padding: 10px;'>"

    # 직업명
    content += "<p><b>🔍 직업명</b></p>"
    content += f"<p>{data.get('name', '')}</p>"
    
    content += f"<br>"

    # 관련직업명
    content += "<p><b>🔍 관련직업명</b></p>"
    content += f"<p>{data.get('rel_job_nm', ''), data.get('std_job_nm', '')}</p>"
    
    content += f"<br>"

    # 핵심능력
    content += "<p><b>🔑 핵심능력</b></p>"
    content += f"<p>{data.get('ability', '')}</p>"

    content += f"<br>"

    # 적성 및 흥미
    content += "<p><b>💡 적성 및 흥미</b></p>"
    content += f"<p><b>적성:</b> {data.get('aptit_name', '') if data.get('aptit_name', '') else ''}</p>"
    content += f"<p><b>흥미:</b> {data.get('interest', '')if data.get('interest', '') else ''}</p>"

    content += f"<br>"

    # 관련직업명
    content += "<p><b>🔍 예상 전망</b></p>"
    content += f"<p>{data.get('forecast', '')}</p>"
    content += f"<br>"
    # 관련학과 및 관련자격
    content += "<p><b>🎓 관련교육 및 관련자격</b></p>"
    content += "<p><b>관련커리큘럼:</b> " + ", ".join(data.get('curriculum', '').split(', ')) + "</p>"
    content += "<p><b>관련자격:</b> " + ", ".join(linked_certificates) + "</p>"
    content += f"<br>"
    # 관련직업명
    content += "<p><b>📋 관련 기관</b></p>"
    content += f"<p>" + ", ".join(linked_institute) + "</p>"
    content += f"<br>"
    # 핵심 능력 비중
    indicators = data.get("indicators", "").split(", ")
    indicator_data = [float(x) for x in data.get("indicator_data", "").split(", ")]
    print('indicator_data:', indicator_data)
    # content = "<div style='font-family: sans-serif; padding: 10px;'>"
    content += "<p><b>📊 국내 직업 지표</b></p>"

    # 각 인디케이터를 막대그래프로 표시
    for i, (indicator, value) in enumerate(zip(indicators, indicator_data)):
        content += f"""
        <div style="margin-bottom: 8px;">
            <span style="display: inline-block; width: 150px; font-weight: bold;">{indicator}</span>
            <div style="display: inline-block; background-color: #f0f0f0; border-radius: 5px; width: 60%; height: 20px; vertical-align: middle;">
                <div style="width: {value}%; background-color: #4CAF50; height: 100%; border-radius: 5px;"></div>
            </div>
            <span style="margin-left: 10px;">{value}%</span>
        </div>
        """
    
    content += "</div>"


    content += "</div>"
    return content


def url_setting_major(data):
    content = display_store_info_major(data)
    
    # 최종 HTML을 Markdown에 적용
    info_box = f"""
        <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:0px;">
            <div style="font-size: 1.2em; font-weight: bold;">🍊 {data.get('major', '학과 정보')} 정보</div>
            <div style="padding-top: 10px;">
                {content}
            </div>
        </div>
    """

    return info_box


def url_setting_career(data):
    content = display_store_info(data)
    
    # 최종 HTML을 Markdown에 적용
    info_box = f"""
        <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:0px;">
            <div style="font-size: 1.2em; font-weight: bold;">🍊 {data.get('major', '학과 정보')} 정보</div>
            <div style="padding-top: 10px;">
                {content}
            </div>
        </div>
    """
    # info_box = f"""
    #     <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:0px;">
    #         <details>
    #             <summary style="cursor: pointer; font-size: 1.2em; font-weight: bold;">{data.get('name', '직업 정보')} 정보</summary>
    #             <div style="padding-top: 10px;">
    #                 {content}
    #             </div>
    #         </details>
    #     </div>
    # """
    return info_box


def json_format(response):
    response = response.replace("json", '')
    response = response.replace("```", '').strip()
    response = ast.literal_eval(response)
    return response
# 로그 설정 
logger = get_logger()
from clients import get_vectordb
vdb = get_vectordb()
c_vectorstore = vdb.c_hugging_vectorstore
c_retriever = c_vectorstore.as_retriever(search_kwargs={"k": 10})

m_vectorstore = vdb.m_hugging_vectorstore
m_retriever = m_vectorstore.as_retriever(search_kwargs={"k": 10})

# Show title and description.
st.logo(logo := "media/Img_Logo.png")
st.set_page_config(page_title="마폴챗", page_icon=logo)

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

# 세션 관리 (API 키, 쿼리 파라미터 등)
ss = st.session_state
if "chat_state" not in ss:
    # Run just once
    prepare_app()
    # Need to reference is_env_loaded to avoid unused import being removed
    is_env_loaded = True  # more info at the end of docdocgo.py

chat_state: ChatState = ss.chat_state

def open_ai_chat(parsed_query=None, eng_flag=False, message=None, docs = None):
    if "messages" not in ss:
        ss.messages = []

    # 메시지 표시를 여기에서 제거했습니다.

    # if message is None:
    #     if eng_flag == True:
    #         temp_prompt = st.chat_input("How can I assist you?")
    #     else:
    #         temp_prompt = st.chat_input("무엇을 도와드릴까요?")
    #     if prompt := temp_prompt:
    #         message = prompt
    if docs:
        chat_state.docs = docs
    if message:
        ss.messages.append({"role": "user", "content": message, "avatar": "🧑‍💻"})
        parsed_query.message = message
        chat_state.update(parsed_query=parsed_query)
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
        print('여기까진 옴', cb)
        response = get_bot_response(chat_state)
        print('여기까지도 옴', type(response))
        answer = response


        # Display the "complete" status - custom or default
        if status:
            default_status = status_config.get(chat_mode, just_chat_status_config)
            status.update(
                label=response.get("status.header", default_status["complete.header"]),
                state="complete",
            )
            status.write(response.get("status.body", default_status["complete.body"]))

        # Add the response to the chat history
        chat_state.chat_history.append((message, answer))


        # 메시지 표시를 여기에서 제거했습니다.
        return answer
def display_messages():
    print('랄랄라')
    if "messages" not in ss:
        ss.messages = []
    for message_dict in ss.messages:
        
        with st.chat_message(message_dict["role"], avatar=message_dict.get("avatar", "")):
            st.markdown(message_dict["content"])

def main():
    if tmp := os.getenv("STREAMLIT_WARNING_NOTIFICATION"):
        st.warning(tmp)    

    # 세션 상태에 페이지 상태 초기화
    if 'stage' not in ss:
        ss.stage = None

    if 'status' not in ss:
        ss.status = None
    
    parsed_query = parse_query("")

    # 메인 앱 페이지
    title_header(logo, "")
    st.title("Myfolio의 AI 봇과 함께하는 진로/진학 상담 서비스입니다.")
    # Korean content here
    st.markdown(GREETING_MESSAGE_KOR)
    
    # 날씨, 시간에 따른 인사말을 세션 상태에 저장
    if 'greeting_message' not in ss:
        parsed_query.chat_mode = ChatMode.JUST_CHAT_GREETING_ID
        # chat_state.flag = ""
        chat_state.update(parsed_query=parsed_query)
        ss.greeting_message = get_bot_response(chat_state)
    # 사용자 ID에 따른 전체 메시지 생성 
    if chat_state.user_id is not None:
        full_message = f"{chat_state.user_id}님 {ss.greeting_message}"
    else: 
        full_message = ss.greeting_message
        st.markdown(format_robot_response(full_message), unsafe_allow_html=True)
    
    # 채팅 히스토리에 메시지 추가 (필요한 경우)
    if 'messages' not in ss:
        ss.messages = []
    
    # if not ss.messages:
    #     ss.messages.append({"role": "assistant", "content": full_message, "avatar": "🦖"})
    
    # 메시지를 먼저 표시합니다.
    display_messages()

    # 대화 흐름 관리
    if ss.stage is None:
        print('stage: None', ss.messages)
        message = '어떤 고민이 있으신가요? 아래 버튼을 선택해주세요'
        # if not any(msg["content"] == message for msg in ss.messages):
        ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
            # 메시지를 다시 표시합니다.
        with st.chat_message('assistant'):
            print('with', message)
            st.write(message)
        # col1= st.columns(1)
        # with col1:
        career_button = st.button('진로 상담하기')
        # with col2:
        #     st.markdown("""
        #     <style>
        #         진학 상담 업데이트 예정
        #     </style>
        #     """, unsafe_allow_html=True)
        if career_button:
            ss.messages.pop()
            ss.stage = 'career_ask_desired_job'
            ss.messages.append({"role": "user", "content": "진로 선택", "avatar": "🧑‍💻"})
            st.rerun()
        # elif school_button:
        #     ss.messages.pop()
        #     ss.stage = 'academic_ask_desired_major'
        #     ss.messages.append({"role": "user", "content": "진학 선택", "avatar": "🧑‍💻"})
        #     st.rerun()

    elif ss.stage == 'career_ask_desired_job':
        print('stage: career_ask_desired_job')
        message = '희망하는 직업이 있나요?'
        # if not any(msg["content"] == message for msg in ss.messages):
        # print('메세지 나옴 career_ask_desired_job')
        ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
        print('여기보셈 1-------', ss.messages)
        with st.chat_message('assistant'):
        #     print('메세지 나옴 career_ask_desired_job2')
            st.write(message)
        col1, col2 = st.columns(2)
        with col1:
            yes_button = st.button('예')
        with col2:
            no_button = st.button('아니오')
        if yes_button:
            
            ss.messages.pop()
            print('여기보셈 2-------', ss.messages)
            ss.stage = 'career_get_desired_job'
            ss.messages.append({"role": "user", "content": "예", "avatar": "🧑‍💻"})
            print('여기보셈 3-------', ss.messages)
            st.rerun()
        elif no_button:
            ss.messages.pop()
            ss.stage = 'career_no_options'
            ss.messages.append({"role": "user", "content": "아니오", "avatar": "🧑‍💻"})
            st.rerun()

    elif ss.stage == 'career_get_desired_job':
        print('stage: career_get_desired_job')
        message = '희망하는 직업을 작성해주세요'
        if not any(msg["content"] == message for msg in ss.messages):
        # print('메세지 나옴 get_desired_job')
            ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
            with st.chat_message('assistant'):
            #     print('메세지 나옴 get_desired_job2')
                st.write(message)        
        desired_job = st.text_input('희망하는 직업')
        if desired_job:
            if not any(msg["content"] == desired_job for msg in ss.messages):
                ss.messages.append({"role": "user", "content": desired_job, "avatar": "🧑‍💻"})
            parsed_query.message = desired_job
            parsed_query.chat_mode = ChatMode.CAREER_CHAT_COMMAND_ID
            chat_state.update(parsed_query=parsed_query)
            print('여기닷')
            result = open_ai_chat(parsed_query=parsed_query, message=desired_job)
            result = json_format(result)
            print('들어간다1')
            if result['type'] == 'yeild':
                ss.messages.pop()
                print('들어감1')
                ss.messages.append({"role": "assistant", "content": result['response'], "avatar": "🦖"})
                    # 메시지를 다시 표시합니다.
                with st.chat_message('assistant'):
                    st.write(result['response'])
                desired_job = None
                ss.stage = 'career_ask_desired_job'
                # ss.stage = None
                st.rerun()
            elif result['type'] == 'SUCCESS' or result['type'] == 'FAILED':
                ss.messages.pop()
                print('들어감2')
                message = f"{result['response']}와 비슷한 직업을 찾았습니다. 아래 중에서 골라주세요."
                # if not any(msg["content"] == result['response'] for msg in ss.messages):
                ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
                print('\n\n\n\n메세지 차이 보기', ss.messages)
                with st.chat_message('assistant'):
                    st.write(message)

                ret_result = c_retriever.invoke(result['response'])
                print('keys~:',ret_result[0].metadata.keys() )
                print('ret_result:', ret_result)
                col1, col2, col3,col4, col5 = st.columns(5)
                # ss.messages.append(ret_result)
                with col1:
                    bttn1 = st.button(ret_result[0].metadata['name'])
                    # ss.messages.pop()
                with col2:
                    bttn2 = st.button(ret_result[1].metadata['name'])
                with col3:
                    bttn3 = st.button(ret_result[2].metadata['name'])
                with col4:
                    bttn4 = st.button(ret_result[3].metadata['name'])
                with col5:
                    bttn5 = st.button(ret_result[4].metadata['name'])
                # 각 버튼의 동작을 정의
                if bttn1:
                    ss.messages.pop()
                    ss.stage = 'research'
                    ss.messages.append({"role": "user", "content": ret_result[0].metadata['name'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[0].metadata
                    st.rerun()
                elif bttn2:
                    ss.messages.pop()
                    ss.stage = 'research'
                    ss.messages.append({"role": "user", "content": ret_result[1].metadata['name'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[1].metadata
                    st.rerun()
                elif bttn3:
                    ss.messages.pop()
                    ss.stage = 'research'
                    ss.messages.append({"role": "user", "content": ret_result[2].metadata['name'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[2].metadata
                    st.rerun()
                elif bttn4:
                    ss.messages.pop()
                    ss.stage = 'research'
                    ss.messages.append({"role": "user", "content": ret_result[3].metadata['name'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[3].metadata
                    st.rerun()
                elif bttn5:
                    ss.messages.pop()
                    ss.stage = 'research'
                    ss.messages.append({"role": "user", "content": ret_result[4].metadata['name'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[4].metadata
                    st.rerun()

    elif ss.stage == "research":
        print('보쇼', ss.status)
        info_box = url_setting_career(ss.status)
        st.markdown(info_box, unsafe_allow_html=True)
        desired_job = None
        ss.stage = None
        ss.messages = []
        st.button('다시하기')

    elif ss.stage == 'career_no_options':
        print('stage: career_ask_desired_job')
        message = '그렇다면, 원하는 학과는 있나요?'
        ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"}) 
        with st.chat_message('assistant'):
            st.write(message)
        col1, col2 = st.columns(2)
        with col1:
            yes_button = st.button('예')
        with col2:
            no_button = st.button('아니오')
        if yes_button:
            ss.messages.pop()
            print('여기보셈 2-------', ss.messages)
            ss.stage = 'major_get_desired_job'
            ss.messages.append({"role": "user", "content": "예", "avatar": "🧑‍💻"})
            print('여기보셈 3-------', ss.messages)
            st.rerun()
        elif no_button:
            ss.messages.pop()
            ss.stage = 'major_no_options'
            ss.messages.append({"role": "user", "content": "아니오", "avatar": "🧑‍💻"})
            st.rerun()
    elif ss.stage == "major_get_desired_job":
        message = '희망하는 전공을 작성해주세요'
        if not any(msg["content"] == message for msg in ss.messages):
            ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
            with st.chat_message('assistant'):
                st.write(message)        
        desired_major = st.text_input('희망하는 전공')
        if desired_major:
            if not any(msg["content"] == desired_major for msg in ss.messages):
                ss.messages.append({"role": "user", "content": desired_major, "avatar": "🧑‍💻"})
            parsed_query.message = desired_major
            parsed_query.chat_mode = ChatMode.SCHOOL_CHAT_COMMAND_ID
            chat_state.update(parsed_query=parsed_query)
            print('여기닷')
            result = open_ai_chat(parsed_query=parsed_query, message=desired_major)
            result = json_format(result)
            print('들어간다1')
            if result['type'] == 'yeild':
                ss.messages.pop()
                print('들어감1')
                ss.messages.append({"role": "assistant", "content": result['response'], "avatar": "🦖"})
                    # 메시지를 다시 표시합니다.
                with st.chat_message('assistant'):
                    st.write(result['response'])
                desired_major = None
                ss.stage = 'career_no_options'
                # ss.stage = None
                st.rerun()
            elif result['type'] == 'SUCCESS' or result['type'] == 'FAILED':
                ss.messages.pop()
                print('들어감2')
                message = f"{result['response']}와 관련된 전공을 찾았습니다. 아래 중에서 골라주세요."
                # if not any(msg["content"] == result['response'] for msg in ss.messages):
                ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
                print('\n\n\n\n메세지 차이 보기', ss.messages)
                with st.chat_message('assistant'):
                    st.write(message)

                ret_result = m_retriever.invoke(result['response'])
                print('keys~:',ret_result[0].metadata.keys() )
                print('ret_result:', ret_result)
                col1, col2, col3,col4, col5 = st.columns(5)
                # ss.messages.append(ret_result)
                with col1:
                    bttn1 = st.button(ret_result[0].metadata['major'])
                    # ss.messages.pop()
                with col2:
                    bttn2 = st.button(ret_result[1].metadata['major'])
                with col3:
                    bttn3 = st.button(ret_result[2].metadata['major'])
                with col4:
                    bttn4 = st.button(ret_result[3].metadata['major'])
                with col5:
                    bttn5 = st.button(ret_result[4].metadata['major'])
                # 각 버튼의 동작을 정의
                if bttn1:
                    ss.messages.pop()
                    ss.stage = 'research_major'
                    ss.messages.append({"role": "user", "content": ret_result[0].metadata['major'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[0].metadata
                    st.rerun()
                elif bttn2:
                    ss.messages.pop()
                    ss.stage = 'research_major'
                    ss.messages.append({"role": "user", "content": ret_result[1].metadata['major'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[1].metadata
                    st.rerun()
                elif bttn3:
                    ss.messages.pop()
                    ss.stage = 'research_major'
                    ss.messages.append({"role": "user", "content": ret_result[2].metadata['major'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[2].metadata
                    st.rerun()
                elif bttn4:
                    ss.messages.pop()
                    ss.stage = 'research_major'
                    ss.messages.append({"role": "user", "content": ret_result[3].metadata['major'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[3].metadata
                    st.rerun()
                elif bttn5:
                    ss.messages.pop()
                    ss.stage = 'research_major'
                    ss.messages.append({"role": "user", "content": ret_result[4].metadata['major'], "avatar": "🧑‍💻"})
                    ss.status = ret_result[4].metadata
                    st.rerun()
    elif ss.stage == "research_major":
        print('보쇼', ss.status)
        info_box = url_setting_major(ss.status)
        st.markdown(info_box, unsafe_allow_html=True)
        desired_job = None
        ss.stage = None
        ss.messages = []
        st.button('다시하기')
    elif ss.stage == "major_no_options":
        message = '어떤 것이든 평소 좋아하거나, 관심있는 것을 검색해주세요! 그에 적합한 전공을 추천해드릴게요!'
        if not any(msg["content"] == message for msg in ss.messages):
            ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
            with st.chat_message('assistant'):
                st.write(message)        
        desired_interest = st.text_input('관심사 입력하기')
        if desired_interest:
            if not any(msg["content"] == desired_interest for msg in ss.messages):
                ss.messages.append({"role": "user", "content": desired_interest, "avatar": "🧑‍💻"})
            parsed_query.message = desired_interest
            parsed_query.chat_mode = ChatMode.MAJOR_CHAT_COMMAND_ID
            chat_state.update(parsed_query=parsed_query)
            print('여기닷')
            result = open_ai_chat(parsed_query=parsed_query, message=desired_interest)
            result = json_format(result)
            print('들어간다1')
            if result['type'] == 'yeild':
                ss.messages.pop()
                print('들어감1')
                ss.messages.append({"role": "assistant", "content": result['response'], "avatar": "🦖"})
                    # 메시지를 다시 표시합니다.
                with st.chat_message('assistant'):
                    st.write(result['response'])
                desired_interest = None
                ss.stage = 'major_no_options'
                ss.stage = None
                st.rerun()
            elif result['type'] == 'SUCCESS' or result['type'] == 'FAILED':
                
                ret_result = m_retriever.invoke(result['keyword'])
                print(f'\n\n\n\n\n\n{ret_result}\n\n\n\n\n\n\n')
                parsed_query.message = desired_interest
                parsed_query.chat_mode = ChatMode.RESPONSE_CHAT_COMMAND_ID
                chat_state.update(parsed_query=parsed_query)
                result = open_ai_chat(parsed_query=parsed_query, message=desired_interest, docs = ret_result[:3])
                print(result)

                res_box = f"""
                    <div style="border:1px solid #ddd; border-radius:5px; padding:10px; margin-bottom:0px;">
                        <div style="font-size: 1.2em; font-weight: bold;"> 추천 학과 정보 </div>
                        <div style="padding-top: 10px;">
                            {result}
                        </div>
                    </div>
                """
                st.markdown(res_box, unsafe_allow_html=True)
                for num in range(3):
                    info_box = url_setting_major(ret_result[num].metadata)
                    st.markdown(info_box, unsafe_allow_html=True)
                desired_interest = None
                ss.stage = None
                ss.messages = []
                st.button('다시하기')
                # ss.messages.pop()
                # print('들어감2')
                # message = f"{result['response']}와 관련된 전공을 찾았습니다. 아래 중에서 골라주세요."
                # # if not any(msg["content"] == result['response'] for msg in ss.messages):
                # ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
                # print('\n\n\n\n메세지 차이 보기', ss.messages)
                # with st.chat_message('assistant'):
                #     st.write(message)

                # ret_result = m_retriever.invoke(result['response'])
                # print('keys~:',ret_result[0].metadata.keys() )
                # print('ret_result:', ret_result)
                # col1, col2, col3,col4, col5 = st.columns(5)
                # # ss.messages.append(ret_result)
                # with col1:
                #     bttn1 = st.button(ret_result[0].metadata['major'])
                #     # ss.messages.pop()
                # with col2:
                #     bttn2 = st.button(ret_result[1].metadata['major'])
                # with col3:
                #     bttn3 = st.button(ret_result[2].metadata['major'])
                # with col4:
                #     bttn4 = st.button(ret_result[3].metadata['major'])
                # with col5:
                #     bttn5 = st.button(ret_result[4].metadata['major'])
                # # 각 버튼의 동작을 정의
                # if bttn1:
                #     ss.messages.pop()
                #     ss.stage = 'research_major'
                #     ss.messages.append({"role": "user", "content": ret_result[0].metadata['major'], "avatar": "🧑‍💻"})
                #     ss.status = ret_result[0].metadata
                #     st.rerun()
                # elif bttn2:
                #     ss.messages.pop()
                #     ss.stage = 'research_major'
                #     ss.messages.append({"role": "user", "content": ret_result[1].metadata['major'], "avatar": "🧑‍💻"})
                #     ss.status = ret_result[1].metadata
                #     st.rerun()
                # elif bttn3:
                #     ss.messages.pop()
                #     ss.stage = 'research_major'
                #     ss.messages.append({"role": "user", "content": ret_result[2].metadata['major'], "avatar": "🧑‍💻"})
                #     ss.status = ret_result[2].metadata
                #     st.rerun()
                # elif bttn4:
                #     ss.messages.pop()
                #     ss.stage = 'research_major'
                #     ss.messages.append({"role": "user", "content": ret_result[3].metadata['major'], "avatar": "🧑‍💻"})
                #     ss.status = ret_result[3].metadata
                #     st.rerun()
                # elif bttn5:
                #     ss.messages.pop()
                #     ss.stage = 'research_major'
                #     ss.messages.append({"role": "user", "content": ret_result[4].metadata['major'], "avatar": "🧑‍💻"})
                #     ss.status = ret_result[4].metadata
                #     st.rerun()

        # message = '어떤 내용으로 진로 상담을 진행할까요? 하나를 선택해주세요'
        # if not any(msg["content"] == message for msg in ss.messages):
        #     print('메세지뜸')
        #     ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
        # with st.chat_message('assistant'):
        #     st.write(message)            
        # col1, col2, col3 = st.columns(3)
        # with col1:
        #     strength_button = st.button('강점')
        # with col2:
        #     interest_button = st.button('관심 지식')
        # with col3:
        #     work_env_button = st.button('업무 환경')
        # if strength_button:
        #     ss.messages.append({"role": "user", "content": "강점", "avatar": "🧑‍💻"})
        #     parsed_query.message = '강점'
        #     parsed_query.chat_mode = ChatMode.CAREER_CHAT_COMMAND_ID
        #     chat_state.update(parsed_query=parsed_query)
        #     open_ai_chat(parsed_query=parsed_query, message='강점')
        #     # ss.stage = None
        #     st.rerun()
    #     elif interest_button:
    #         ss.messages.append({"role": "user", "content": "관심 지식", "avatar": "🧑‍💻"})
    #         parsed_query.message = '관심 지식'
    #         parsed_query.chat_mode = ChatMode.CAREER_CHAT_COMMAND_ID
    #         chat_state.update(parsed_query=parsed_query)
    #         open_ai_chat(parsed_query=parsed_query, message='관심 지식')
    #         ss.stage = None
    #         st.rerun()
    #     elif work_env_button:
    #         ss.messages.append({"role": "user", "content": "업무 환경", "avatar": "🧑‍💻"})
    #         parsed_query.message = '업무 환경'
    #         parsed_query.chat_mode = ChatMode.CAREER_CHAT_COMMAND_ID
    #         chat_state.update(parsed_query=parsed_query)
    #         open_ai_chat(parsed_query=parsed_query, message='업무 환경')
    #         ss.stage = None
    #         st.rerun()

    # elif ss.stage == 'academic_ask_desired_major':
    #     message = '희망하는 학과, 전공이 있으신가요?'
    #     if not any(msg["content"] == message for msg in ss.messages):
    #         ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
    #     with st.chat_message('assistant'):
    #         st.write(message)            
    #     col1, col2 = st.columns(2)
    #     with col1:
    #         yes_button = st.button('예')
    #     with col2:
    #         no_button = st.button('아니오')
    #     if yes_button:
    #         ss.stage = 'academic_get_desired_major'
    #         ss.messages.append({"role": "user", "content": "예", "avatar": "🧑‍💻"})
    #         st.rerun()
    #     elif no_button:
    #         ss.stage = 'academic_no_options'
    #         ss.messages.append({"role": "user", "content": "아니오", "avatar": "🧑‍💻"})
    #         st.rerun()

    # elif ss.stage == 'academic_get_desired_major':
    #     message = '희망하는 학과를 입력해주세요'
    #     if not any(msg["content"] == message for msg in ss.messages):
    #         ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
    #     with st.chat_message('assistant'):
    #         st.write(message)            
    #     desired_major = st.text_input('희망하는 학과')
    #     if desired_major:
    #         ss.messages.append({"role": "user", "content": desired_major, "avatar": "🧑‍💻"})
    #         parsed_query.message = desired_major
    #         parsed_query.chat_mode = ChatMode.SCHOOL_CHAT_COMMAND_ID
    #         chat_state.update(parsed_query=parsed_query)
    #         open_ai_chat(parsed_query=parsed_query, message=desired_major)
    #         ss.stage = None
    #         st.rerun()

    # elif ss.stage == 'academic_no_options':
    #     message = '어떤 내용으로 진학 상담을 진행할까요? 하나를 선택해주세요'
    #     if not any(msg["content"] == message for msg in ss.messages):
    #         ss.messages.append({"role": "assistant", "content": message, "avatar": "🦖"})
            
    #     col1, col2, col3 = st.columns(3)
    #     with col1:
    #         grades_button = st.button('성적')
    #     with col2:
    #         major_selection_button = st.button('전공 선택')
    #     with col3:
    #         university_selection_button = st.button('대학 선택')
    #     if grades_button:
    #         ss.messages.append({"role": "user", "content": "성적", "avatar": "🧑‍💻"})
    #         parsed_query.message = '성적'
    #         parsed_query.chat_mode = ChatMode.SCHOOL_CHAT_COMMAND_ID
    #         chat_state.update(parsed_query=parsed_query)
    #         open_ai_chat(parsed_query=parsed_query, message='성적')
    #         ss.stage = None
    #         st.rerun()
    #     elif major_selection_button:
    #         ss.messages.append({"role": "user", "content": "전공 선택", "avatar": "🧑‍💻"})
    #         parsed_query.message = '전공 선택'
    #         parsed_query.chat_mode = ChatMode.SCHOOL_CHAT_COMMAND_ID
    #         chat_state.update(parsed_query=parsed_query)
    #         open_ai_chat(parsed_query=parsed_query, message='전공 선택')
    #         ss.stage = None
    #         st.rerun()
    #     elif university_selection_button:
    #         ss.messages.append({"role": "user", "content": "대학 선택", "avatar": "🧑‍💻"})
    #         parsed_query.message = '대학 선택'
    #         parsed_query.chat_mode = ChatMode.SCHOOL_CHAT_COMMAND_ID
    #         chat_state.update(parsed_query=parsed_query)
    #         open_ai_chat(parsed_query=parsed_query, message='대학 선택')
    #         ss.stage = None
    #         st.rerun()

    # 항상 메시지 입력창 제공
    print('여기도!!')
    # open_ai_chat(parsed_query=parsed_query)

def title_header(logo, title):
    # 이미지와 제목을 포함한 컨테이너 생성
    header = st.container()

    with header:
        # 두 열로 나누기
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # 첫 번째 열에 로고 이미지 표시
            st.image(logo, width=200)  # 너비를 조절하여 크기 조정
        
        with col2:
            # 두 번째 열에 제목 텍스트 표시
            st.markdown(f"# {title}")  # 큰 글씨로 제목 표시

def format_robot_response(message):
    return f'''<div style="background-color: #f0f0f0; padding: 15px; border-radius: 8px; border: 1px solid #ffb74d; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #e65100; box-shadow: 0 4px 8px rgba(0,0,0,0.1); font-size: 16px;">
        <strong>🍊:</strong> {message} </div>'''

if __name__ == '__main__':
    main()  
