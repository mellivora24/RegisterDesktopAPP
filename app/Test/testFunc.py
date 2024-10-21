information = input()

id = information.split(" ")[0]
name = information.split(" ")
name = " ".join(name[1:])
print(f"ID: {id}")
print(f"Name: {name}")