
from utils.type_utils import BotSettings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate

REPORT_ASSESSMENT_INSTRUCTION = """\
"REPORT ASSESSMENT: X%", where X is your estimate of how well the query was answered on a scale from 0% to 100%. 
"""

REPORT_ASSESSMENT_INSTRUCTION = """\
"---
REPORT ASSESSMENT: <biggest constructive criticism some hypothetical person making the above query might have for the report, assuming they are difficult to please (AVOID any praise, write ONLY what can be improved, be brief)> <percentage grade they might assign>%"
"""

REPORT_INSTRUCTION = (
    """\
1. Focus on addressing the specific query.
2. Avoid fluff and irrelevant information.
3. Provide available facts, figures, examples, details, dates, locations, etc.
4. If not enough information is available, be honest about it.

The report type should be: {report_type}

Format nicely in Markdown, starting with a title. 

Finish with: \
"""
    + REPORT_ASSESSMENT_INSTRUCTION
)

# TODO rethink the following prompt
condense_question_template = """Given the following chat history (between Human and you, the Assistant) add context to the last Query from Human so that it can be understood without needing to read the whole conversation: include necessary details from the conversation to make Query completely standalone:
1. First put the original Query as is or very slightly modified (e.g. replacing "she" with who this refers to) 
2. Then, add "[For context: <condensed summary to yourself of the relevant parts of the chat history: if Human asks a question and the answer is clear from the chat history, include it in the summary>]"

Examples of possible Standalone Queries:
- "And then? [For context: Human wrote this in response to your summary of the Big Bang. The general conversation was about the history of the universe.]"
- "How do you know this? [For context: you just summarized relevant parts of your knowledge base answering Human's question about installing Langchain. Briefly, you explained that they need to run "pip install langchain" and likely other libraries like openai, tiktoken, etc.]"
- "hm [For context: Human asked you to write a poem about Washington and you wrote one.]"
- "What was my first message to you? [For context: Human's first message in our chat history was <exact first message from Human in chat history, verbatim>.]

Chat History:
{chat_history}
Last Query from Human: {question}
Standalone version of Last Query: """
CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(condense_question_template)


# - Chat
#     * It applies to general conversation. and all other types of questions.
# - CAREER
#     * Content related to desired occupation - for cases where the user is curious about a specific job.
# - INDUSTRY
#     * Content related to desired career path (field) - for cases where the user is curious about an industry.

career_prompt = """
GOAL:
* You are a bot that analyzes the user’s response and takes appropriate action.
* The response must be about the desired occupation. If not, return "This is not an appropriate occupation, please enter again."
* Please provide the response in JSON format.        

EXAMPLES:

    USER's INPUT:
    안녕

    OUTPUT:
    {{'type':'FAILED','response':'적절한 직업이 아닙니다, 다시 입력해주세요'}}

    USER's INPUT:
    야 나는 장사꾼이야

    OUTPUT:
    {{'type':'FAILED','response':'적절한 직업이 아닙니다, 다시 입력해주세요'}}

    USER's INPUT:
    맛있는 직업 추천좀

    OUTPUT:
    {{'type':'FAILED','response':'적절한 직업이 아닙니다, 다시 입력해주세요'}}

    USER's INPUT:
    건축전문가

    OUTPUT:
    {{'type':'SUCCESS','response':'건축가'}}

    USER's INPUT:
    인테리어 디자이너

    OUTPUT:
    {{'type':'SUCCESS','response':'인테리어 디자이너'}}

    USER's INPUT:
    실내 쪽

    OUTPUT:
    {{'type':'SUCCESS','response':'인테리어'}}

    USER's INPUT:
    {message}

    OUTPUT:
    """


major_prompt = """
GOAL:
* You are a bot that analyzes the user’s response and takes appropriate action.
* The response must be about the desired major. If not, return "This is not an appropriate major or department, please enter again."
* Please provide the response in JSON format.        

EXAMPLES:

    USER's INPUT:
    안녕

    OUTPUT:
    {{'type':'FAILED','response':'적절한 전공이 아닙니다, 다시 입력해주세요'}}

    USER's INPUT:
    야 나는 장사꾼이야

    OUTPUT:
    {{'type':'FAILED','response':'적절한 전공이 아닙니다, 다시 입력해주세요'}}

    USER's INPUT:
    맛있는 직업 추천좀

    OUTPUT:
    {{'type':'FAILED','response':'적절한 전공이 아닙니다, 다시 입력해주세요'}}

    USER's INPUT:
    건축학과

    OUTPUT:
    {{'type':'SUCCESS','response':'건축학'}}

    USER's INPUT:
    인테리어 디자인

    OUTPUT:
    {{'type':'SUCCESS','response':'인테리어 디자인'}}

    USER's INPUT:
    실내 쪽

    OUTPUT:
    {{'type':'SUCCESS','response':'실내 디자인'}}

    USER's INPUT:
    경영

    OUTPUT:
    {{'type':'SUCCESS','response':'경영학'}}



    USER's INPUT:
    {message}

    OUTPUT:
    """

interest_major_prompt = """
GOAL:
* You are a bot that analyzes the user’s response and takes appropriate action.
* The response must be about the desired major. If not, return "This is not an appropriate major or department, please enter again."
* The expected User's INPUT is about what the User used to be interested in. if it's not about that, you may just return the not an appropriate major comment
* If it has 'SUCESS', extract the original expression what the User entered, then think and map it to related keyword in industry to get related majors.

* Please provide the response in JSON format.        

EXAMPLES:

    USER's INPUT:
    안녕

    OUTPUT:
    {{'type':'FAILED','response':'적절한 취미 또는 흥미 거리가 아닙니다.'}}

    USER's INPUT:
    야 나는 장사꾼이야

    OUTPUT:
    {{'type':'SUCCESS','original': '장사꾼', 'keyword':'장사, 영업'}}

    USER's INPUT:
    맛있는 직업 추천좀

    OUTPUT:
    {{'type':'SUCCESS','original': '맛있는 직업', 'keyword':'주방, 요리, 제빵'}}

    USER's INPUT:
    건축학과

    OUTPUT:
    {{'type':'SUCCESS','original': '건축학과', 'keyword':'건축'}}

    USER's INPUT:
    인테리어 디자인

    OUTPUT:
    {{'type':'SUCCESS','original': '인테리어 디자인', 'keyword':'인테리어, 디자인'}}

    USER's INPUT:
    실내 쪽

    OUTPUT:
    {{'type':'SUCCESS','original': '실내', 'keyword':'실내, 디자인'}}

    USER's INPUT:
    경영

    OUTPUT:
    {{'type':'SUCCESS','original': '경영', 'keyword':'경영, 운영, 인사'}}

    USER's INPUT:
    {message}

    OUTPUT:
    """

response_major_prompt = """
GOAL:
* You are a bot that making the answer as related major about entered user's interests.
* The situation is the user doesn't have any interested job or major. so you have to recommend the searched major information in 'CONTEXT'
* Refer to the following CONTEXT which is about the majors after search, and make the answer like you are recommending as a career teacher.

CONTEXT:
{context}

FORMAT:
* output must be in korean.
* the tone must be a career teacher.

USER's INPUT:
{message}

OUTPUT:
    """



sub_task_detection_prompt = """
GOAL:
* You are a bot which can route user's question for givining appropriate career or school solution
* Determine which of the following 3 types of responses is needed for the user's question:

RESPONSE TYPE:
- 

- Chat
    * It applies to general conversation. and all other types of questions.
    
PROCEDURE:

IMPORTANCE:
    * Do not make response with any kinds of emoji. just make only text and basic mark like .
        

EXAMPLES:
    
    USER's QUESTION:
    어떤게 적성에 맞는지 모르겠어

    OUTPUT:
    "{{'task_type':'Self-exploration and Aptitude',
    'response_type':'Promote Self-Understanding'
    'response':'어떤 활동을 할 때 시간이 가는 줄 모를 만큼 몰입하나요?'}}"

    USER's QUESTION:
    좋아하는 것과 잘하는 것이 다른데, 어떻게 결정해야 할까요?

    OUTPUT:
    "{{'task_type':'Self-exploration and Aptitude',
    'response_type':'Foster Flexible Thinking',
    'response':'좋아하는 것과 잘하는 것을 모두 고려해서 그 중간 지점을 찾아보는 건 어떨까요? 예를 들어, 좋아하는 분야에서 조금 더 잘할 수 있는 방법을 찾아보거나, 잘하는 일에 대해 더 깊이 흥미를 느낄 수 있는 길을 고민해보세요. 이를 통해 새로운 길을 찾을 수 있을 거예요.'}}"

    USER's QUESTION:
    AI나 IT 같은 분야에 관심이 있는데, 어떤 직업이 좋을까요?

    OUTPUT:
    "{{'task_type':'Job Exploration and Preparation',
    'response_type':'Recommend careers',
    'response':''}}"

    USER's QUESTION:
    AI나 IT 같은 분야에 관심이 있는데, 어떤 직업이 좋을까요?

    OUTPUT:
    "{{'task_type':'Job Exploration and Preparation',
    'response_type':'Recommend careers',
    'response':''}}"

    User's QUESTION:
    {question}
    
    OUTPUT:
    """

MAJOR_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", interest_major_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{message}"),
    ]
)

CAREER_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", career_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{message}"),
    ]
)
SCHOOL_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", major_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{message}"),
    ]
) 

RESPONSE_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", response_major_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{message}"),
    ]
) 
# career_chat_system_template = """
# You are Myfolio's counselling AI,
# a friendly Assistant AI who has been equipped with your own special knowledge base and the ability to do Internet research for the user.
# The users are usually related with highscool student's career and future education.
# You have to check the Query and make the right answers for the students, their parents or teachers
# Make sure to take into account that the user is a {user_type} when crafting your response.

# USER TYPE:
# {user_type}

# USERS INTERESTED CAREER:
# {user_career}

# OUTPUT PROCEDURE:
# Must mention the user's type if 'user_type' is not None.

# OUTPUT:
# """

# CAREER_CHAT_PROMPT = ChatPromptTemplate.from_messages(
#     [
#         ("system", sub_task_detection_prompt),
#         MessagesPlaceholder(variable_name="chat_history"),
#         ("user", "{message}"),
#     ]
# )


just_chat_system_template = """
You are Myfolio's counselling AI,
a friendly Assistant AI who has been equipped with your own special knowledge base and the ability to do Internet research for the user.
The users are usually related with highscool student's career and future education.
You have to check the Query and make the right answers for the students, their parents or teachers
Make sure to take into account that the user is a {user_type} when crafting your response.

USER TYPE:
{user_type}

USERS INTERESTED CAREER:
{user_career}

OUTPUT PROCEDURE:
Must mention the user's type if 'user_type' is not None.

OUTPUT:
"""

JUST_CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", just_chat_system_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{message}"),
    ]
)

chat_with_docs_system_template = """You are 탐라는 맛(Tamla's Flavor) AI, a friendly Assistant AI who has been equipped with your own special knowledge base, separated into collections. The currently selected collection is `{coll_name}`. In response to the user's query you have retrieved the most relevant parts of this collection you could find:

{context}

END OF PARTS OF YOUR KNOWLEDGE BASE YOU RETRIEVED.
Use them for your response ONLY if relevant. Use Markdown syntax for your reply."""
CHAT_WITH_DOCS_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", chat_with_docs_system_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{question}"),
    ]
)

# chat_greet_template = """
#         현재 제주도의 날씨를 기반으로 친근하고 재미있으며 약간 재치 있는 인사말을 만들어주세요.
#         오늘 날짜는 {date}이고, 현재 시간은 {time}입니다. 인사말을 만들 때 연중 날짜와 시간대를 고려해주세요.
#         예를 들어:
#         - 만약 오늘이 12월 31일이라면, 특별한 날임을 언급하고 축하할 만한 식사를 제안하세요.
#         - 만약 점심시간(오전 11시 ~ 오후 2시)이라면, 점심 메뉴를 제안하세요.
#         - 만약 저녁시간(오후 5시 ~ 오후 8시)이라면, 저녁 메뉴를 제안하세요.
#         - 제주도의 지역 음식인 '흑돼지', '전복죽', '고등어회', '고기국수', '딱새우', '성게 미역국', '오메기떡', '갈치조림' 등을 우선적으로 제안하되, 적절하지 않다면 일반적인 음식을 제안하세요.
        
#         현재 기온({temperature}°C)과 날씨 상태({weather_condition})를 언급하세요.
#         메시지를 재미있고 상황에 맞게 개인화해주세요.
        
#         예시 형식:
#         1.
#         - 인사말: "오늘 기온은 {temperature}°C로, {weather_condition}입니다. {time}인 지금, 제주도의 유명한 흑돼지 BBQ로 멋진 저녁을 즐겨보는 건 어떨까요?"
        
#         2.
#         - 인사말: "현재 기온은 {temperature}°C이며, {weather_condition}입니다. 상쾌한 점심을 즐기기 딱 좋은 시간이에요. 제주식 해물구이로 하루를 즐겨보세요!"
        
#         3.
#         - 인사말: "오늘은 12월 31일, 특별한 날이에요! 기온은 {temperature}°C로, {weather_condition}입니다. 한 해의 마무리를 제주도의 유명한 해물탕으로 축하해보는 건 어떨까요?"
        
#         4.
#         - 인사말: "기온은 {temperature}°C이고, {weather_condition}입니다. 저녁시간에 약간 쌀쌀하니, 제주 갈치조림으로 몸을 녹여보세요!"
        
#         5.
#         - 인사말: "좋은 오후입니다! 제주도는 현재 기온 {temperature}°C에 {weather_condition}입니다. 신선한 해산물과 시원한 음료로 맛있는 점심을 즐겨보세요!"
        
#         6.
#         - 인사말: "오늘 제주도는 아름다운 맑은 날씨에 기온이 {temperature}°C입니다. 점심시간인 지금, 더위를 이길 수 있는 제주 냉면 한 그릇은 어떠세요?"
        
#         안녕하세요는 생락하고, 톤을 친근하고 매력적으로 유지하며, 음식 제안이 세심하게 느껴지도록 해주세요. 따옴표 없이 인사말은 최대한 간단하게 {flag} 적어주세요. 
#         1.
        # - 인사말: "오늘 기온은 {temperature}°C로, {weather_condition}입니다. {time}인 지금, 시원하게 드라이아이스의 원리가 어떻게 이뤄져있는지 탐구 해보는 건 어떨까요?"
        
        # 2.
        # - 인사말: "오늘 기온은 {temperature}°C로, {weather_condition}입니다. {time}이니 살짝 출출할 시간인데요, 점심 메뉴로 먹은 음식들이 소화되는 원리, 우리 몸 속에서 어떤 과정을 거치는지 탐구해보는 건 어떨까요? '소화의 과학'을 공부하면서, 뇌도 함께 연료 보충해보세요!"
        
        # 3.
        # - 인사말: "오늘 기온은 {temperature}°C로, {weather_condition}이네요. {time}이니 저녁 준비 전, 잠깐 시간을 내어 '시간 관리의 비밀'을 공부해보는 건 어때요? 저녁 후엔 좀 더 여유롭게 쉴 수 있을 테니, 지금 짧고 강하게 집중해보는 것도 좋겠죠?"
        
        # 4.
        # - 인사말: 인사말: "현재 기온은 {temperature}°C이고, {weather_condition}이네요. {time}인 이 시간엔 밖에 나가기 좋은 날씨는 아니지만, 실내에서 '행성의 대기'에 대해 공부하며 이 날씨를 제대로 이해해보는 건 어떨까요? 나중에 친구들에게 똑똑한 날씨 박사가 될지도 몰라요!"
        
        # 5.
        # - 인사말: "오늘 기온은 {temperature}°C로, {weather_condition}입니다. {date}인 오늘은 {time}, 조금만 더 공부하면 하루가 훌쩍 지나가겠죠? '인간의 수면 주기'를 공부해서 오늘 밤엔 꿀잠 예약해보세요!"
        
        # 안녕하세요는 생락하고, 톤을 친근하고 매력적으로 유지하며, 음식 제안이 세심하게 느껴지도록 해주세요. 따옴표 없이 인사말은 최대한 간단하게 {flag} 적어주세요.         
# 
# """
chat_greet_template = """
        GOAL:
        * 당신은 공부관련 인삿말을 만들어주는 봇입니다.
        * 한 줄의 공부관련 내용을 만들어서 친근하고 재미있으며 약간 재치 있는 학습 또는 공부 관련 인사말을 만들어주세요.
        * 안녕하세요는 생락하고, 톤을 친근하고 매력적으로 유지하며, 음식 제안이 세심하게 느껴지도록 해주세요. 따옴표 없이 인사말은 최대한 간단하게 {flag} 적어주세요. 
        * 메시지를 재미있게 상황에 맞게 개인화해주세요.

        
        예시 형식:
        OUTPUT:
        "시원하게 드라이아이스의 원리가 어떻게 이뤄져있는지 탐구 해보는 건 어떨까요?"
        
        OUTPUT:
        "살짝 출출할 시간인데요, 점심 메뉴로 먹은 음식들이 소화되는 원리, 우리 몸 속에서 어떤 과정을 거치는지 탐구해보는 건 어떨까요? '소화의 과학'을 공부하면서, 뇌도 함께 연료 보충해보세요!"
        
        OUTPUT:
        "잠깐 시간을 내어 '시간 관리의 비밀'을 공부해보는 건 어때요? 저녁 후엔 좀 더 여유롭게 쉴 수 있을 테니, 지금 짧고 강하게 집중해보는 것도 좋겠죠?"
        
        OUTPUT:
        "실내에서 '행성의 대기'에 대해 공부하며 이 날씨를 제대로 이해해보는 건 어떨까요? 나중에 친구들에게 똑똑한 날씨 박사가 될지도 몰라요!"
        
        OUTPUT:
        "조금만 더 공부하면 하루가 훌쩍 지나가겠죠? '인간의 수면 주기'를 공부해서 오늘 밤엔 꿀잠 예약해보세요!"
        
        OUTPUT:
        """

CHAT_GREETING_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", chat_greet_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{message}"),
    ]
)

qa_template_summarize_kb = """You are a helpful Assistant AI who has been equipped with your own special knowledge base.
 In response to the user's query you have retrieved the most relevant parts of your knowledge base you could find:

{context}

END OF RETRIEVED PARTS OF YOUR KNOWLEDGE BASE.

USER'S QUERY: {question}

YOUR TASK: present the retrieved parts in a digestible way:
1. Start with the TLDR section heading (use Markdown) followed by a quick summary of only the retrieved parts directly relevant to the user's query, if there are any.
2. Continue the rest of your report in Markdown, with section headings. For this part, completely ignore user's query.

YOUR RESPONSE: """
QA_PROMPT_SUMMARIZE_KB = PromptTemplate.from_template(qa_template_summarize_kb)

qa_template_quotes = """You are a helpful Assistant AI who has been equipped with your own special knowledge base. In response to the user's query you have retrieved the most relevant parts of your knowledge base you could find:

{context}

END OF PARTS OF YOUR KNOWLEDGE BASE YOU RETRIEVED.

USER'S QUERY: {question}

YOUR TASK: print any quotes from your knowledge base relevant to user's query, if there are any. Use Markdown syntax for your reply.
YOUR RESPONSE: """
QA_PROMPT_QUOTES = PromptTemplate.from_template(qa_template_quotes)

researcher_template_gpt_researcher = (
    'Information: """{texts_str}"""\n\n'
    "Using the above information, answer the following"
    ' query or task: "{query}" in a detailed report --'
    " The report should focus on the answer to the query, should be well structured, informative,"
    " in depth and comprehensive, with facts and numbers if available and a minimum of 1000 words.\n"
    "You should strive to write the report as long as you can using all relevant and necessary information provided.\n"
    "You must write the report with markdown syntax.\n "
    "Use an unbiased and journalistic tone. \n"
    "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n"
    "You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.\n"
    "You MUST write the report in apa format.\n "
    "Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them.\n"
    "Please do your best, this is very important to my career. "
    "Assume that the current date is {datetime}"
)

researcher_template_simple = """<sources>{texts_str}</sources>
Please extract all information relevant to the following query: 
<query>{query}</query>
Write a report, which should be: 1500-2000 words long, in markdown syntax, in apa format. List the references used.
"""
RESEARCHER_PROMPT_SIMPLE = PromptTemplate.from_template(researcher_template_simple)

query_generator_template = """# MISSION
You are an advanced assistant in satisfying USER's information need.

# INPUT 
You are given the following query: {query}
Current timestamp: {timestamp}

# HIGH LEVEL TASK
You don't need to answer the query. Instead, your goal is to determine the information need behind the query and help USER generate a sophisticated plan to satisfy that information need.

# OUTPUT
There are two parts to your output:

## PART 1: Array of google search queries that would be most helpful to perform. These could be sub-questions and/or different ways to rephrase the original query to get an objective, unbiased, up-to-date answer. Use everything you know about information foraging and information literacy in this task.

## PART 2: Brief description of the type of answer/report that will best suit the information need. Examples: "comprehensive report in apa format", "step by step plan of action", "brief one sentence answer", "python code snippet", etc. Use your best judgement to describe the report that will best satisfy the information need. Keep in mind that the report will be written by another LLM, so it can't have images.

Your output should be in JSON following the examples below.

## EXAMPLES OF OUTPUT 

query: "How do I start with Langchain? I want to use it to make a chatbot that I can deploy on a website."
timestamp: Thursday, March 13, 2025, 04:40 PM

output: {{"queries": ["langchain chatbot tutorial March 2025", "langchain getting started", "deploy langchain chatbot on website"],
"report_type": "step by step guide including code snippets, 1500-3000 words"}}


query: "openai news"
timestamp: Saturday, June 22, 2024, 11:01 AM

output: {{"queries": ["openai news June 22 2024", "openai products new features June 2024", "openai organization updates June 2024"],
"report_type": "specifics-dense report rich in facts and figures, 1000-2000 words long"}}


query: "how can I merge two dictionaries in python?"
timestamp: Saturday, November 08, 2025, 06:04 PM

output: {{"queries": ["python merge dictionaries", "python 2025 dictionary union"],
"report_type": "python code snippet with explanation, likely less than 500 words"}}


query: "could you give me a comprehensive medical report on treating chronic migraines?"
timestamp: Monday, August 12, 2024, 11:15 PM

output: {{"queries": ["chronic migraines treatment", "medications for chronic migraines", "non-drug treatments for chronic migraines", "differential diagnosis migraines", "alternative treatments for chronic migraines", "chronic migraines recent research August 2024"],
"report_type": "comprehensive medical report, 1500-2000 words long"}}


query: "how old was John Lennon during the Cuban Missile Crisis?"
timestamp: Tuesday, September 12, 2023, 07:39 AM

output: {{"queries": ["John Lennon birth date", "Cuban Missile Crisis dates"],
"report_type": "brief relevant facts, followed by a formula to calculate the answer, followed by the answer"}}


query: "how old was John Lennon during the Cuban Missile Crisis? I want a report in apa format."
timestamp: Tuesday, September 12, 2023, 07:39 AM

output: {{"queries": ["John Lennon birth date", "Cuban Missile Crisis dates", "John Lennon during Cuban Missile Crisis"],
"report_type": "report in apa format, at least 1000 words long"}}

# YOUR ACTUAL OUTPUT
query: "{query}"
timestamp: {timestamp}

output: """
QUERY_GENERATOR_PROMPT = PromptTemplate.from_template(query_generator_template)

search_queries_updater_template = """\
You are an advanced assistant in satisfying USER's information need.

# High Level Task

You will be provided information about USER's query and current state of formulating the answer. Your task is to determine what needs to be added or improved in order to better satisfy USER's information need and strategically design a list of google search queries that would be most helpful to perform.

# Input

1. USER's query: {query} 
END OF USER's query 

2. Current timestamp: {timestamp}
END OF timestamp

3. Requested answer format: {report_type}
END OF requested answer format

4. Google search queries used to generate the current draft of the answer: {search_queries}
END OF search queries

5. Current draft of the answer: {report}

# Detailed Task

Let's work step by step. First, you need to determine what needs to be added or improved in order to better satisfy USER's information need. Then, based on the results of your analysis, you need to strategically design a list of google search queries that would be most helpful to perform to get an accurate, complete, unbiased, up-to-date answer. Design these queries so that the google search results will provide the necessary information to fill in any gaps in the current draft of the answer, or improve it in any way.

Use everything you know about information foraging and information literacy in this task.

# Output

Your output should be in JSON in the following format:

{{"analysis": <brief description of what kind of information we should be looking for to improve the answer and why you think the previous google search queries may not have yielded that information>,
"queries": [<array of 3-7 new google search queries that would be most helpful to perform, based on that analysis>]}}

# Example

Suppose the user wants to get a numbered list of top Slavic desserts and you notice that the current draft includes desserts from Russia and Ukraine, but is missing desserts from other, non-former-USSR Slavic countries. You would then provide appropriate analysis and design new google search queries to fill in that gap, for example your output could be:

{{"analysis": "The current draft of the answer is missing desserts from other Slavic countries besides Russia and Ukraine. The current search queries seem to have resulted in content being mostly about countries from the former USSR so we should specifically target other Slavic countries.",
"queries": ["top desserts Poland", "top desserts Czech Republic", "top desserts Slovakia", "top desserts Bulgaria", "best desserts from former Yugoslavia", "desserts from Easern Europe"]}}

# Your actual output

Now, please use the information in the "# Input" section to construct your actual output, which should start with the opening curly brace and end with the closing curly brace:


"""
SEARCH_QUERIES_UPDATER_PROMPT = PromptTemplate.from_template(
    search_queries_updater_template
)

researcher_template_initial_report = (
    """<sources>{texts_str}</sources>
The above information has been retrieved from online sources. Please use it to \
answer the following query: 

<query>{query}</query>

Your answer/report type must be: {report_type}. 

The query and report type provide the most important guidelines, but here are additional general guidelines:
1. Focus on addressing the specific query.
2. Avoid fluff and irrelevant information.
3. Provide available facts, figures, examples, details, dates, locations, etc.
4. If not enough information is available, be honest about it.

Use Markdown syntax for your answer. Start with a title.

Write **only** the report, followed by \
"""
    + REPORT_ASSESSMENT_INSTRUCTION
)

researcher_template_initial_report = (
    """\
Here is the scraped content of some online sources.

<sources>{texts_str}</sources>

Using them, please respond to the following query:

<query>{query}</query>

"""
    + REPORT_INSTRUCTION
)

RESEARCHER_PROMPT_INITIAL_REPORT = ChatPromptTemplate.from_messages(
    [("user", researcher_template_initial_report)]
)

report_combiner_template = (
    """\
Here are two reports.

1/2:
{report_1}

END OF REPORT 1/2

2/2:
{report_2}

END OF REPORT 2/2

Both reports/answers were written with the aim to best respond to the following query:

<query>{query}</query>

The difference in the reports' content is because they were written using different online sources. Your task: use the above content to write a new version of the report, which will be even better, since it will be indirectly based on twice as many sources as each report individually. Follow these guidelines:

1. Most important: focus on addressing the above query. Provide available facts and figures, if any, and be as specific as possible. Avoid irrelevant information, filler words, and generalizations. If not enough information is available, be honest about it and avoid just filling up space.

2. Use Markdown syntax for your answer. Start with a title.

3. Please write **only** the complete report, followed by \
"""
    + REPORT_ASSESSMENT_INSTRUCTION
)

report_combiner_template = (
    """\
Here are two reports compiled from two sets of online sources.

1/2:
{report_1}

END OF REPORT 1/2

2/2:
{report_2}

END OF REPORT 2/2

Using them, please respond to the following query:

<query>{query}</query>

Strive to keep all information from both reports. For example, if both reports contain \
lists of items, include all items from both reports (de-duplicate if necessary).

"""
    + REPORT_INSTRUCTION
)


REPORT_COMBINER_PROMPT = ChatPromptTemplate.from_messages(
    [("user", report_combiner_template)]
)

_searcher_template = """\
Here is the scraped content of some online sources.

<sources>{context}</sources>

Your task: determine if the above sources contain the answer to the following query:

<query>{query}</query>

Answer following one of these scenarios:

1. If the information to answer the query is not available in the sources, write: "ANSWER NOT FOUND".
2. If the sources contain information to fully answer the query, then write: "ANSWER: " followed by the answer. Cite the source where you found the information, including its URL. If more than one source was needed, cite all of them, including their URLs.
3. If the sources contain information to partially answer the query, then write: "PARTIAL ANSWER (<percentage of the answer that was found>)%: " followed by the partial answer. Again, cite the source(s) where you found the information, including their URL(s). 
"""

_possible_report_template = """\
... Use only information from the sources, no extra info please. If the sources don't contain relevant information, just say so without trying to make up your own info. After each paragraph, include the URL(s) of the source(s) from which the information was used. If there's no relevant source for a paragraph, write [NO_SOURCE] after it
"""


iterative_report_improver_template = (
    """\
You are ARIA, Advanced Report Improvement Assistant. 

For this task, you can use the following information retrieved from the Internet:

{new_info}

END OF RETRIEVED INFORMATION 

Your task: pinpoint areas of improvement in the report/answer prepared in response to the following query:

{query}

END OF QUERY. REPORT/ANSWER TO ANALYZE:

{previous_report}

END OF REPORT

That report was prepared using information from elsewhere. Your task: combine all of the provided information into a new report. Specifically:

Please write: "ACTION ITEMS FOR IMPROVEMENT:" then provide a numbered list of the individual SOURCEs in the RETRIEVED INFORMATION: first the URL, then specific instructions, in imperative form, for how to use **that particular** URL's CONTENT from above to enhance the report - use word economy, no filler words, and if that particular content is not useful then just write "NOT RELEVANT". Be brief, one numbered list item per SOURCE, with just one or two sentences per item.

Add one more item in your numbered list - any additional instructions you can think of for improving the report/answer, independent of the RETRIEVED INFORMATION, particularly as related to the overall structure of the report, for example how to rearrange sections, what parts to remove, reword, etc. Again, be brief.

After that, write: "NEW REPORT:" and write a new report from scratch in Markdown format, starting with a title. Important: any action items you listed must be **fully** implemented in your report, in which case your report must necessarily be different from the original report. In fact, the new report can be completely different if needed, the only concern is to craft an informative, no-fluff answer to the user's query:

{query}

END OF QUERY. This new report/answer should be: {report_type}. (in case of conflict, user's query takes precedence)

Finish with: """
    + REPORT_ASSESSMENT_INSTRUCTION
    + """\
Don't use Markdown here, only for the new report/answer.

**Important**: don't delete information from the report only because it can't be verified using the provided sources! The information in the report was obtained from previously retrieved sources!
"""
)

ITERATIVE_REPORT_IMPROVER_PROMPT = ChatPromptTemplate.from_messages(
    [("user", iterative_report_improver_template)]
)

summarizer_template = """\
Summarize the following content. Use Markdown syntax. Start with a short title. \
Then have a TL;DR (1 short paragraph). Then summarize the content in an easily digestible way. \
Act like an experienced content writer, \
who knows how to explain and format your articles/blog posts for easy reading: \
1. Break things up into short paragraphs, 1-3 sentences long.
2. Use section headings, numbered or bullet point lists, \
other Markdown formatting features to add structure and make the content easy to scan.

CONTENT:
{content}
"""

SUMMARIZER_PROMPT = ChatPromptTemplate.from_messages([("user", summarizer_template)])
