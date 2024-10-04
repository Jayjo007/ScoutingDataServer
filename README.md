# Scouting Data Server

This is a Flask application designed for handling scouting data for FIRST Robotics Competition teams. 

## Table of Contents

- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Technologies Used

- **Flask**: A micro web framework for Python.
- **MySQL**: Relational database management system for data storage.
- **SQLAlchemy**: ORM for database interaction.
- **Flask-SQLAlchemy**: Flask extension for SQLAlchemy.
- **WTForms**: Flexible forms for web applications.

## Installation

To run this application, you need to have Python and MySQL installed on your system.

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/your-flask-app.git
   cd your-flask-app
   ```

2. **Set up a virtual environment (optional but recommended)**:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**:

   Ensure you have `requirements.txt` in your project directory. Run:

   ```bash
   pip install -r requirements.txt
   ```

   The application depends on the following packages:

   - `Flask`: A micro web framework.
   - `Flask-SQLAlchemy`: Flask extension for SQLAlchemy.
   - `SQLAlchemy`: SQL toolkit and ORM.
   - `PyMySQL`: MySQL client for Python.
   - `WTForms`: Library for creating web forms.
   - Additional libraries such as `requests`, `Werkzeug`, and `Jinja2`.

4. **Install MySQL**:

   Follow the installation instructions for your platform:

   - **Windows**: Download and install MySQL from [MySQL Installer](https://dev.mysql.com/downloads/installer/).
   - **macOS**: Install MySQL using Homebrew:

     ```bash
     brew install mysql
     ```
   - **Linux**: Use your package manager to install MySQL. For example, on Ubuntu:

     ```bash
     sudo apt-get update
     sudo apt-get install mysql-server
     ```

## Configuration

1. **Set up your MySQL database**:
   
   - Create a database for your application:

     ```sql
     CREATE DATABASE your_database_name;
     ```

   - Update your database connection settings in the application configuration file (`.env`).

2. **Start the Flask server**:

   You can run the application using:

   ```bash
   py app.py
   ```

   By default, the server will be available at [http://127.0.0.1:5000](http://127.0.0.1:5000) or [localhost:5000](localhost:5000).

2. **Access the application**:
   
   Open your web browser and go to [http://127.0.0.1:5000](http://127.0.0.1:5000) to view the application.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/YourFeature`).
3. Make your changes and commit them (`git commit -m 'Add some feature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
