FROM python:3
RUN pip install discord.py
RUN git clone https://github.com/cepawiel/DiscordTagsBot
CMD ["python", "./DiscordTagsBot/main.py"]
