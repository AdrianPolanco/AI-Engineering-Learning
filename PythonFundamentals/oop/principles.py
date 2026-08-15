class Subscription:
    def __init__(self, name: str, price: float, permissions: set[str]):
        self.name = name
        self.price = price
        self.permissions = permissions

    def delete_permission_to_account(self, permission: str, account: Account) -> bool:
        if "admin" not in self.permissions:
            raise ValueError("Only admin subscriptions can delete permissions")
        if permission not in account.subscription.permissions:
            raise ValueError(f"Account does not have permission '{permission}'")
        account.subscription.permissions.remove(permission)
        return True

    def cancel_subscription(self) -> None:
        if self.name == "Free":
            raise ValueError("Free subscription cannot be canceled")

        self.name = "Free"
        self.price = 0.0
        self.permissions = {"read"}

"""
Herencia: Las clases FreeSubscription, ProSubscription y MaxSubscription
estan heredando de la clase Subscription, es decir, tienen acceso a los
atributos y metodos de la clase Subscription, y pueden ser tratadas como instancias
de la clase Subscription, ya que son subclases de Subscription.
"""
class FreeSubscription(Subscription):
    def __init__(self):
        super().__init__("Free", 0.0, {"read"})

    def delete_permission_to_account(self, permission: str, account: Account) -> bool:
        raise ValueError("Free subscriptions cannot delete permissions")

class ProSubscription(Subscription):
    def __init__(self):
        super().__init__("Pro", 9.99, {"read", "write", "delete"})

    def delete_permission_to_account(self, permission: str, account: Account) -> bool:
        raise ValueError("Pro subscriptions cannot delete 'delete' permission")

class MaxSubscription(Subscription):
    def __init__(self):
        super().__init__("Max", 19.99, {"admin"})
    """Polimorfismo: La clase MaxSubscription esta sobrescribiendo
      el metodo delete_permission_to_account de la clase Subscription, es decir, 
      tiene una implementacion diferente a la de la clase Subscription, 
      pero sigue teniendo el mismo nombre y parametros,"""
    def delete_permission_to_account(self, permission: str, account: Account) -> bool:
        if permission == "admin":
            raise ValueError("Max subscriptions cannot delete 'admin' permission")
        return super().delete_permission_to_account(permission, account)

class Account:
    """
    Abstraccion: La clase Account esta utilizando simplemente una clase Subscription,
    sin importarle si es una FreeSubscription, ProSubscription o MaxSubscription.
    Las esta tratando a todas de la misma manera para sus propositos.
    """
    def __init__(self, username: str, subscription: Subscription):
        self.username = username
        self.subscription = subscription

    def upgrade_subscription(self, new_subscription: Subscription) -> None:
        if new_subscription.price <= self.subscription.price:
            raise ValueError("New subscription must be more expensive than the current one")
        self.subscription = new_subscription

    def downgrade_subscription(self, new_subscription: Subscription) -> None:
        if new_subscription.price >= self.subscription.price:
            raise ValueError("New subscription must be less expensive than the current one")
        self.subscription = new_subscription

    def has_permission(self, permission: str) -> bool:
        return permission in self.subscription.permissions