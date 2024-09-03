FROM python:3.12

ARG PORT="3000"

WORKDIR /app

# Step 1: Copy only the requirements file to leverage layer caching
COPY ./requirements.txt /app/

# Step 2: Install dependencies from the requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 3: Copy the rest of the application code
COPY ./ /app/

# Step 4: Check if uvicorn is installed
RUN uvicorn --version

EXPOSE $PORT

# Step 5: Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
