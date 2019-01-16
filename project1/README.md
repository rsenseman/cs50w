# Project 1: Robert's Book Emporium

For this project, I created a simple website to let users leave reviews on a set of books. Users must login to use the site and may leave one review per work.

Video showing functionality here: https://youtu.be/3xoDOVof1Cs

The file structure is as follows:

Project 1
* static/
  * main.css: this contains all of the css styling for the site
* templates/
  * book_details.html: html for the book details and reviews page
  * error.html: html for when a user hits an error
  * homesearch.html: The landing/search page html
  * layout.html: The base html extended for all other pages
  * login.html: login page
  * registration.html: registration page
* application.py: handles all the backend logic
* book_load.py: script use to add books to database
* helpers.py: python logic that supports the primary flask application
* readme.md: this file
* requirement.txt: python libraries required to run the web app
