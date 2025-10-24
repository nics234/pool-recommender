FROM python:3.11-slim
#Set working directory
WORKDIR /code

#Copy and install dependencies
COPY requirement.txt 
RUN pip install --no-cache-dir -r requirement.txt

# Copy project files 
COPY . 
COPY . .

#Command to run FASTAPO
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
