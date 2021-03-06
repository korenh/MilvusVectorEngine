from fastapi import FastAPI, File, Form, Security, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyQuery, APIKey
from starlette.status import HTTP_403_FORBIDDEN
import uvicorn
from classmilvus import ClassMilvus
import config

config = config.get_config()
app = FastAPI(title=config['APP_TITLE'], version=config['APP_VERSION'])
app.add_middleware(CORSMiddleware, allow_origins=[
                   '*'], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
milvus_utils = ClassMilvus()


async def get_api_key(api_key_query: str = Security(APIKeyQuery(name='key', auto_error=False))):
    if api_key_query == config['SECRET']:
        return api_key_query
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN,
                            detail=config['AUTH_ERROR_STRING'])


@app.get('/create_collection/{collection_name}')
async def create_collection(collection_name, api_key: APIKey = Depends(get_api_key)):
    milvus_result = milvus_utils.create_collection(collection_name)
    return {"status": milvus_result}


@app.get('/drop_collection/{collection_name}')
async def drop_collection(collection_name, api_key: APIKey = Depends(get_api_key)):
    milvus_result = milvus_utils.drop_collection(collection_name).message
    return {"status": milvus_result}


@ app.get('/info_collection/{collection_name}')
async def info_collection(collection_name, api_key: APIKey = Depends(get_api_key)):
    milvus_result = milvus_utils.info(collection_name)
    return {"status": milvus_result}


@ app.post('/insert_collection/')
async def insert_collection(file: bytes = File(...), collection_name: str = Form(...), api_key: APIKey = Depends(get_api_key)):
    milvus_result = milvus_utils.insert(collection_name, file).message
    return {"status": milvus_result}


@ app.post('/search_collection/')
async def search_collection(file: bytes = File(...), collection_name: str = Form(...), api_key: APIKey = Depends(get_api_key)):
    milvus_result = milvus_utils.search(collection_name, file)
    return {"result": milvus_result}

uvicorn.run(app, host=config['APP_HOST'], port=config['APP_PORT'])
