# Padel-Court-Reservations-System
Padel Court Reservations is a Django-based web application for managing reservations at padel courts. It allows users to sign up, log in, view locations, create new reservations, manage account information, and more.

## Features

- **User Authentication:** Sign up, log in, and log out functionalities.
- **Reservation Management:** Create new reservations, view upcoming and past reservations, cancel reservations.
- **Location Information:** View available padel court locations.
- **Email Notifications:** Send confirmation and cancellation emails for reservations.
- **Responsive Design:** Built using Bootstrap for a mobile-friendly experience.

## Installation
1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/padel-court-reservations.git
   ```

2. Navigate into the project directory:
   ```bash
   cd padel-court-reservations
   ```

3. Install dependencies:
   ```bash
   pipenv install
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```
   
5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage
- Navigate to the homepage to sign up or log in.
- View available locations
- Create new reservations by selecting a location, court, date, and time.
- Manage account settings and view past and upcoming reservations
