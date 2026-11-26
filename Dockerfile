FROM python:3.12-slim
WORKDIR /srv
COPY toolkit/ toolkit/
COPY examples/ examples/
USER 10001
EXPOSE 8081
CMD ["python","-m","toolkit","serve","--port","8081"]
