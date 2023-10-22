FROM public.ecr.aws/lambda/python:3.10
RUN yum install -y Cython libxml2-devel libxslt-devel gcc python-devel
COPY requirements.txt .
COPY .env ${LAMBDA_TASK_ROOT}
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"
# Copy function code
COPY ./src/ ${LAMBDA_TASK_ROOT}/src
COPY ./funcs/data_upload.py ${LAMBDA_TASK_ROOT}
COPY ./funcs/llama2_inference.py ${LAMBDA_TASK_ROOT}
# CMD [ "data_upload.lambda_handler" ]
