FROM python:3
RUN pip install discord.py
ADD main.py .
CMD ["python", "./main.py"]
