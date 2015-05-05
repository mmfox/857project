import imp
imp.load_source('pyaes', './pyaes/pyaes/aes.py')
import pyaes
import os
import math
import random
class UFE:
    def __init__(self, modeOfOperation, key1, key2, key3, modifiedUFE=False, m2rRatio=0.125):
        self.modeOfOperation = modeOfOperation
        self.k1 = key1
        self.k2 = key2
        self.k3 = key3
        self.modifiedUFE = modifiedUFE
        self.m2rRatio = m2rRatio
        self.blockSize = 128

    def encrypt(self, message):
        # create random r
        (r_padded, r_original) = self.eugenes_large_erection(message)
        # encrypt message and create ciphertext
        if self.modeOfOperation == "CTR":
            counter = pyaes.Counter(initial_value = self.bits_to_int(r_padded))
            aes = pyaes.AESModeOfOperationCTR(self.k1, counter = counter)
            ciphertext = aes.encrypt(message)
        
        
        # CBC Mode of Operation
        elif self.modeOfOperation == "CBC":
            (paddedMessageBlocks, numBlocks) = self.pad_message_CBC(message)
            ciphertext = ''
            aes = pyaes.AESModeOfOperationCBC(self.k1, iv = self.bits_to_string(r_padded))
            for i in range(numBlocks):
                ciphertext = ciphertext + aes.encrypt(paddedMessageBlocks[i])
            
            
            
        # CFB Mode of Operation
        elif self.modeOfOperation == "CFB":
            aes = pyaes.AESModeOfOperationCFB(self.k1, iv = self.bits_to_string(r_padded))
            ciphertext = aes.encrypt(message)
            
        # create CBC-MAC of ciphertext
        CBC_MAC = self.cbc_mac(ciphertext)
        
        
        # CBC_MAC is a list of bytes represented as integers
        # xor CMB_MAC with r
        r = self.bits_to_bytes(r_original)
        sigma = []
        for i in range(len(r)):
            sigma.append(CBC_MAC[i]^r[i])
            
        # sigma is a list of bytes represented as integers
        sigmaStr = ''
        for s in sigma:
            sigmaStr = sigmaStr + chr(s)
        return (ciphertext, sigma)
        


    def decrypt(self, ciphertext, sigma):
        
        # calculate CBC_MAC of ciphertext
        CBC_MAC = self.cbc_mac(ciphertext)
        
        # find r from sigma
        r = []
        for i in range(len(sigma)):
            r.append(chr(CBC_MAC[i]^sigma[i]))
        # turn r into eugene's form
        r_original = self.string_to_bits(r)
        # create r_padded
        # r_padded = self.pad(r_original)
        
        r_padded = self.pad_r(r_original)
        
        
        # decrypt using AES
        if self.modeOfOperation == "CTR":
            counter = pyaes.Counter(initial_value = self.bits_to_int(r_padded))
            aes = pyaes.AESModeOfOperationCTR(self.k1, counter = counter)
            plaintext = aes.decrypt(ciphertext)
        
        
        # CBC Mode of Operation
        elif self.modeOfOperation == "CBC":
            ciphertextBlocks = self.split_ciphertext_into_blocks(ciphertext)
            numBlocks=len(ciphertextBlocks)
            plaintext = ''
            aes = pyaes.AESModeOfOperationCBC(self.k1, iv = self.bits_to_string(r_padded))
            for i in range(numBlocks):
                plaintext = plaintext + aes.decrypt(ciphertextBlocks[i])
            plaintext=self.unpad_message_CBC(plaintext)
            
            
        # CFB Mode of Operation
        elif self.modeOfOperation == "CFB":
            aes = pyaes.AESModeOfOperationCFB(self.k1, iv = self.bits_to_string(r_padded))
            plaintext = aes.decrypt(ciphertext)
            
        # return plaintext
        return plaintext
        


    
    def pad_message_CBC(self, message):
        # TODO
        # pad message so that it is a multiple of 16 bytes
        # returns a list of plaintexts in 16 byte blocks and the number of blocks
        message_bytes = [ ord(c) for c in message ]
        padded_blocks = []
        numBlocks = int(math.ceil(len(message_bytes)/16.0))
        # pad
        for i in range((numBlocks*16) - len(message_bytes)):
            # TODO change the padding structure so we don't change the final letter of the message
            message_bytes.append(0)
        for i in range(numBlocks):
            block = message_bytes[i*16:(i+1)*16]
            string_block = []
            for b in block:
                string_block.append(chr(b))
            padded_blocks.append(string_block)
        
        return (padded_blocks, numBlocks)

    def unpad_message_CBC(self,message):
        message_bytes = [ ord(c) for c in message if ord(c)!=0]
        return "".join([chr(x) for x in message_bytes])

                    
    def split_ciphertext_into_blocks(self, ciphertext):
        # break the cipher text into blocks of 16 letters
        blocks = []
        block = ''
        for i in range(len(ciphertext)):
            block = block + str(ciphertext[i])
            if (i+1)%16 == 0:
                blocks.append(block)
                block = ''
        return blocks
            
        
    
    # Takes in message as unicode string, outputs CBC_MAC as a list of bytes (in integer form)
    def cbc_mac(self, ciphertext):
        aes1 = pyaes.AESModeOfOperationCBC(self.k2)
        # convert message to bytes
        #blocks = [ ord(c) for c in ciphertext ]
        blocks = self.split_ciphertext_into_blocks(self.string_to_bits(ciphertext))
        #ciphertext = aes.encrypt(plaintext_bytes)
        n = len(blocks)
        for i in range(n-1):
            nxt=aes1.encrypt(blocks[i])
        aes2 = pyaes.AESModeOfOperationCBC(self.k3,iv = nxt)
        nxt=self.bits_to_bytes(self.string_to_bits(aes2.encrypt(blocks[n-1])))
        return nxt
        
        
    # returns a list, first element is r without padding represented as list of bits
    # second element is r with padding represented as list of bits
    def eugenes_large_erection(self, message):
        # Eugene get this shit done
        result = []
        messageBitArray = self.string_to_bits(message)
        if self.modifiedUFE:
            lengthOfR = math.ceil(len(messageBitArray)/self.m2rRatio)
            if lengthofR>16:
                lengthOfR=16
        else:
            lengthOfR = 16
        rand = random.getrandbits(lengthOfR)
        rand = self.int_to_bitlist(rand)
        result.append(rand)
        while len(rand) < self.blockSize:
            rand.append(0)
        result.append(rand)
        return result


    # input is a list of bits, output is a list of ints
    def bits_to_bytes(self, bits):
        byteList = []
        for b in range(len(bits) / 8):
            byte = bits[b*8:(b+1)*8]
            byteList.append(int(''.join([str(bit) for bit in byte]), 2))
        return byteList

    # input is a list of bits
    def bits_to_string(self, bits):
        chars = []
        for b in range(len(bits) / 8):
            byte = bits[b*8:(b+1)*8]
            chars.append(chr(int(''.join([str(bit) for bit in byte]), 2)))
        return ''.join(chars)

    # input is list of bits, returns integer
    def bits_to_int(self, bits):
        e = 0
        res = 0
        for i in reversed(range(len(bits))):
            if bits[i] == 1:
                res = res + (2**e)
            e = e + 1
        return res

    # converts an integer into a list of bits
    def int_to_bitlist(self, n):
        return [int(digit) for digit in bin(n)[2:]]

    def pad_r(self, r):
        res = []
        while len(r) < self.blockSize:
            r.append(0)
        res = r
        return res

    # returns a list of bits
    def string_to_bits(self, s):
        result = []
        for c in s:
            bits = bin(ord(c))[2:]
            bits = '00000000'[len(bits):] + bits
            result.extend([int(b) for b in bits])
        return result    

key1=os.urandom(16)
key2=os.urandom(16)
key3=os.urandom(16)
a = UFE('CTR',key1,key2,key3)
b = UFE('CBC',key1,key2,key3)
c = UFE('CFB',key1,key2,key3)