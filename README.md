pip install -r requirements.txt

.venv312\Scripts\activate

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

.\.venv312\Scripts\python.exe -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
