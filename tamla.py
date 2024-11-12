import os
from typing import Any

from langchain.chains import LLMChain
from utils.prepare import DEFAULT_OPENAI_API_KEY, WEATHER_KEY, get_logger
from utils.chat_state import ChatState
from utils.type_utils import OperationMode
from utils.prompts import ( 
    JUST_CHAT_PROMPT, CAREER_CHAT_PROMPT, SCHOOL_CHAT_PROMPT
)
from components.llm import get_prompt_llm_chain
from utils.lang_utils import pairwise_chat_history_to_msg_list
from agents.greeting_quick import get_greeting_chat_chain
from utils.type_utils import ChatMode
import json
logger = get_logger()

default_vectorstore = None  # can move to chat_state

import ast

def json_format(response):
    response = response.replace("json", '')
    response = response.replace("```", '').strip()
    response = ast.literal_eval(response)
    return response
def get_bot_response(
    chat_state: ChatState,
):  
    chat_mode_val = (
        chat_state.chat_mode.value
    )
    print(dir(chat_state))
    print('챗모드', chat_mode_val)
    answer = None
    if chat_mode_val == ChatMode.JUST_CHAT_COMMAND_ID.value:
        chat_chain = get_prompt_llm_chain(
            JUST_CHAT_PROMPT,
            llm_settings=chat_state.bot_settings,
            api_key=chat_state.google_api_key,
            callbacks=chat_state.callbacks,
            stream=True,
        )
        answer = chat_chain.invoke(
            {   
                "message": chat_state.message,
                "chat_history": pairwise_chat_history_to_msg_list(
                    chat_state.chat_history
                ),
            }
        )
        print('일반대화모드', answer)
    elif chat_mode_val == ChatMode.CAREER_CHAT_COMMAND_ID.value:
        # CAREER_CHAT_PROMPT를 사용하여 LLM에 요청
        chat_chain = get_prompt_llm_chain(
            CAREER_CHAT_PROMPT,
            llm_settings=chat_state.bot_settings,
            api_key=chat_state.google_api_key,
            callbacks=chat_state.callbacks,
            stream=True,
        )
        print('문제:', chat_state.message)
        print('히스토리:', chat_state.chat_history)
        answer = chat_chain.invoke(
            {   
                "message": chat_state.message,
                "chat_history": pairwise_chat_history_to_msg_list(
                    chat_state.chat_history
                ),
            }
        )
        print('진로모드', answer)
    elif chat_mode_val == ChatMode.SCHOOL_CHAT_COMMAND_ID.value:
        # SCHOOL_CHAT_PROMPT를 사용하여 LLM에 요청
        chat_chain = get_prompt_llm_chain(
            SCHOOL_CHAT_PROMPT,
            llm_settings=chat_state.bot_settings,
            api_key=chat_state.google_api_key,
            callbacks=chat_state.callbacks,
            stream=True,
        )
        answer = chat_chain.invoke(
            {   
                "message": chat_state.message,
                "chat_history": pairwise_chat_history_to_msg_list(
                    chat_state.chat_history
                ),
            }
        )
        print('진학모드', answer)
    elif chat_mode_val == ChatMode.JUST_CHAT_GREETING_ID.value:
        print('인사모드', answer)
        return get_greeting_chat_chain(chat_state)
    else:
        # Should never happen
        raise ValueError(f"Invalid chat mode: {chat_state.chat_mode}")
    print('여기 지나감')
    

    return answer


if __name__ == "__main__":
    chat_history = []

    response = get_bot_response(
        ChatState(
            operation_mode=OperationMode.CONSOLE,
            chat_history=chat_history,
            google_api_key=GOOGLE_API_KEY,
            user_id=None,  # would be set to None by default but just to be explicit
        )
    )
