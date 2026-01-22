"""
Database module for the AI Booking Assistant.
Handles SQLite operations for customers and bookings.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

DB_PATH = "booking_assistant.db"


def initialize_db():
    """Initialize the SQLite database with required tables."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Create customers table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                phone TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create bookings table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                booking_type TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT DEFAULT 'confirmed',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
            """
        )

        conn.commit()
        logger.info("Database initialized successfully.")
    except sqlite3.Error as e:
        logger.error(f"Database initialization error: {e}")
        raise
    finally:
        conn.close()


def get_or_create_customer(name: str, email: str, phone: str) -> int:
    """Get existing customer by email or create new one. Returns customer_id."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Check if customer exists
        cursor.execute("SELECT customer_id FROM customers WHERE email = ?", (email,))
        result = cursor.fetchone()

        if result:
            return result[0]

        # Create new customer
        cursor.execute(
            "INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)",
            (name, email, phone),
        )
        conn.commit()
        customer_id = cursor.lastrowid
        logger.info(f"Customer created: {email} (ID: {customer_id})")
        return customer_id

    except sqlite3.Error as e:
        logger.error(f"Error getting/creating customer: {e}")
        raise
    finally:
        conn.close()


def save_booking(
    customer_id: int, booking_type: str, date: str, time: str
) -> int:
    """Save a booking to the database. Returns booking ID."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO bookings (customer_id, booking_type, date, time, status)
            VALUES (?, ?, ?, ?, 'confirmed')
            """,
            (customer_id, booking_type, date, time),
        )
        conn.commit()
        booking_id = cursor.lastrowid
        logger.info(f"Booking saved: ID {booking_id} for customer {customer_id}")
        return booking_id

    except sqlite3.Error as e:
        logger.error(f"Error saving booking: {e}")
        raise
    finally:
        conn.close()


def get_all_bookings() -> List[Dict]:
    """Retrieve all bookings with customer information."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                b.id,
                c.name,
                c.email,
                c.phone,
                b.booking_type,
                b.date,
                b.time,
                b.status,
                b.created_at
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            ORDER BY b.created_at DESC
            """
        )

        rows = cursor.fetchall()
        bookings = [dict(row) for row in rows]
        return bookings

    except sqlite3.Error as e:
        logger.error(f"Error retrieving bookings: {e}")
        raise
    finally:
        conn.close()


def search_bookings(email: str = "", date: str = "") -> List[Dict]:
    """Search bookings by email and/or date."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        query = """
            SELECT 
                b.id,
                c.name,
                c.email,
                c.phone,
                b.booking_type,
                b.date,
                b.time,
                b.status,
                b.created_at
            FROM bookings b
            JOIN customers c ON b.customer_id = c.customer_id
            WHERE 1=1
        """
        params = []

        if email:
            query += " AND c.email LIKE ?"
            params.append(f"%{email}%")

        if date:
            query += " AND b.date = ?"
            params.append(date)

        query += " ORDER BY b.created_at DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        bookings = [dict(row) for row in rows]
        return bookings

    except sqlite3.Error as e:
        logger.error(f"Error searching bookings: {e}")
        raise
    finally:
        conn.close()


def get_customer_by_email(email: str) -> Optional[Dict]:
    """Get customer details by email."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM customers WHERE email = ?", (email,))
        row = cursor.fetchone()

        if row:
            return dict(row)
        return None

    except sqlite3.Error as e:
        logger.error(f"Error retrieving customer: {e}")
        raise
    finally:
        conn.close()
