from .random_fact import router as fact_router
from .talk import router as talk_router
from .gpt_chat import router as gpt_router
from .quiz import router as quiz_router
from .translator import router as translator_router
from .recommendations import router as recommendations_router

all_routers = [
    fact_router,
    talk_router,
    gpt_router,
    quiz_router,
    translator_router,
    recommendations_router
]
