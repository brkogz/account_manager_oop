# OOP Trade Account Management System

This is a clean, modular **Python OOP (Object-Oriented Programming)** project developed to simulate a multi-account trading system. It supports Crypto, Forex, and BIST accounts and allows centralized management via a core account manager.

The project applies core object-oriented principles:

- Abstraction
- Encapsulation
- Inheritance
- Polymorphism

It is designed to be **extendable and production-ready** for future integration with real APIs and trading logic.

---

## Features

- Abstract base class: `Account`
- Concrete subclasses:
  - `CryptoAccount`
  - `ForexAccount`
  - `BistAccount`
- Central `AccountManager` to:
  - Add / remove accounts
  - List all accounts
  - Calculate total portfolio value (converted to USD)
- Real-time USD/TRY exchange rate via `yfinance`
- Modular, clean codebase – easy to expand and maintain

---

## Tech Stack

- Python 3.12
- `yfinance` (for currency data)

---

## Project Structure

```

oop\_trade/
├── account\_manager\_oop.py     # Core class definitions and example usage
└── requirements.txt           # Dependencies

````

---

## How to Run

```bash
# Clone the repository
git clone https://github.com/yourusername/account_manager_oop.git
cd account_manager_oop

# Install dependencies
pip install -r requirements.txt

# Run the project
python account_manager_oop.py
````

---

## Sample Output

```
=== Accounts ===
CryptoAccount(broker_name='Binance', account_number='C123456', balance=5000.0 USDT, level='Prime')
ForexAccount(broker_name='ICMarkets', account_number='F654321', balance=12000.0 USD, level='Standard')
BistAccount(broker_name='A1 Capital', account_number='B987654', balance=75000.0 TRY, level='VIP')
Fetched USD/TRY rate: 40.24

Total Balance: 18863.80 USD
```

---

## Potential Extensions

* API integration for real-time trading (Binance, MetaTrader)
* SQLite / PostgreSQL database support
* GUI with Streamlit or Flask
* Multi-currency portfolio support

---

## About the Developer

Hi, I’m **Berk**, a Computer Engineering graduate working on Python-based trading and automation tools.
This project is part of my development process to build scalable and modular financial systems.

[GitHub – @brkogz](https://github.com/brkogz)

---

## Purpose

This project was developed to **solidify OOP knowledge** in Python and to build a **modular foundation** for future trading-related applications.
It is intended to be extended with real-time APIs, trading logic, and production-level features.

```
