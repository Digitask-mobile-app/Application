FROM redis:4.0.11

CMD ["sh", "-c", "exec redis-server --requirepass \"$REDIS_PASSWORD\""]
