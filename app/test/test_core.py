import pytest
import re

from app import Seance
from app.core_functions import set_seance_date, set_seance_hour

@pytest.fixture
def seance_correct():
    seance = Seance()
    seance.date = '2020-07-06 18:53:46'
    return seance


@pytest.fixture
def seance_incorrect():
    seance = Seance()
    seance.date = '20-07-2006 18:5346'
    return seance


def test_set_seance_date_passed(seance_correct):
    pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
    only_date = set_seance_date(seance_correct)
    assert re.match(pattern, only_date), 'Date should has patter dd.mm.yyyy.'


def test_set_seance_date_failed(seance_incorrect):
    pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
    only_date = set_seance_date(seance_incorrect)
    assert not re.match(pattern, only_date), 'Date with wrong pattern match.'


def test_set_seance_hour_passed(seance_correct):
    pattern = re.compile(r'\d\d:\d\d')
    only_hour = set_seance_hour(seance_correct)
    assert re.match(pattern, only_hour), 'Hour should has patter hh:mm:ss.'


def test_set_seance_hour_failed(seance_incorrect):
    pattern = re.compile(r'\d\d:\d\d')
    only_hour = set_seance_date(seance_incorrect)
    assert not re.match(pattern, only_hour), 'Hour with wrong pattern match.'