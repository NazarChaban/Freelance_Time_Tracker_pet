from django.contrib.auth import get_user_model
import django
import os

django.setup()


def create_superuser():
    User = get_user_model()
    username = os.environ.get("SUPERUSER_USERNAME")
    email = os.environ.get("SUPERUSER_EMAIL")
    password = os.environ.get("SUPERUSER_PASSWORD")

    if not User.objects.filter(username=username).exists():
        print("Creating superuser...")
        User.objects.create_superuser(username, email, password)
    else:
        print("Superuser exists.")

if __name__ == "__main__":
    create_superuser()
