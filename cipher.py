import util
import numpy as np

# __all__ = ["Hill", "Des"]
PRIM_256 = [
    1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 37, 39, 41, 43, 45, 47, 49, 51, 53, 55, 57, 59, 61, 63, 65, 67, 69, 71, 73, 75, 77, 79, 81, 83, 85, 87, 89, 91, 93, 95, 97, 99,
    101, 103, 105, 107, 109, 111, 113, 115, 117, 119, 121, 123, 125, 127, 129, 131, 133, 135, 137, 139, 141, 143, 145, 147, 149, 151, 153, 155, 157, 159, 161, 163, 165, 167, 169, 171, 173, 175, 177,
    179, 181, 183, 185, 187, 189, 191, 193, 195, 197, 199, 201, 203, 205, 207, 209, 211, 213, 215, 217, 219, 221, 223, 225, 227, 229, 231, 233, 235, 237, 239, 241, 243, 245, 247, 249, 251, 253, 255
]

HILL_KEY = [[21, 109, 119, 23, 88, 15, 116, 66], [22, 119, 70, 118, 111, 82, 121, 98], [79, 86, 2, 96, 90, 54, 95, 83], [22, 100, 113, 122, 92, 6, 52, 60], [1, 9, 9, 4, 112, 13, 26, 74],
            [3, 100, 92, 83, 51, 122, 102, 63], [71, 110, 92, 74, 26, 96, 92, 24], [30, 10, 85, 92, 47, 91, 114, 108]]

HILL_KEY_REVERSE = [[138, 124, 28, 104, 136, 176, 193, 182], [65, 229, 101, 214, 103, 57, 4, 224], [140, 138, 214, 71, 46, 62, 148, 184], [77, 64, 202, 44, 119, 246, 60, 86],
                    [69, 173, 41, 8, 106, 175, 255, 119], [105, 45, 131, 23, 116, 193, 29, 114], [190, 79, 82, 26, 81, 22, 187, 253], [70, 99, 51, 2, 221, 248, 152, 59]]


class Hill:
    __key = [[]]
    __content = [[]]

    def __init__(self, content=[[]], key=[[]]):
        self.__content = content  ## BlockArray
        self.__key = key  ## BlockArray

    def set_key(self, key):
        self.__key = key

    def reset_key(self):
        self.__key = [[]]

    def put_key(self, isPrint=False):
        if self.__key != [[]]:
            if isPrint:
                print("希尔密码密钥：")
                for line in self.__key:
                    print(line)
            return self.__key
        else:
            print("Warning: 对象没有密钥")

    def set_content(self, content):
        pass

    def reset_content(self):
        self.__content = []

    def put_content(self, isPrint=False):
        self.put_key(self.__key)

    def generate_hill_key_block(self, keyLen, keySapce=256, method=""):
        if np.sqrt(keyLen) != int(np.sqrt(keyLen)):
            keyLen = (int(np.sqrt(keyLen) + 1)) * (int(np.sqrt(keyLen) + 1))
            print("希尔密码密钥长度重置为" + str(keyLen))
        rowLen = int(np.sqrt(keyLen))
        keyBlock = []
        keyLine = []

        # for i in range(0, rowLen):
        #     for j in range(0, rowLen):
        #         keyLine.append(PRIM_256[np.random.randint(0, 128)])
        #     keyBlock.append(keyLine)
        #     keyLine = []

        while 1:
            for i in range(0, rowLen):
                for j in range(0, rowLen):
                    keyLine.append(np.random.randint(0, 128))
                keyBlock.append(keyLine)
                keyLine = []
            det = FiniteField.det(np.array(keyBlock), keySapce)
            if FiniteField.gcd(det % keySapce, keySapce) == 1:
                break
            # 非可逆矩阵，清除
            keyBlock = []

        if method == "return":
            return keyBlock
        self.__key = keyBlock

    @staticmethod
    # formatLen 控制标准化输打印输出
    def format_key_block(keyBlock, formatLen=3):
        keyStringArray = []
        for keyLen in keyBlock:
            keyString = ""
            for item in keyLen:
                for i in range((formatLen + 1) - len(str(item)) % (formatLen + 1)):
                    keyString += " "
                keyString += str(item)
                keyString += " "
            keyStringArray.append(keyString)
        return keyStringArray

    @staticmethod
    def print_key_string_array(keyStringArray):
        for keyString in keyStringArray:
            print(keyString)

    def generate_hill_key_block_array(self, keyLen, blockNum, keySapce=256, method=""):
        keyBlockArray = []
        for num in range(blockNum):
            keyBlockArray.append(self.generate_hill_key_block(keyLen, method="return"))
        if method == "return":
            return keyBlockArray
        self.__key = keyBlockArray

    def encrypt(self, field, **arg):
        cipherBlockArray = Hill.encrypt_block_array(self.__content, self.__key, 256)
        return cipherBlockArray

    def decrypt(self, fied, **arg):
        plainBlockArray = Hill.decrypt_block_array(self.__content, self.__key, 256)
        return plainBlockArray

    @staticmethod
    def encrypt_block_array(contentBlockArray, keyBlockArray, field, multiKeyEncryption=False, **arg):
        cipherBlockArray = []
        keyBlockNum = 0
        if multiKeyEncryption:
            for contentBlock in contentBlockArray:
                outMetrix = Hill.encrypt_block(contentBlock, keyBlockArray[keyBlockNum % len(keyBlockArray)], field)
                cipherBlockArray.append(outMetrix)
                keyBlockNum += 1
        else:
            for contentBlock in contentBlockArray:
                outMetrix = Hill.encrypt_block(contentBlock, keyBlockArray, field)
                cipherBlockArray.append(outMetrix)
        return cipherBlockArray

    @staticmethod
    def decrypt_block_array(contentBlockArray, keyBlock, field):
        plainBlockArray = []
        for contentBlock in contentBlockArray:
            outMetrix = Hill.decrypt_block(contentBlock, keyBlock, field)
            plainBlockArray.append(outMetrix)
        return plainBlockArray

    # 希尔密码 Block 处理
    @staticmethod
    def encrypt_block(contentBlock, keyBlock, field):
        cipherBlock = []
        contentArray = np.array(contentBlock)
        keyArray = np.array(keyBlock)
        cipherBlock = np.ndarray.tolist(np.dot(contentArray, keyArray))
        cipherBlock = np.ndarray.tolist(np.array(cipherBlock) % (field))
        return cipherBlock

    @staticmethod
    def decrypt_block(contentBlock, keyBlock, field):
        plainBlock = []
        contentArray = np.array(contentBlock)
        keyArray = np.array(keyBlock)
        plainBlock = np.ndarray.tolist(np.dot(contentArray, keyArray) % (field))
        return plainBlock


class Des:
    # 常量部分
    # yapf: disable

    # P 盒
    IP = [[58, 50, 42, 34, 26, 18, 10, 2],
          [60, 52, 44, 36, 28, 20, 12, 4],
          [62, 54, 46, 38, 30, 22, 14, 6],
          [64, 56, 48, 40, 32, 24, 16, 8],
          [57, 49, 41, 33, 25, 17, 9, 1],
          [59, 51, 43, 35, 27, 19, 11, 3],
          [61, 53, 45, 37, 29, 21, 13, 5],
          [63, 55, 47, 39, 31, 23, 15, 7]]

    # P 盒逆
    IP_INV = []

    # S 盒
    S_BOX = [
        [[14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
         [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
         [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
         [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
         ],
        [[15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
         [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
         [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
         [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
         ],
        [[10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
         [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
         [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
         [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
         ],
        [[7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
         [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
         [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
         [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
         ],
        [[2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
         [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
         [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
         [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
         ],
        [[12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
         [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
         [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
         [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
         ],
        [[4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
         [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
         [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
         [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
         ],
        [[13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
         [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
         [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
         [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
         ]
    ]

    # yapf: disable

    def __init__(self):
        self.algorithm = "DES"

    def set_name(self, nn):
        self.name = nn

    def print(self):
        print("name is:" + self.name)


class FiniteField:
    __field = 0
    __content = []

    def __init__(self):
        '''
        扩展有限域函数
        '''

    def reset_field(self):
        self.__field = 0

    def set_content(self, content):
        self.__content = content

    def format_list(self, numberList):
        out = []
        if isinstance(numberList, int):
            out = numberList % self.__field
        else:
            for i in numberList:
                out.append(i % self.__field)
        return out

    def format_list_list(self, numberListList):
        outContent = []
        if isinstance(numberListList, int):
            outContent = self.format_list(numberListList)
        else:
            for i in range(len(numberListList)):
                if isinstance(numberListList[1], int):
                    outContent.append(self.format_list(numberListList[i]))
                else:
                    outContent.append(self.format_list_list(numberListList[i]))
        return outContent

    def format_content(self):
        self.__content = self.format_list_list(self.__content)

    def get_content(self):
        return self.__content

    def reset_content(self):
        self.__content = []

    def field(self, **arg):
        try:
            if "field" in arg:
                self.__field = arg["field"]
            elif "GF2" in arg:
                self.__field = 2 ^ arg["field"]
            else:
                raise Exception("Argument Error")
        except (ValueError, TypeError) as e:
            print(e)

    @staticmethod
    def is_squre_field_matrix(matrix):
        try:
            content = np.array(matrix)
            np.linalg.det(content)  # 只有方阵才能计算行列式
        except Exception:
            return False
        return True

    def inverse_matrix_in_field(self):
        if self.is_squre_field_matrix(self.__content):
            content = np.array(self.__content)  # 转换成矩阵
            martixSize = content.shape[0]
            eye = np.eye(martixSize)
            content = np.concatenate((content, eye), axis=1)  # 连接矩阵

            # 矩阵求逆变换
            '''
            Guass Jordan Elimination
            [[213,3213,23],
            [231,321,21],
            [23,42,21]]

            [[ 24.   0.   0. 141. 219. 102.]
            [  0. 170.   0.  60. 138. 162.]
            [  0.   0. 216.  41.  79. 118.]]
            '''
            self.__gauss_jordan_elimination_left_side(content)
            self.__gauss_jordan_elimination_right_side(content)
            self.__gauss_jordan_eliminate(content)
            out = [np.ndarray.tolist(content[i][martixSize:]) for i in range(content.shape[0])]
            print(out)
        else:
            raise TypeError

    def __gauss_jordan_eliminate(self, content):
        rowLen = content.shape[0]
        # clounmLen=Kcontent.shape[1]
        for i in range(rowLen):
            # For monitor
            # vector=np.zeros((1,clounmLen+1))
            time = FiniteField.get_prime(content[i][i], self.__field)
            content[i] = time * content[i] % self.__field
            content[i] = content[i] / content[i][i]
            
    @staticmethod
    def field_matrix_multiplication(matrix1,matrix2,field):
        return np.ndarray.tolist(np.dot(np.array(matrix1),np.array(matrix2))%field)

    @staticmethod
    # TODO:改名为扩展欧几里得算法
    def get_prime(number, field):
        '''
        用于求 number * result = 1 mod field
        7*8=1 mod 11
        '''
        flag = False
        for k in range(1, field):
            for i in range(field):
                if (i * number) % field == k:
                    flag = True
                    break
            if flag:
                break
        return i

    def __gauss_jordan_elimination_left_side(self, content):
        rowLen = content.shape[0]
        for i in range(len(content)):
            if content[i][i] == 0:
                content = self.switch_matrix_row(content, i, rowLen)
            for j in range(i):
                lcm = self.lcm(content[i][j], content[j][j])
                content[i] = content[i] * (lcm / content[i][j]) - content[j] * (lcm / content[j][j])
                content[i] = content[i] % self.__field  # 缩短 GCD 时间，都是内不应该写这里

    def __gauss_jordan_elimination_right_side(self, content):
        rowLen = content.shape[0]
        for i in range(rowLen - 1, -1, -1):
            if content[i][i] == 0:
                content = self.switch_matrix_row(content, i, rowLen, -1)
            for j in range(rowLen - 1, i, -1):
                lcm = self.lcm(content[i][j], content[j][j])
                content[i] = content[i] * (lcm / content[i][j]) - content[j] * (lcm / content[j][j])
                content[i] = content[i] % self.__field  # 缩短 GCD 时间，都是内不应该写这里

    @staticmethod
    def switch_matrix_row(metrix, row, martixSize, stepLen=1):
        i = row
        while True:
            row += stepLen
            if metrix[(row) % martixSize][i] != 0:
                break
        tmp = metrix[row]
        metrix[row] = metrix[(row) % martixSize]
        # metrix[(row+1)%martixSize]=tmp
        metrix[row] = tmp  # 理论上不应该存在最后一行盒第一行调换
        return metrix

    @staticmethod
    def gcd(m, n):
        if m > n:
            m, n = n, m
        if n % m == 0:
            return m
        else:
            return FiniteField.gcd(m, n % m)

    @staticmethod
    def lcm(m, n):
        if m * n == 0:
            return 0
        return int(m * n / FiniteField.gcd(m, n))

    @staticmethod
    def get_prime_num_list(filed):
        a = []
        for i in range(1, filed):
            if FiniteField.gcd(i, filed) == 1:
                a.append(i)
        return a

    @staticmethod
    def det(m, field):
        if len(m) <= 0:
            return None
        elif len(m) == 1:
            return m[0][0]
        else:
            s = 0
            for i in range(len(m)):
                n = [[row[a] for a in range(len(m)) if a != i] for row in m[1:]]  # 这里生成余子式
                s += m[0][i] * FiniteField.det(n,field) * (-1) ** (i % 2) % field
            return s


if __name__ == "__main__":
    a= FiniteField.field_matrix_multiplication(HILL_KEY_REVERSE,HILL_KEY,256)
    print(a)
