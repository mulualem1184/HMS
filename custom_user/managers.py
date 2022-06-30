from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):

    def create(self, *args, **kwargs):
        return self.create_user(*args, **kwargs)

    def create_user(self, first_name, last_name, phone_number, password, *args, **kwargs):
        if not all([ first_name, last_name, phone_number, password ]):
            raise ValueError("`first_name, last_name, phone_number and password` can not be null.")
        user = self.model(first_name=first_name, last_name=last_name,
            phone_number=phone_number, 
            *args, **kwargs,
        )
        user.set_password(password)
        user.save()
        return user 

    def create_superuser(self, phone_number, password, *args, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)

        if not kwargs.get('is_staff'):
            raise ValueError('is_staff must be set to true on a Superuser')
        if not kwargs.get('is_superuser'):
            raise ValueError('is_superuser must be set to true on a Superuser')
        
        return self.create_user(phone_number=phone_number, password=password, **kwargs)