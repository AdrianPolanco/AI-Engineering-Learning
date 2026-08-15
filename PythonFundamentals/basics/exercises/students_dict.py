students = {
    "Ana": [8,7,9],
    "Luis": [6,5,7],
    "Sofia": [10,9,10]
}

# Agregar nuevo estudiante
students['Adrian'] = [10,10,10]
students.setdefault('Yari', [10,10,10])

def avg(scores):
    # return (sum(scores)/len(scores)).__round__(2)
    raw_avg = sum(scores)/len(scores)
    return round(raw_avg, 2)

# Calcular el promedio de un estudiante
def average_student(student_key):
    if student_key in students.keys():
        scores = students[student_key]
        print(f"The average of {student_key} is: {avg(scores)}")

# Calcular el promedio del estudiante nuevo (ultimo estudiante)

def average_newest():
    if len(students):
        students_copy = students.copy()
        newest_student = students_copy.popitem()
        average = avg(newest_student[-1])
        print(f"The average of the newest student ({newest_student[0]}) is: {average}")

average_student("Adrian")
average_student("Yari")
average_student("Ana")
average_student("Sofia")
average_newest()