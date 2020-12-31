from prettytable import PrettyTable

x = PrettyTable(field_names=["name", "age", "sex", "money"])
x.add_row(["wang",20, "man", 1000])
x.add_row(["alex",21, "man", 2000])
x.add_row(["peiqi",22, "man", 3000])
# print(x)
print(x.get_string(sortby="money", reversesort=True))