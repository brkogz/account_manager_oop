from abc import ABC, abstractmethod
import yfinance as yf

class Account(ABC):
    """
    Abstract base class representing a generic financial account.
    Enforces a common interface for all account types.
    """

    @property
    @abstractmethod
    def broker_name(self):
        """Return the name of the broker."""
        pass

    @property
    @abstractmethod
    def account_number(self):
        """Return the account number."""
        pass

    @property
    @abstractmethod
    def account_balance(self):
        """Return the current balance of the account."""
        pass

    @property
    @abstractmethod
    def account_currency(self):
        """Return the currency in which the account operates."""
        pass

    @property
    @abstractmethod
    def account_level(self):
        """Return the account level or tier."""
        pass


class CryptoAccount(Account):
    """
    Represents a cryptocurrency trading account.
    Implements the Account interface.
    """
    account_type = 'Crypto'

    def __init__(self, broker_name, account_number, account_balance, account_currency, account_level):
        self._broker_name = broker_name
        self._account_number = account_number
        self._account_balance = account_balance
        self._account_currency = account_currency
        self._account_level = account_level

    @property
    def broker_name(self):
        return self._broker_name

    @property
    def account_number(self):
        return self._account_number

    @property
    def account_balance(self):
        return self._account_balance

    @property
    def account_currency(self):
        return self._account_currency

    @property
    def account_level(self):
        return self._account_level

    def __repr__(self):
        return (f"{self.account_type}Account("
                f"broker_name='{self.broker_name}', "
                f"account_number='{self.account_number}', "
                f"balance={self.account_balance} {self.account_currency}, "
                f"level='{self.account_level}')")


class ForexAccount(Account):
    """
    Represents a forex trading account.
    Implements the Account interface.
    """
    account_type = 'Forex'

    def __init__(self, broker_name, account_number, account_balance, account_currency, account_level):
        self._broker_name = broker_name
        self._account_number = account_number
        self._account_balance = account_balance
        self._account_currency = account_currency
        self._account_level = account_level

    @property
    def broker_name(self):
        return self._broker_name

    @property
    def account_number(self):
        return self._account_number

    @property
    def account_balance(self):
        return self._account_balance

    @property
    def account_currency(self):
        return self._account_currency

    @property
    def account_level(self):
        return self._account_level

    def __repr__(self):
        return (f"{self.account_type}Account("
                f"broker_name='{self.broker_name}', "
                f"account_number='{self.account_number}', "
                f"balance={self.account_balance} {self.account_currency}, "
                f"level='{self.account_level}')")


class BistAccount(Account):
    """
    Represents a BIST (Turkish stock exchange) trading account.
    Implements the Account interface.
    """
    account_type = 'Bist'

    def __init__(self, broker_name, account_number, account_balance, account_currency, account_level):
        self._broker_name = broker_name
        self._account_number = account_number
        self._account_balance = account_balance
        self._account_currency = account_currency
        self._account_level = account_level

    @property
    def broker_name(self):
        return self._broker_name

    @property
    def account_number(self):
        return self._account_number

    @property
    def account_balance(self):
        return self._account_balance

    @property
    def account_currency(self):
        return self._account_currency

    @property
    def account_level(self):
        return self._account_level

    def __repr__(self):
        return (f"{self.account_type}Account("
                f"broker_name='{self.broker_name}', "
                f"account_number='{self.account_number}', "
                f"balance={self.account_balance} {self.account_currency}, "
                f"level='{self.account_level}')")


class AccountManager:
    """
    Manages a collection of various Account objects (crypto, forex, bist).
    Provides methods to add, remove, list accounts and calculate total balance.
    """

    def __init__(self):
        self._accounts = []

    def add_account(self, account):
        """Add an account to the manager."""
        self._accounts.append(account)

    def remove_account(self, account):
        """Remove an account from the manager."""
        self._accounts.remove(account)

    def list_accounts(self):
        """Print all accounts managed by this manager."""
        for account in self._accounts:
            print(account)

    @staticmethod
    def get_usd_try_rate():
        """
        Fetch the current USD/TRY exchange rate from Yahoo Finance.
        Returns:
            float: latest USD/TRY price
        """
        ticker = yf.Ticker("USDTRY=X")
        last_price = ticker.history(period="1d")["Close"].iloc[-1]
        return last_price

    def total_balance(self):
        """
        Calculate the total balance in USD.
        Converts TRY balances using the fetched USD/TRY rate.
        Assumes USDT and USD are equivalent to USD.
        """
        usd_try_rate = self.get_usd_try_rate()
        print(f"Fetched USD/TRY rate: {usd_try_rate:.2f}")

        total = 0
        for account in self._accounts:
            if account.account_currency == "TRY":
                # Convert TRY balance to USD
                total += account.account_balance / usd_try_rate
            else:
                # USD or USDT, add directly
                total += account.account_balance
        return total


# Example usage:

# Create individual account objects
binance_acc = CryptoAccount(
    broker_name="Binance",
    account_number="C123456",
    account_balance=5000.0,
    account_currency="USDT",
    account_level="Prime"
)

icmarkets_acc = ForexAccount(
    broker_name="ICMarkets",
    account_number="F654321",
    account_balance=12000.0,
    account_currency="USD",
    account_level="Standard"
)

a1capital_acc = BistAccount(
    broker_name="A1 Capital",
    account_number="B987654",
    account_balance=75000.0,
    account_currency="TRY",
    account_level="VIP"
)

# Manage accounts via AccountManager
manager = AccountManager()
manager.add_account(binance_acc)
manager.add_account(icmarkets_acc)
manager.add_account(a1capital_acc)

# Display accounts
print("=== Accounts ===")
manager.list_accounts()

# Compute total balance
print("\nTotal Balance:", manager.total_balance())













