with open("orders.txt", "r") as file:
    lines = file.readlines()
    for line in lines:
        print(f"'{line.strip()}'")