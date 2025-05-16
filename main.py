import logging
import uuid
import time
import base64
import os
from fastapi import FastAPI, Request, Depends, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from PIL import Image
import requests
from setup_logging import setup_logging
from module import Words
logger = logging.getLogger(__name__)

# JWT相关配置
SECRET_KEY = os.getenv("JWT_SECRET_KEY")  # 生产环境中应使用更安全的密钥
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7

# 用户模型
class User(BaseModel):
    username: str
    email: str = None
    disabled: bool = False

class UserInDB(User):
    hashed_password: str

# 令牌模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str = None

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 用户数据库 - 在实际应用中应替换为真实数据库
fake_users_db = {
    "testuser": {
        "username": "testuser",
        "email": "testuser@example.com",
        "hashed_password": pwd_context.hash("testpassword"),
        "disabled": False,
    }
}

class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 从 header 中获取 X-Request-ID，如果没有则生成一个新的
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        request.state.request_id = request_id

        #  添加request_id到logging
        logging.getLogger().handlers[0].addFilter(lambda record: setattr(record, 'request_id', request_id) or True)

        logger.info(f"********** Request started: {request.method} {request.url} **********")
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(f"********** Request completed: Status {response.status_code} **********")

        return response

# JWT相关函数
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="用户已禁用")
    return current_user

app = FastAPI()
app.add_middleware(RequestIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以限制为特定的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from src import VocabVidManager
manager = VocabVidManager()

# 登录获取token
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 获取当前用户信息
@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# 定义一个需要认证的路由
@app.post("/gen-sentence")
async def gen_sentence(words: Words, current_user: User = Depends(get_current_active_user)):
    st = time.time()
    if not words.words:
        # 参数错误
        return {
            "code": 1,
            "massage": "参数错误",
            "data": {}
        }
    
    # 使用当前用户信息
    logger.info(f"用户 {current_user.username} 请求生成句子，单词: {words.words}")

    return StreamingResponse(manager.get_example_senctence(words.words), media_type="text/event-stream")

# 定义一个需要认证的路由
@app.get("/gpu/info")
async def gen_sentence():
    requests_url = os.getenv("gpu_url")
    return requests.get(requests_url).json()

# 定义一个需要认证的路由
@app.get("/okx")
async def gen_sentence():
    requests_url = os.getenv("okx_url")
    return requests.get(requests_url).json()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=20050, workers=1)

#  nohup python main.py > log.log &