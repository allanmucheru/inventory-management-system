# Inventory Management System with OpenFoodFacts API Integration

A Flask RESTful API and interactive CLI administration portal designed for small retail inventory management. Features full CRUD operations, query-based search routes, real-time product lookup via the OpenFoodFacts API, and automated testing.

## Features
- **Flask REST API**: Supports CRUD actions (`GET`, `POST`, `PATCH`, `DELETE`).
- **Helper Search Route**: Endpoint to query inventory by product name or category.
- **External API Integration**: Fetch real-time product data using barcodes from OpenFoodFacts and auto-populate the database array.
- **CLI Admin Portal**: Interactive terminal client for managing inventory actions.
- **Unit Test Suite**: Automated unit tests using `pytest` with mocked external API requests.

## Project Directory
