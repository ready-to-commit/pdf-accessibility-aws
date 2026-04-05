FROM public.ecr.aws/lambda/python:3.10

COPY app.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["app.lambda_handler"]