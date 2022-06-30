from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()

class UserManagersTest(TestCase):

    def setUp(self) -> None:
        self.phone_number = '0123456789'
        self.password = 'test_password'
        self.first_name = 'test_fname'
        self.last_name = 'test_lname'

    def test_create_user(self):
        user = User.objects.create_user(first_name=self.first_name, last_name=self.last_name,
            phone_number=self.phone_number, password=self.password
        )
        self.assertEqual(user.phone_number, self.phone_number)
        self.assertEqual(user.first_name, self.first_name)
        self.assertEqual(user.last_name, self.last_name)
        self.assertTrue(user.check_password(self.password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertIsNone(user.username)
        with self.assertRaises(TypeError):
            User.objects.create_user()
        with self.assertRaises(ValueError):
            User.objects.create_user('','','','')

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(first_name=self.first_name, last_name=self.last_name,
            phone_number=self.phone_number, password=self.password
        )
        self.assertEqual(superuser.phone_number, self.phone_number)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_staff)
        self.assertIsNone(superuser.username)
        with self.assertRaises(ValueError, msg="is_superuser can not be set to False while creating superuser"):
            User.objects.create_superuser(first_name=self.first_name, last_name=self.last_name, 
                phone_number=self.phone_number, password=self.password, 
                is_superuser=False
            )
        with self.assertRaises(ValueError, msg="is_staff can not be set to False while creating superuser"):
            User.objects.create_superuser(first_name=self.first_name, last_name=self.last_name, 
                phone_number=self.phone_number, password=self.password, 
                is_staff=False
            )
        
