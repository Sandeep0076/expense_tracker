from dataclasses import dataclass
from datetime import datetime

@dataclass
class Transaction:
    id: int
    amount: float
    category: str
    date: datetime
    type: str

@dataclass
class Balance:
    amount: float

@dataclass
class Loan:
    amount: float

@dataclass
class Savings:
    amount: float