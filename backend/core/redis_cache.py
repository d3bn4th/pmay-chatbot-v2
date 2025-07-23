import redis

# Connect to local Redis instance
def get_redis_client():
    return redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

FAQ_KEYS = [
    "what is pmay?",
    "how to apply for pmay?",
    "what is the eligibility criteria?"
]

def get_faq_answer(question: str):
    r = get_redis_client()
    return r.get(question.lower())

def set_faq_answer(question: str, answer: str):
    r = get_redis_client()
    r.set(question.lower(), answer) 