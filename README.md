# 🏦 Banking Management System (Python + MySQL)

A fully functional **command-line Banking Management System** built with **Python** and **MySQL**, featuring account management, transaction handling, and secure data storage.

This project automatically handles **database creation**, **table creation**, and provides a clean set of banking operations like deposit, withdrawal, balance check, and history tracking.

---

## 🚀 Features

### 🧾 **Account Management**

* Create new bank accounts
* View all accounts
* Unique auto-increment account numbers
* Stores account holder info, balance & timestamps

### 💰 **Transaction Features**

| Feature                | Description                                  |
| ---------------------- | -------------------------------------------- |
| ➕ Deposit Money        | Add funds to an account                      |
| ➖ Withdraw Money       | Validates balance before withdrawal          |
| 👀 Check Balance       | Fetch latest balance instantly               |
| 📜 Transaction History | Shows deposits & withdrawals with timestamps |

### 🛠️ **Technical Features**

* Automatic MySQL database creation
* Automatic table creation (`accounts`, `transactions`)
* Safe SQL operations with error handling
* Input validation for all operations
* Graceful exit on errors or keyboard interrupt

---

## 📂 Database Structure

### **Database:** `bank_db`

### **Table: accounts**

```sql
CREATE TABLE accounts (
    account_number INT AUTO_INCREMENT PRIMARY KEY,
    holder_name VARCHAR(100) NOT NULL,
    balance DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Table: transactions**

```sql
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_number INT,
    type VARCHAR(20),
    amount DECIMAL(10,2),
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
);
```

---

## 🛠️ Installation & Setup

### **1️⃣ Install Required Package**

```bash
pip install mysql-connector-python
```

### **2️⃣ Ensure MySQL Server Is Running**

The program attempts common default credentials:

* `root` / *(empty password)*
* `root` / `root`

If those fail, it will ask you to enter credentials manually.

### **3️⃣ Run the Program**

```bash
python main.py
```

---

## 📸 Menu Preview

```
==============================================
🏦 BANKING SYSTEM
==============================================
1. ➕ Create Account
2. 💰 Deposit Money
3. 💸 Withdraw Money
4. 👀 View Balance
5. 📜 View Transaction History
6. 👥 View All Accounts
7. 🚪 Exit
==============================================
```

---

## 📦 Project Structure

```
banking-management/
│
├── main.py            # Main application
├── README.md          # Project documentation
└── requirements.txt   # Optional dependencies
```

---

## 📄 Optional: requirements.txt

```
mysql-connector-python
```





---

## 👨‍💻 Author

**Mahima**
Python + MySQL Development Project

---

