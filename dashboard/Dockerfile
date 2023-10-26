FROM python

WORKDIR /app

COPY dashboard_requirements.txt .

RUN pip3 install -r dashboard_requirements.txt

COPY dashboarding_from_db.py .

EXPOSE 8501

CMD ["streamlit", "run", "dashboarding_from_db.py"]