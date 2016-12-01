import itertools

MIN_ACCEPTED = 0.1


def calculate_owns(data):
    members = dict.fromkeys(data['members'], 0)
    for payment in data['payments']:
        members[payment['payee']] += payment['amount']
        dept_amount = payment['amount'] // len(payment['beneficiary'])
        for dept in payment['beneficiary']:
            members[dept] -= dept_amount

    return members


def calculate_payables(data):
    result = []
    while data:
        sort = sorted(data, key=data.__getitem__)
        # print(data)
        payer = sort[0]
        pay_amount = data[payer]
        payee = sort[-1]
        amount = data[payee]
        # print(payee, amount, payer, pay_amount)

        if payee == payer:
            break  # TODO: return result
        # if abs(amount)- +pay_amount) < MIN_ACCEPTED:
        #     data.pop(payee)
        #     data.pop(payer)
        #     continue
        if amount > - pay_amount:
            # print('payee(%s) is bigger' % payee)
            result.append((payer, payee, -pay_amount))
            data[payee] += pay_amount
            data.pop(payer)
            if abs(data[payee]) < MIN_ACCEPTED:
                data.pop(payee)
                # print(payee, 'cleared')
                # print(payer, 'cleared')
        else:
            data[payer] += amount
            result.append((payer, payee, amount))

            # print(payee, 'cleared')
            data.pop(payee)
            if abs(data[payer]) < MIN_ACCEPTED:
                data.pop(payer)
                # print(payer,'cleared')
                # print(payer, pay_amount, payee, amount)

    return result


def optimized(data):
    result = []
    for x in range(2, len(data)):
        for t in itertools.combinations(data.items(), x):
            # print(t,abs(sum([v for k,v in t ])))
            if abs(sum([v for k, v in t])) < MIN_ACCEPTED:
                new_data = dict(t)
                result.append(calculate_payables(new_data))
                # print(result)
                _ = [data.pop(k) for k, v in t]
    if data:
        result.append(calculate_payables(data))
    return result


if __name__ == '__main__':
    t = {'calc': '69000', 'uncommitted_payment': {}, 'members': {'C', 'B', 'A'},
         'payments': [{'description': '', 'beneficiary': {'B', 'A'}, 'amount': 58000, 'payee': 'B'},
                      {'description': '\nHome', 'beneficiary': {'B', 'C', 'A'}, 'amount': 69000, 'payee': 'C'}]}
    m = calculate_owns(t)
    m = dict(a=100, b=50, c=-40, d=-10, e=-100)
    m = dict(a=10, b=-49, c=-50, d=65, e=-75, f=-99)
    print('M:', m)
    v = calculate_payables(m)
    print('V', v)
    m = dict(a=-10, b=-49, c=-50, d=-65, e=75, f=99)
    print('optimized:',optimized(m))
    #
