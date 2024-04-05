# snippet below comes from the official Airflow documentation:
# https://airflow.apache.org/docs/apache-airflow/1.10.12/security.html#generating-fernet-key
# run this to generate a Fernet key to secure your Airflow installation

from cryptography.fernet import Fernet

fernet_key = Fernet.generate_key()
print(fernet_key.decode())  # your fernet_key, keep it in secured place!
