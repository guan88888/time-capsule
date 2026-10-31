"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

# 先初始化数据库，再导入其他模块
from app.database_init import create_database_if_not_exists
create_database_if_not_exists()

from app.database import engine, Base
from app.routers import auth, user, capsules, emotions, achievements, ai

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建上传目录
os.makedirs("uploads/avatars", exist_ok=True)

app = FastAPI(
    title="时空胶囊 API",
    description="时空胶囊App后端API",
    version="1.0.0"
)

# 配置CORS，允许前端跨域请求
# 注意：CORS中间件必须在路由之前注册
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源，生产环境应设置具体域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有请求头
    expose_headers=["*"],  # 暴露所有响应头
)

# 注册路由（注意：静态文件服务应该在路由之后注册，避免路径冲突）
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(user.router, prefix="/api/user", tags=["用户"])
app.include_router(capsules.router, prefix="/api/capsules", tags=["胶囊"])
app.include_router(emotions.router, prefix="/api/emotions", tags=["情绪"])
app.include_router(achievements.router, prefix="/api/achievements", tags=["成就"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI功能"])

# 静态文件服务（用于访问上传的头像）
# 注意：mount 应该在路由注册之后，避免路径冲突
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
async def root():
    return {"message": "时空胶囊 API", "version": "1.0.0"}

# 添加异常处理器，确保所有HTTPException都包含CORS头
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
    # 手动添加CORS头，确保错误响应也能跨域
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

