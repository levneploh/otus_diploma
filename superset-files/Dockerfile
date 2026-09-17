mkdir -p custom
cat > custom/Dockerfile <<'EOF'
FROM apache/superset:6.1.0
USER root
RUN uv pip install --python /app/.venv/bin/python clickhouse-connect
USER superset
EOF
