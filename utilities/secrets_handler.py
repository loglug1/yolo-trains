import os

def read_secret(secret_file):
    """
    Reads the content of a specific secret file from /run/secrets.
    """
    try:
        with open(secret_file, 'r') as f:
            secret_value = f.read().strip()
        return secret_value
    except FileNotFoundError:
        return None
    except Exception as e:
        return None

def read_all_secrets(secrets_directory="/run/secrets"):
    """
    Reads all secrets from the specified directory.
    """
    secrets = {}
    if not os.path.exists(secrets_directory):
        return secrets

    try:
        for filename in os.listdir(secrets_directory):
            secret_path = os.path.join(secrets_directory, filename)
            if os.path.isfile(secret_path):
                with open(secret_path, 'r') as f:
                    secret_value = f.read().strip()
                    secrets[filename] = secret_value
        return secrets
    except Exception as e:
        return {}