class Person:

    # Constructor
    def __init__(self, name: str, age: int, gender: str):
        # Atributos de instancia
        self.name = name
        self.age = age
        if(gender != 'male' and gender != 'female'):
            raise ValueError("Gender must be 'male' or 'female'")
        self.gender = gender

    def eat(self, food: str) -> None:
        print(f"{self.name} is eating {food}...")

    def sleep(self) -> None:
        print(f"{self.name} is sleeping...")

    # Miembros protegidos (convencion de Python, no es privado)
    def _take_a_shower(self) -> None:
        print(f"{self.name} is taking a shower...")

    """Miembros privados (convencion de Python, no es privado realmente)
    Sin embargo, en el caso de los miembros privados, Python hace name mangling,
    es decir, si se hace por ejemplo person.__havesex() desde fuera de la clase, 
    dara un error de atributo ya que Python renombra el metodo a _Person__havesex() 
    para evitar colisiones de nombres con subclases"""
    def __have_sex(self, partner: Person) -> None:
        if(partner is self):
            raise ValueError("A person cannot have sex with themselves")
        if self.gender == partner.gender:
            raise ValueError("Both persons must have different genders")
        print(f"{self.name} is having sex with {partner.name}...")

    # El decorador @classmethod indica que el metodo es de clase, 
    # es decir, no necesita una instancia de la clase para ser llamado
    # El caso de uso principal es para definir constructores alternativos, 
    # es decir, metodos de fabrica que devuelven una instancia de la clase
    @classmethod
    def create_male(cls, name: str, age: int) -> Person:
        return cls(name, age, "male")

    @classmethod
    def create_female(cls, name: str, age: int) -> Person:
        return cls(name, age, "female")

# Employee hereda de Person, es decir, Employee es una subclase de Person
class Employee(Person):
    def __init__(self, name: str, age: int, gender: str, position: str, salary: float):
        super().__init__(name, age, gender)
        self.position = position
        self.salary = salary

    def work(self) -> None:
        print(f"{self.name} is working...")

    def detach_from_position(self) -> None:
        self.position = None
        self.salary = 0

class Department:
    def __init__(self, name: str, employees: set[Employee], manager: Manager|None = None):
        self.name = name
        self.employees = employees
        self.manager = manager

    def add_employee(self, employee: Employee) -> None:
        self.employees.add(employee)

    def remove_employee(self, employee: Employee) -> None:
        #if employee in self.employees:
        self.employees.discard(employee)
        employee.detach_from_position()

    def set_manager(self, manager: Manager) -> None:
        self.manager = manager
        self.add_employee(manager)

    def remove_manager(self) -> None:
        if self.manager is not None:
            self.remove_employee(self.manager)
            self.manager = None

    def disolve_department(self) -> None:
        for employee in self.employees:
            employee.detach_from_position()
        self.employees.clear()
        self.manager = None
        self.name = None

    @staticmethod
    def merge_departments(name: str, department1: Department, department2: Department) -> Department:
        #managers_set = {department1.manager, department2.manager}
        #ex_managers = {manager for manager in managers_set if manager is not None}
        #if ex_managers:
        #    for manager in ex_managers:
        #        manager.detach_from_position()
        department1.remove_manager()
        department2.remove_manager()
        merged_employees = department1.employees.union(department2.employees)
        merged_department = Department(name, merged_employees)
        department1.disolve_department()
        department2.disolve_department()
        return merged_department

class Manager(Employee):
    def __init__(self, name: str, age: int, gender: str, department: Department):
        super().__init__(name, age, gender, "Manager", 200000)

    @classmethod
    def create_manager(cls, name: str, age: int, gender: str, department: Department) -> Manager:
        manager = cls(name, age, gender, department)
        department.set_manager(manager)
        return manager

class ApplicationDevelopmentManager(Manager):
    pass

class InfrastructureManager(Manager):
    pass

class ITManager(Manager):
    pass

class FinanceManager(Manager):
    pass

# Ambas clases (ApplicationDevelopmentManager y FinanceManager) heredan de Employee,
# y reutilizan el metodo de clase create_manager() para crear instancias de ellas
application_development_department = Department('Application Development', set())
finance_department = Department('Finance', set())
application_development_manager = ApplicationDevelopmentManager.create_manager("Mengano", 42, "male", application_development_department)
finance_manager = FinanceManager.create_manager("Maria", 30, "female", finance_department)
infrastructure_department = Department('Infrastructure', set())
it_department = Department.merge_departments('IT', application_development_department, infrastructure_department)
it_manager = ITManager.create_manager("Adrian", 35, "male", it_department)
