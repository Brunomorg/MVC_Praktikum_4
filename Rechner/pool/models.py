from django.db import models
from django.db.models import Sum

# Database entry for topics.
class Topic(models.Model):
    title = models.CharField(max_length=200)

    class Meta:
        db_table = 'pool_thema'

    def __str__(self):
        return self.title
   


# Database entry for a person.
class Person(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='people')
    name = models.CharField(max_length=100)

    # Show the person's name.
    def __str__(self):
        return self.name

    def total_expenses(self):
        total = self.expenses.filter(topic=self.topic).aggregate(Sum('amount'))['amount__sum']
        return float(total) if total is not None else 0.0

    def calculate_balance(self, per_person_share):
        return round(self.total_expenses() - per_person_share, 2)


# Database entry for expenses.
class Expense(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='expenses')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='expenses')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True) 
    class Meta:
        db_table = 'pool_ausgabe'

    # Show the description of the expense.
    def __str__(self):
        return f"{self.person.name}: {self.amount} € for {self.description}"