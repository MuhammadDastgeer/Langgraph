# from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

os.environ["LANGSMITH_PROJECT"] = "langsmith-demo1"


load_dotenv()

prompt1 = PromptTemplate(
    template='Generate a detailed report on {topic}',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Generate a 5 pointer summary from the following text \n {text}',
    input_variables=['text']
)

# model = ChatOpenAI()
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

parser = StrOutputParser()

chain = prompt1 | model | parser | prompt2 | model | parser

config = {
    'run_name': 'sequential chain',
    'tags': ['llm app', 'report generation', 'summarization'],
    'metadata': {
        'model1': 'gpt-4o-mini',
        'model1_temp': 0.7,
        'parser': 'stroutputparser'
    }
}

result = chain.invoke({'topic': 'Unemployment in India'}, config=config)

print(result)
