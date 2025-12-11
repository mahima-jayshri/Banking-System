import mysql.connector
from mysql.connector import Error
import datetime
import sys
import os

class BankingSystem:
    def __init__(self):
        """Initialize database connection with configurable credentials"""
        self.connection = None
        self.db_config = self.get_database_config()
        self.connect_to_database()
    
    def get_database_config(self):
        """Get database configuration from user or use defaults"""
        print("\n" + "="*60)
        print("DATABASE CONFIGURATION")
        print("="*60)
        
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'banking_system')
        
        configure = input("Do you want to configure database settings? (y/n, default=n): ").strip().lower()
        
        if configure == 'y':
            print("\nEnter database configuration (press Enter for defaults):")
            host = input(f"Host [{host}]: ").strip() or host
            user = input(f"Username [{user}]: ").strip() or user
            password = input(f"Password [{'*' * len(password) if password else 'empty'}]: ").strip() or password
            database = input(f"Database name [{database}]: ").strip() or database
        
        return {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
    
    def test_connection(self, config):
        """Test database connection with given configuration"""
        try:
            test_conn = mysql.connector.connect(
                host=config['host'],
                user=config['user'],
                password=config['password']
            )
            if test_conn.is_connected():
                test_conn.close()
                return True
        except Error as e:
            print(f"Connection test failed: {e}")
            return False
    
    def connect_to_database(self):
        """Establish connection to MySQL database with error handling"""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                print(f"\nAttempt {attempt + 1} of {max_attempts} to connect to database...")
                
                # First try without database to check credentials
                test_conn = mysql.connector.connect(
                    host=self.db_config['host'],
                    user=self.db_config['user'],
                    password=self.db_config['password']
                )
                
                if test_conn.is_connected():
                    print("✓ Connected to MySQL server successfully")
                    
                    # Create database if it doesn't exist
                    cursor = test_conn.cursor()
                    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db_config['database']}")
                    cursor.execute(f"USE {self.db_config['database']}")
                    test_conn.close()
                    
                    # Now connect to the specific database
                    self.connection = mysql.connector.connect(
                        host=self.db_config['host'],
                        user=self.db_config['user'],
                        password=self.db_config['password'],
                        database=self.db_config['database']
                    )
                    
                    if self.connection.is_connected():
                        print(f"✓ Connected to database '{self.db_config['database']}' successfully")
                        self.setup_database()
                        return
                        
            except Error as e:
                print(f"✗ Connection attempt {attempt + 1} failed: {e}")
                
                if attempt < max_attempts - 1:
                    print("\nPlease check your MySQL credentials:")
                    print(f"1. Make sure MySQL is running")
                    print(f"2. Check username and password")
                    print(f"3. Try using default credentials (username: root, password: empty)")
                    
                    retry = input("\nDo you want to reconfigure database settings? (y/n): ").strip().lower()
                    if retry == 'y':
                        self.db_config = self.get_database_config()
                    else:
                        print("Using current configuration for next attempt...")
                else:
                    print("\n" + "="*60)
                    print("CONNECTION FAILED - TROUBLESHOOTING STEPS:")
                    print("="*60)
                    print("1. Check if MySQL service is running:")
                    print("   Windows: Open Services (services.msc) and start MySQL")
                    print("   Or run: net start mysql")
                    print("\n2. Common default credentials:")
                    print("   Username: root")
                    print("   Password: (empty), 'root', or the password you set during installation")
                    print("\n3. If you forgot your password:")
                    print("   - Stop MySQL service")
                    print("   - Start MySQL with --skip-grant-tables option")
                    print("   - Reset password using: ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';")
                    print("\n4. Install MySQL if not installed:")
                    print("   Download from: https://dev.mysql.com/downloads/installer/")
                    print("="*60)
                    
                    sys.exit(1)
    
    def setup_database(self):
        """Create database and tables if they don't exist"""
        cursor = self.connection.cursor()
        
       
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id INT AUTO_INCREMENT PRIMARY KEY,
                account_number VARCHAR(20) UNIQUE NOT NULL,
                account_holder VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                phone VARCHAR(20),
                address TEXT,
                balance DECIMAL(15, 2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status ENUM('active', 'inactive', 'suspended') DEFAULT 'active'
            )
        """)
        
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INT AUTO_INCREMENT PRIMARY KEY,
                account_id INT NOT NULL,
                transaction_type ENUM('deposit', 'withdrawal', 'transfer', 'account_creation') NOT NULL,
                amount DECIMAL(15, 2) NOT NULL,
                description VARCHAR(255),
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE
            )
        """)
        
        self.connection.commit()
        cursor.close()
        print("✓ Database tables created/verified successfully")
    
    def generate_account_number(self):
        """Generate a unique 10-digit account number"""
        cursor = self.connection.cursor()
        while True:
            import random
            account_number = str(random.randint(1000000000, 9999999999))
            
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE account_number = %s", (account_number,))
            if cursor.fetchone()[0] == 0:
                cursor.close()
                return account_number
    
    def create_account(self):
        """Create a new bank account"""
        print("\n" + "="*50)
        print("CREATE NEW ACCOUNT")
        print("="*50)
        
        account_holder = input("Enter account holder name: ").strip()
        if not account_holder:
            print("Account holder name is required!")
            return
        
        email = input("Enter email address: ").strip()
        phone = input("Enter phone number: ").strip()
        address = input("Enter address: ").strip()
        
        account_number = self.generate_account_number()
        
        while True:
            try:
                initial_deposit = float(input("Enter initial deposit amount: $"))
                if initial_deposit < 0:
                    print("Initial deposit cannot be negative.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                INSERT INTO accounts (account_number, account_holder, email, phone, address, balance)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (account_number, account_holder, email, phone, address, initial_deposit))
            
            account_id = cursor.lastrowid
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, amount, description)
                VALUES (%s, 'account_creation', %s, 'Initial deposit - Account creation')
            """, (account_id, initial_deposit))
            
            self.connection.commit()
            
            print(f"\n✓ Account created successfully!")
            print(f"   Account Number: {account_number}")
            print(f"   Account Holder: {account_holder}")
            print(f"   Initial Balance: ${initial_deposit:.2f}")
            
        except Error as e:
            print(f"✗ Error creating account: {e}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def get_account_id(self, account_number):
        """Get account ID from account number"""
        cursor = self.connection.cursor()
        cursor.execute("SELECT account_id FROM accounts WHERE account_number = %s", (account_number,))
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
    
    def deposit_money(self):
        """Deposit money into an account"""
        print("\n" + "="*50)
        print("DEPOSIT MONEY")
        print("="*50)
        
        account_number = input("Enter account number: ").strip()
        account_id = self.get_account_id(account_number)
        
        if not account_id:
            print("✗ Account not found!")
            return
        
        while True:
            try:
                amount = float(input("Enter deposit amount: $"))
                if amount <= 0:
                    print("Deposit amount must be positive.")
                    continue
                break
            except ValueError:
                print("Please enter a valid number.")
        
        description = input("Enter deposit description (optional): ").strip()
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("""
                UPDATE accounts 
                SET balance = balance + %s 
                WHERE account_id = %s
            """, (amount, account_id))
            
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, amount, description)
                VALUES (%s, 'deposit', %s, %s)
            """, (account_id, amount, description or "Cash deposit"))
            
            self.connection.commit()
            
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
            balance = cursor.fetchone()[0]
            
            print(f"\n✓ Deposit successful!")
            print(f"   Amount deposited: ${amount:.2f}")
            print(f"   New balance: ${balance:.2f}")
            
        except Error as e:
            print(f"✗ Error processing deposit: {e}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def withdraw_money(self):
        """Withdraw money from an account"""
        print("\n" + "="*50)
        print("WITHDRAW MONEY")
        print("="*50)
        
        account_number = input("Enter account number: ").strip()
        account_id = self.get_account_id(account_number)
        
        if not account_id:
            print("✗ Account not found!")
            return
        
        cursor = self.connection.cursor()
        cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
        balance = cursor.fetchone()[0]
        
        print(f"Current balance: ${balance:.2f}")
        
        while True:
            try:
                amount = float(input("Enter withdrawal amount: $"))
                if amount <= 0:
                    print("Withdrawal amount must be positive.")
                    continue
                if amount > balance:
                    print("✗ Insufficient funds!")
                    return
                break
            except ValueError:
                print("Please enter a valid number.")
        
        description = input("Enter withdrawal description (optional): ").strip()
        
        try:
            cursor.execute("""
                UPDATE accounts 
                SET balance = balance - %s 
                WHERE account_id = %s
            """, (amount, account_id))
            
            cursor.execute("""
                INSERT INTO transactions (account_id, transaction_type, amount, description)
                VALUES (%s, 'withdrawal', %s, %s)
            """, (account_id, amount, description or "Cash withdrawal"))
            
            self.connection.commit()
            
            cursor.execute("SELECT balance FROM accounts WHERE account_id = %s", (account_id,))
            new_balance = cursor.fetchone()[0]
            
            print(f"\n✓ Withdrawal successful!")
            print(f"   Amount withdrawn: ${amount:.2f}")
            print(f"   New balance: ${new_balance:.2f}")
            
        except Error as e:
            print(f"✗ Error processing withdrawal: {e}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def view_balance(self):
        """View account balance"""
        print("\n" + "="*50)
        print("VIEW ACCOUNT BALANCE")
        print("="*50)
        
        account_number = input("Enter account number: ").strip()
        
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT account_number, account_holder, balance, status 
            FROM accounts 
            WHERE account_number = %s
        """, (account_number,))
        
        account = cursor.fetchone()
        cursor.close()
        
        if account:
            print(f"\nAccount Number: {account['account_number']}")
            print(f"Account Holder: {account['account_holder']}")
            print(f"Account Status: {account['status']}")
            print(f"Current Balance: ${account['balance']:.2f}")
        else:
            print("✗ Account not found!")
    
    def view_transaction_history(self):
        """View transaction history for an account"""
        print("\n" + "="*50)
        print("TRANSACTION HISTORY")
        print("="*50)
        
        account_number = input("Enter account number: ").strip()
        account_id = self.get_account_id(account_number)
        
        if not account_id:
            print("✗ Account not found!")
            return
        
        limit = 10
        try:
            limit_input = input("Enter number of transactions to display (default 10, 'all' for all): ").strip()
            if limit_input.lower() == 'all':
                limit = None
            elif limit_input:
                limit = int(limit_input)
        except ValueError:
            print("Using default limit of 10 transactions")
            limit = 10
        
        cursor = self.connection.cursor(dictionary=True)
        
        if limit:
            cursor.execute("""
                SELECT transaction_type, amount, description, transaction_date
                FROM transactions
                WHERE account_id = %s
                ORDER BY transaction_date DESC
                LIMIT %s
            """, (account_id, limit))
        else:
            cursor.execute("""
                SELECT transaction_type, amount, description, transaction_date
                FROM transactions
                WHERE account_id = %s
                ORDER BY transaction_date DESC
            """, (account_id,))
        
        transactions = cursor.fetchall()
        
        cursor.execute("SELECT account_holder FROM accounts WHERE account_id = %s", (account_id,))
        account_holder = cursor.fetchone()['account_holder']
        cursor.close()
        
        print(f"\nTransaction History for: {account_holder}")
        print(f"Account Number: {account_number}")
        print("-"*80)
        
        if not transactions:
            print("No transactions found.")
            return
        
        print(f"{'Date':<20} {'Type':<15} {'Amount':<15} {'Description':<30}")
        print("-"*80)
        
        total_deposits = 0
        total_withdrawals = 0
        
        for trans in transactions:
            date_str = trans['transaction_date'].strftime("%Y-%m-%d %H:%M:%S")
            trans_type = trans['transaction_type'].upper()
            amount = trans['amount']
            description = trans['description'] or ""
            
            if trans_type in ['DEPOSIT', 'ACCOUNT_CREATION']:
                total_deposits += amount
            elif trans_type == 'WITHDRAWAL':
                total_withdrawals += amount
            
            print(f"{date_str:<20} {trans_type:<15} ${amount:<14.2f} {description:<30}")
        
        print("-"*80)
        print(f"Total Deposits: ${total_deposits:.2f}")
        print(f"Total Withdrawals: ${total_withdrawals:.2f}")
        print(f"Net Change: ${(total_deposits - total_withdrawals):.2f}")
    
    def view_all_accounts(self):
        """View all accounts (admin function)"""
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT account_number, account_holder, balance, status, created_at
            FROM accounts
            ORDER BY created_at DESC
        """)
        
        accounts = cursor.fetchall()
        cursor.close()
        
        print("\n" + "="*80)
        print("ALL ACCOUNTS")
        print("="*80)
        
        if not accounts:
            print("No accounts found.")
            return
        
        print(f"{'Account No.':<15} {'Holder':<25} {'Balance':<15} {'Status':<12} {'Created On':<20}")
        print("-"*80)
        
        total_balance = 0
        for account in accounts:
            created_date = account['created_at'].strftime("%Y-%m-%d")
            print(f"{account['account_number']:<15} {account['account_holder']:<25} "
                  f"${account['balance']:<14.2f} {account['status']:<12} {created_date:<20}")
            total_balance += account['balance']
        
        print("-"*80)
        print(f"Total Accounts: {len(accounts)}")
        print(f"Total Bank Balance: ${total_balance:.2f}")
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("\nDatabase connection closed.")
    
    def display_menu(self):
        """Display main menu"""
        print("\n" + "="*50)
        print("BANKING SYSTEM MANAGEMENT")
        print("="*50)
        print("1. Create New Account")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. View Account Balance")
        print("5. View Transaction History")
        print("6. View All Accounts (Admin)")
        print("7. Exit")
        print("="*50)

def main():
    """Main function to run the banking system"""
    print("\n" + "="*60)
    print("BANKING SYSTEM")
    print("="*60)
    
    try:
        bank = BankingSystem()
        
        while True:
            bank.display_menu()
            
            choice = input("\nEnter your choice (1-7): ").strip()
            
            if choice == '1':
                bank.create_account()
            elif choice == '2':
                bank.deposit_money()
            elif choice == '3':
                bank.withdraw_money()
            elif choice == '4':
                bank.view_balance()
            elif choice == '5':
                bank.view_transaction_history()
            elif choice == '6':
                bank.view_all_accounts()
            elif choice == '7':
                print("\nThank you for using the Banking System. Goodbye!")
                break
            else:
                print("Invalid choice! Please enter a number between 1 and 7.")
            
            input("\nPress Enter to continue...")
        
        bank.close_connection()
        
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()