from hashlib import sha256


def find_merkle_root(transactions):
    length = len(transactions)
    if length % 2 != 0:
        transactions.append(transactions[len(transactions)-1])
    i = 0
    while i < len(transactions):
        # print(i)
        encoded_string = str(transactions[i]).encode()
        hashed_string = sha256(encoded_string).hexdigest()
        # print(hashed_string, 'first')
        second_encoded_string = str(transactions[i+1]).encode()
        second_hashed_string = sha256(second_encoded_string).hexdigest()
        # print(second_hashed_string, 'second')
        sum_and_hashed_string = hashed_string + second_hashed_string
        transactions[i] = sha256(sum_and_hashed_string.encode()).hexdigest()
        del transactions[i+1]
        i += 1
    if(len(transactions)) != 1 and (len(transactions) != 2):
        find_merkle_root(tr)
    if(len(transactions) == 2):
        return sha256((str(transactions[0]) + str(transactions[1])).encode()).hexdigest()


if __name__ == '__main__':
    tr = [1, 2, 3, 4]
    merkle_root = find_merkle_root(tr)
    print(merkle_root)