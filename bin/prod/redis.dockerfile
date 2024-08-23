FROM redis:5

CMD ["sh", "-c", "exec redis-server --requirepass \"$REDIS_PASSWORD\""]
