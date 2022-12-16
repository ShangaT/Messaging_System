#pip install gostcrypto
import gostcrypto

key = "1234567890".rjust(32, '0').encode('utf-8')
text = "helloooooooo".encode('utf-8')

cipher_obj = gostcrypto.gostcipher.new('kuznechik', key, gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
encrypted_text = cipher_obj.encrypt(text)

cipher_obj_1 = gostcrypto.gostcipher.new('kuznechik', key, gostcrypto.gostcipher.MODE_ECB, pad_mode=gostcrypto.gostcipher.PAD_MODE_1)
decrypted_text = cipher_obj_1.decrypt(encrypted_text).decode('utf-8')

print(text)
print (encrypted_text)
print (decrypted_text)
