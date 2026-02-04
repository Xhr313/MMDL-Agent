# Application entry point: expose FastAPI `app` for Uvicorn.
from app.api.main import app

# 切环境:conda activate pytorch（自己环境的命名）
# 终端运行: uvicorn main:app --reload
# 访问地址: http://127.0.0.1:8000
# 返回结果{"app":"industrial-anomaly-agent","version":"0.1.0","message":"Welcome to MMDL-Agent","docs":"/docs","openapi_schema":"/openapi.json"}
