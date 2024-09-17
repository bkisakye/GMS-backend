from django.db import models

from subgrantees.models import SubgranteeProfile

# Create your models here.

class FinancialInformation(models.Model):
    subgrantee_profile = models.ForeignKey(SubgranteeProfile, on_delete=models.CASCADE)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    funding_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Additional fields as necessary
    
    def __str__(self):
        return f"Financial Information for {self.subgrantee_profile}"

