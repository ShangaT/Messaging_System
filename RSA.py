#pip install rsa
import rsa

(publicKey, privateKey) = rsa.newkeys(2048)

p = publicKey.save_pkcs1()
key =  rsa.PublicKey.load_pkcs1(p)

string = "Строка".encode('utf-8')
crypto = rsa.encrypt(string, key)
#not_crypto = rsa.decrypt(crypto, privateKey).decode('utf-8')

print (crypto)

#pub_k_str = b'-----BEGIN RSA PUBLIC KEY-----' + str(publicKey).encode('utf-8') + b'-----END RSA PUBLIC KEY'
#ks = pub_k_str.encode('utf-8')
#pub_k_str = str(publicKey)
#key = rsa.PublicKey.load_pkcs1(pub_k_str)
