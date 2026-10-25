# 🍽️ Amenity Food Prediction System

## 📌 Project Overview
The **Amenity Food Prediction System** is a web-based application designed to simplify food ordering and help administrators monitor food demand. It provides a user-friendly interface for customers to browse food items, manage their cart, place orders, and view bills.

The admin dashboard supports food menu management, order monitoring, and demand classification to help with food planning.

## ✨ Features

### 👤 Customer Module
- User registration and login
- Browse available food items
- Add items to the cart and manage quantities
- Place food orders
- Generate bills with 5% GST

### 🛠️ Admin Module
- Admin login
- Manage food menu items
- View and manage customer orders
- Monitor food demand using rule-based classification

## 🧰 Technologies Used
- **Backend:** Python, Flask
- **Database:** MongoDB
- **Frontend:** HTML, CSS, JavaScript
- **Tools:** Visual Studio Code, Git, GitHub

## 📂 Project Structure

```text
Amenity_food_prediction/
├── app.py
├── database.py
├── requirements.txt
├── amenity_dataset.csv
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── templates/
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/KANISHKA-EEE/Amenity_food_prediction.git
cd Amenity_food_prediction
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure MongoDB
Install and start MongoDB locally, or configure a MongoDB connection using environment variables. Do not publish database credentials or secret keys.

### 5. Run the application

```bash
python app.py
```

Open the local address displayed in the terminal in your web browser.

## 🎯 Project Objective
To simplify food ordering, improve order management, and support food-demand monitoring through a web application.

## 🚀 Future Enhancements
- Implement and evaluate a trained machine-learning model for food-demand prediction
- Add interactive demand analytics and visualizations
- Improve authentication and password security
- Deploy the application to a cloud platform

## 👩‍💻 Author
**Kanishka S**

Electrical and Electronics Engineering Student | Interested in AI, Software Development, and Cloud Technologies
