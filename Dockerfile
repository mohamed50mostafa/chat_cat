# استخدام نسخة بايثون خفيفة ومستقرة
FROM python:3.10-slim

# ضبط متغيرات البيئة لمنع بايثون من كتابة ملفات كاش pyc ولعرض الـ logs فوراً
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# تثبيت التبعيات الأساسية للنظام
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# نسخ ملف المكتبات وتثبيتها
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي ملفات المشروع بالكامل إلى الحاوية
COPY . /app/

# Hugging Face Spaces تعطي الحاوية منفذ 7860 افتراضياً، لذلك سنخبر دجانجو أن يعمل عليه
EXPOSE 7860

# تشغيل الـ Migrations ثم انطلاق السيرفر عبر gunicorn
# (تأكد من تغيير كلمة project لاسم المجلد المالي الذي يحتوي على ملف wsgi.py)
CMD python manage.py migrate && gunicorn project.wsgi:application --bind 0.0.0.0:7860