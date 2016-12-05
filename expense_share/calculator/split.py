import itertools

MIN_ACCEPTED = 0.1


def calculate_owns(members, payments):
    members = dict.fromkeys(members,0)
    for payment in payments:
        members[payment['payee']] += payment['amount']
        dept_amount = payment['amount'] // len(payment['beneficiary'])
        for dept in payment['beneficiary']:
            members[dept] -= dept_amount

    return members


def calculate_payables(data):
    result = []
    while data:
        sort = sorted(data, key=data.__getitem__)
        payer = sort[0]
        pay_amount = data[payer]
        payee = sort[-1]
        amount = data[payee]
        if payee == payer:
            break  # TODO: return result
        if amount > - pay_amount:
            result.append((payer, payee, -pay_amount))
            data[payee] += pay_amount
            data.pop(payer)
            if abs(data[payee]) < MIN_ACCEPTED:
                data.pop(payee)
        else:
            data[payer] += amount
            result.append((payer, payee, amount))
            data.pop(payee)
            if abs(data[payer]) < MIN_ACCEPTED:
                data.pop(payer)

    return result


def optimized(data):
    result = []
    for x in range(2, len(data)):
        for t in itertools.combinations(data.items(), x):
            if abs(sum([v for k, v in t])) < MIN_ACCEPTED:
                new_data = dict(t)
                result += calculate_payables(new_data)
                _ = [data.pop(k) for k, v in t]
    if data:
        result += calculate_payables(data)
    return result


if __name__ == '__main__':
    t = {'calc': '69000', 'uncommitted_payment': {}, 'members': {'C', 'B', 'A'},
         'payments': [{'description': '', 'beneficiary': {'B', 'A'}, 'amount': 58000, 'payee': 'B'},
                      {'description': '\nHome', 'beneficiary': {'B', 'C', 'A'}, 'amount': 69000, 'payee': 'C'}]}
    m = calculate_owns(t)
    m = dict(a=100, b=50, c=-40, d=-10, e=-100)
    m = dict(a=10, b=-49, c=-50, d=65, e=-75, f=-99)  # http://stackoverflow.com/a/1163209/501979
    print('M:', m)
    v = calculate_payables(m)
    print('V', v)
    m = dict(a=-10, b=-49, c=-50, d=-65, e=75, f=99)
    print('optimized:', optimized(m))
    #
