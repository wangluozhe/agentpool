from fastapi import FastAPI
import uvicorn
import aioredis
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI()
db = None
MAX_SCORE = 100
MIN_SCORE = 0
INIT_SCORE = 10
REDIS_KEY = 'proxies'

@app.on_event('startup')
async def start_event():
    global db
    db = await aioredis.create_redis_pool('redis://{host}:{port}/{database}'.format(host='127.0.0.1',port=6379,database=0))

@app.get('/')
async def index():
    #提示操作
    return {
        'message':'欢迎使用LeeGene的个人代理池',
        '/random':'获取随机代理地址',
        '/count':'获取代理总数量'
    }

@app.get('/random')
async def randoms():
    result = await db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
    if len(result):
        return {
            'status':200,
            'proxy':random.choice(result)
        }
    else:
        result = await db.zrevrange(REDIS_KEY, MIN_SCORE, MAX_SCORE)
        if len(result):
            return {
                'status':200,
                'proxy':random.choice(result)
            }
        else:
            return {
                'status':200,
                'proxy':'None'
            }

@app.get('/count')
async def count():
    result = await db.zcount(REDIS_KEY,MAX_SCORE,MAX_SCORE)
    if result:
        return {
            'status':200,
            'count':result
        }
    else:
        return {
            'status':200,
            'count':0
        }

def run(host='127.0.0.1',port=8000):
    uvicorn.run(app='api:app', host=host, port=port)
