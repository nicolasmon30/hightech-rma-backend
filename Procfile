release: alembic upgrade head && python init_superadmin.py
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
