from hashlib import sha256

previous_hash = '6629ddae3736e894e89cb4a1300a9d2c5c0fad418f8ea06a341b81f2a98bb491'


def get_new_right_hash_with_previous(previous, number):
    guess = f'{previous}{number}'.encode()
    #print(guess)                                #кодированная строка
    guess_hash = sha256(guess).hexdigest()
    #print(guess_hash)                           #новый хэш
    #print(len(str(guess_hash)))                 #длина хэша
    return str(guess_hash)[:7] == "0000000"


def get_two_num_for_generate_hash():
    num = 0
    while get_new_right_hash_with_previous(previous_hash, num) == False:
        num += 1
    return num


def answer_test(right_num):
    check = f'{previous_hash}{right_num}'.encode()
    print(sha256(check).hexdigest())


if __name__ == '__main__':
    get_right_num = get_two_num_for_generate_hash()
    print(get_right_num)
    answer_test(get_right_num)

