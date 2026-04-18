FROM python:3.9-slim

WORKDIR /app

COPY backend/ backend/
COPY frontend/ frontend/

RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

EXPOSE 5000
EXPOSE 8501

CMD bash -c "python backend/app.py & streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0"