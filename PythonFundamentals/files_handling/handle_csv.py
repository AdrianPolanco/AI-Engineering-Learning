import csv

with open("file.csv", "w", newline="") as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(["name", "age", "religion"])
    writer.writerow(["Adrian", 24, "atheist"])
    writer.writerow(["Yarilyn", 21, "evangelical"])

with open("file.csv", "r") as csv_file:
    reader = csv.reader(csv_file)
    for row in reader:
        print(row)