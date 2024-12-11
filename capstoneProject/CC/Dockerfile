# Gunakan image dasar Python
FROM python:3.11.9

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED=True

# Set working directory di dalam container
WORKDIR /app

# Salin file requirements.txt terlebih dahulu agar dependensi dapat diinstal
COPY requirements.txt /app/

# Install dependensi aplikasi dari requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua file dari direktori lokal ke dalam container
COPY . /app/

# Expose port yang digunakan oleh aplikasi (9898 sesuai dengan main.py)
EXPOSE 9898

# Jalankan aplikasi Flask
CMD ["python", "main.py"]
