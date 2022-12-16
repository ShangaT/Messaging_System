import rsa

(publicKey, privateKey) = rsa.newkeys(2048)

string = "Строка".encode('utf-8')
crypto = rsa.encrypt(string, publicKey)
not_crypto = rsa.decrypt(crypto, privateKey).decode('utf-8')

print (f"Строка: {string}")
print(f"Зашифрованаая строка: {crypto}")
print(f"Публичный ключ: {publicKey}")
print(f"Приватный ключ: {privateKey}")
print (f"{not_crypto}")
