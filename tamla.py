import os
from typing import Any

from langchain.chains import LLMChain
from utils.prepare import DEFAULT_OPENAI_API_KEY, WEATHER_KEY, get_logger
from utils.chat_state import ChatState
from utils.type_utils import OperationMode
from utils.prompts import ( 
    JUST_CHAT_PROMPT,CAREER_CHAT_PROMPT
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
    print('변수값', chat_mode_val)
    if chat_mode_val == ChatMode.JUST_CHAT_COMMAND_ID.value:
        chat_chain = get_prompt_llm_chain(
            JUST_CHAT_PROMPT,
            # chatstate,
            llm_settings=chat_state.bot_settings,
            api_key=chat_state.google_api_key,
            callbacks=chat_state.callbacks,
            stream=True,
        )
        print('\n\n\n\n여기:', chat_state.selected_career_groups,chat_state.user_type, '\n\n\n')
        answer = chat_chain.invoke(
            {   "user_career": chat_state.selected_career_groups,
                "user_type": chat_state.user_type,
                "message": chat_state.message,
                "chat_history": pairwise_chat_history_to_msg_list(
                    chat_state.chat_history
                ),
            }
        )
    elif chat_mode_val == ChatMode.CAREER_CHAT_COMMAND_ID.value:
        
        chat_chain = get_prompt_llm_chain(
            CAREER_CHAT_PROMPT,
            # chatstate,
            llm_settings=chat_state.bot_settings,
            api_key=chat_state.google_api_key,
            callbacks=chat_state.callbacks,
            stream=True,
        )
        print('\n\n\n\n여기?:', chat_state.selected_career_groups,chat_state.user_type, '\n\n\n')
        answer = chat_chain.invoke(
            {   "question": chat_state.parsed_query,
                "message": chat_state.message,
                "chat_history": pairwise_chat_history_to_msg_list(
                    chat_state.chat_history
                ),
            }
        )
        print('답변', answer)
        # # data_str = answer.replace("'", '"')
        # answer = json_format(answer)
 
        # return {"answer": answer['response'], 'task_type': 'Self-exploration and Aptitude', 'response_type': 'Promote Self-Understanding'}
        return answer
    elif chat_mode_val == ChatMode.JUST_CHAT_GREETING_ID.value:
        return get_greeting_chat_chain(chat_state)
    else:
        # Should never happen
        raise ValueError(f"Invalid chat mode: {chat_state.chat_mode}")


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
