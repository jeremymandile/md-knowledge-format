FROM python:3.11-alpine

LABEL org.opencontainers.image.title="md-knowledge-format tool"
LABEL org.opencontainers.image.description="Unified CLI for LESSON.md and LESSONS.md — scaffold, validate, and export portable knowledge files."
LABEL org.opencontainers.image.source="https://github.com/jeremymandile/md-knowledge-format"

RUN pip install --no-cache-dir pyyaml markdown

COPY lesson_tool.py /usr/local/bin/lesson-tool

WORKDIR /workspace

ENTRYPOINT ["python", "/usr/local/bin/lesson-tool"]
