FROM python:3

RUN pip install torch==1.8.1+cpu torchvision==0.9.1+cpu torchaudio==0.8.1 \
    -f https://download.pytorch.org/whl/torch_stable.html

RUN pip install mlflow

ADD package_models ./package_models

COPY stylize.py .

RUN python3 -m package_models

ENTRYPOINT ["python3", "./stylize.py"]
