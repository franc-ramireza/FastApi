import pytest


def test_equal_or_not_equal():
    assert 3 == 3
    assert 3 != 1

def test_is_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)

def test_boolean():
    validated = True
    assert validated is True
    assert ('hello' == 'world') is False

def test_type ():
    assert type ('hello' is str)
    assert type ('world' is not int)

def test_list():
    num_list = [1, 2, 3 , 4 , 5]
    any_list = [True, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all not in any_list

class Student:
    def __init__(self, first_name: str , last_name : str , major: str , years : int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years

@pytest.fixture
def default_employee():
    return Student('john', 'doe', 'computer science', 3)


def test_person_initializacion(default_employee):
    assert default_employee.first_name == 'john', 'first name should be john'
    assert default_employee.last_name == 'doe', 'last name should be doe'
    assert default_employee.major == 'computer science', 'major should be computer science'
    assert default_employee.years == 3