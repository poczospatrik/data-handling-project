from __future__ import annotations

import random
from dataclasses import field, dataclass
from typing import Type, cast

from faker import Faker
from faker_education import SchoolProvider


from data.project.base import Dataset, Entity


@dataclass
class EADataset(Dataset):
    people: list[Person]
    jobs: list[Job]
    schools: list[School]
    transactions: list[Transaction]

    @staticmethod
    def entity_types() -> list[Type[Entity]]:
        return [Person, Job, School, Transaction]

    @staticmethod
    def from_sequence(entities: list[list[Entity]]) -> Dataset:
        return EADataset(
            cast(list[Person], entities[0]),
            cast(list[Job], entities[1]),
            cast(list[School], entities[2]),
            cast(list[Transaction], entities[3])
        )

    def entities(self) -> dict[Type[Entity], list[Entity]]:
        res = dict()
        res[Person] = self.people
        res[Job] = self.jobs
        res[School] = self.schools
        res[Transaction] = self.transactions

        return res

    @staticmethod
    def generate(
            count_of_people: int,
            count_of_jobs: int,
            count_of_schools: int,
            count_of_transactions: int):

        def generate_people(n: int, male_ratio: float = 0.5, locale: str = "en_US",
                            unique: bool = False, min_age: int = 18, max_age: int = 80) -> list[Person]:
            """
            Generates people.
            """

            assert n > 0
            assert 0 <= male_ratio <= 1
            assert 0 <= min_age <= max_age

            fake = Faker(locale)
            people = []
            for i in range(n):
                male = random.random() < male_ratio
                generator = fake if not unique else fake.unique
                people.append(Person(
                    "P-" + (str(i).zfill(6)),
                    generator.name_male() if male else generator.name_female(),
                    random.randint(min_age, max_age)
                ))

            return people

        def generate_jobs(n: int, min_wage: int = 1000, max_wage: int = 9999) -> list[Job]:
            """
            Generates jobs.
            """
            assert n > 0
            assert min_wage >= 1000
            assert min_wage < max_wage

            fake = Faker()
            jobs = []

            for i in range(n):
                x1 = random.randint(min_wage, max_wage)
                x2 = random.randint(min_wage, max_wage)

                jobs.append(Job(
                    "J-" + (str(i).zfill(6)),
                    fake.job(),
                    x1 if x1 < x2 else x2,
                    x1 if x1 > x2 else x2
                ))
            return jobs

        def generate_schools(n: int) -> list[School]:
            """
            Generate schools.
            """

            assert n > 0

            fake = Faker()
            fake.add_provider(SchoolProvider)
            schools = []

            for i in range(n):
                schools.append(School(
                    "S-" + (str(i).zfill(6)),
                    fake.school_name(),
                    fake.school_district(),
                    fake.school_level(),
                    fake.school_state(),
                ))
            return schools

        def generate_transactions(n: int, people: list[Person], jobs: list[Job], schools: list[School]) -> list[
            Transaction]:
            """
            Generates transactions.
            """

            assert n > 0
            assert len(people) > 0
            assert len(jobs) > 0
            assert len(schools) > 0

            trips = []
            for i in range(n):
                person = random.choice(people)
                job = random.choice(jobs)
                school = random.choice(schools)
                trips.append(
                    Transaction(f"T-{str(i).zfill(6)}",school.school_id, person.person_id, job.job_id))

            return trips

        people = generate_people(count_of_people)
        jobs = generate_jobs(count_of_jobs)
        schools = generate_schools(count_of_schools)
        transactions = generate_transactions(count_of_transactions, people, jobs, schools)
        return EADataset(people, jobs, schools, transactions)


@dataclass
class Person(Entity):
    person_id: str = field(hash=True)
    person_name: str = field(repr=True, compare=False)
    age: int = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Person:
        return Person(seq[0], seq[1], int(seq[2]))

    def to_sequence(self) -> list[str]:
        return [self.person_id, self.person_name, str(self.age)]

    @staticmethod
    def field_names() -> list[str]:
        return ["person_id", "person_name", "age"]

    @staticmethod
    def collection_name() -> str:
        return "people"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Person.collection_name()} (
            PERSON_ID VARCHAR(8) PRIMARY KEY,
            PERSON_NAME VARCHAR(100),
            AGE NUMBER(3)
        )
        """


@dataclass
class Job(Entity):
    job_id: str = field(hash=True)
    job_name: str = field(repr=True, compare=False)
    min_wage: int = field(compare=False)
    max_wage: int = field(compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Job:
        return Job(seq[0], seq[1], int(seq[2]), int(seq[3]))

    def to_sequence(self) -> list[str]:
        return [self.job_id, self.job_name, self.min_wage, self.max_wage]

    @staticmethod
    def field_names() -> list[str]:
        return ["job_id", "job_name", "min_wage", "max_wage"]

    @staticmethod
    def collection_name() -> str:
        return "job"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Job.collection_name()} (
            JOB_ID VARCHAR(8) PRIMARY KEY,
            JOB_NAME VARCHAR(100),
            MIN_WAGE NUMBER(8),
            MAX_WAGE NUMBER(8)       
        )
        """


@dataclass
class School(Entity):
    school_id: str = field(hash=True)
    school_name: str = field(repr=True, compare=False)
    school_district: str = field(compare=False)
    school_level: str = field(compare=False)
    school_state: str = field(compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> School:
        return School(seq[0], seq[1], seq[2], seq[3], seq[4])

    def to_sequence(self) -> list[str]:
        return [self.school_id, self.school_name, self.school_district, self.school_level, self.school_state]

    @staticmethod
    def field_names() -> list[str]:
        return ["school_id", "school_name", "school_district", "school_level", "school_state"]

    @staticmethod
    def collection_name() -> str:
        return "school"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {School.collection_name()} (
            SCHOOL_ID VARCHAR(8) NOT NULL PRIMARY KEY,
            SCHOOL_NAME VARCHAR(150),
            SCHOOL_DISTRICT VARCHAR(150),
            SCHOOL_LEVEL VARCHAR(150),
            SCHOOL_STATE VARCHAR(150)
        )
        """


@dataclass
class Transaction(Entity):
    transaction_id: str = field(hash=True)
    school: str = field(repr=True, compare=False)
    person: str = field(repr=True, compare=False)
    job: str = field(repr=True, compare=False)

    @staticmethod
    def from_sequence(seq: list[str]) -> Transaction:
        return Transaction(seq[0], seq[1], seq[2], seq[3])

    def to_sequence(self) -> list[str]:
        return [self.transaction_id, self.school, self.person, self.job]

    @staticmethod
    def field_names() -> list[str]:
        return ["transaction_id", "school", "person", "job"]

    @staticmethod
    def collection_name() -> str:
        return "transactions"

    @staticmethod
    def create_table() -> str:
        return f"""
        CREATE TABLE {Transaction.collection_name()} (
            TRANSACTION_ID VARCHAR(8) NOT NULL PRIMARY KEY,
            SCHOOL VARCHAR(50) NOT NULL,
            PERSON VARCHAR(50) NOT NULL,
            JOB VARCHAR(50) NOT NULL,

            FOREIGN KEY (SCHOOL) REFERENCES {School.collection_name()}(SCHOOL_ID),
            FOREIGN KEY (PERSON) REFERENCES {Person.collection_name()}(PERSON_ID),
            FOREIGN KEY (JOB) REFERENCES {Job.collection_name()}(JOB_ID)
        )
         """