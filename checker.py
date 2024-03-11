import base64

encoded_password = "ZW14eWNYcG9WblJyUzBOVk9IaEhkQW89"
decoded_password = base64.b64decode(encoded_password).decode('utf-8')
print(decoded_password)
