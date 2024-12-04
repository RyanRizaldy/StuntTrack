# Gunakan image dasar Python
FROM python:3.9-slim

# Set working directory di dalam container
WORKDIR /app

# Salin file aplikasi dan model ke dalam container
COPY . /app

# Install dependensi aplikasi dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8080 untuk aplikasi
EXPOSE 8080

# Jalankan aplikasi Flask
CMD ["python", "main.py"]
