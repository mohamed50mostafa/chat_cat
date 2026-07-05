#!/usr/bin/env bash
# exit on error
set -o errexit

# تثبيت المكتبات
pip install -r requirements.txt

# تجميع الملفات الثابتة
python manage.py collectstatic --noinput

# تطبيق الهجرات على قاعدة البيانات
python manage.py migrate