from django.db import models
from django.urls import reverse


class Address(models.Model):
    """
    Patient address.
    """

    street = models.CharField(max_length=100)
    number = models.CharField(max_length=10)
    apartment = models.CharField(max_length=10, null=True)
    zip_code = models.CharField(max_length=6)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Addresses"
    
    def address(self):
        """
        Full address.
        """

        apartment = '/' + self.apartment if self.apartment else ""
        street = f"{self.street} {self.number}{apartment}"
        full_address = f"{street} {self.zip_code} {self.city} {self.country}"
        return full_address
    
    def __str__(self):
        """
        Full address.
        """

        return self.address()


class Patient(models.Model):
    """
    Patient personal details.
    """

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    personal_id = models.CharField(max_length=11, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=10)
    address = models.OneToOneField(
        Address, on_delete=models.SET_NULL, null=True)


    def name(self):
        """
        Full name.
        """

        return f"{self.first_name} {self.last_name}"
    

    def __str__(self):
        """
        Full name.
        """
        
        return self.name()

    def get_absolute_url(self):
        return reverse("patients:patient", args=[self.id])
