# Book Catalog App.

Book Catalog is a Python application that provides a list of items within 
a variety of categories as well as provide a user registration and 
authentication system. Registered users will have the ability to post, 
edit and delete their own items.

This app is a project for the Udacity [FSND](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004) Course.


### What I Should learned
 * How to develop a RESTful web application using the Python framework Flask.
 * Implementing third-party OAuth authentication.
 * Learn when to properly use the various HTTP methods available to me and how these methods relate to CRUD (create, read, update and delete) operations.
## Getting Started

### Prerequisites
Before run the project you should install these version:
* Python 2.7.
* Vagrant.
* VirtualBox.

### Installing

* Install Vagrant and VirtualBox.
* Clone the [Udacity Vagrantfile.](https://github.com/udacity/fullstack-nanodegree-vm)
* Clone this is app.
* Using Terminal turn Vagrant up, then run it.
```sh
$ vagrant up
$ vagrant ssh
```
* Go To catalog folder, then run the file application.
```sh
$ cd vagrant/catalog
$ python application.py
```
* The app will run using port of 5000.

## JSON Endpoints

* Returns JSON of all BookCatalog:
```python
/book_catalog/json
```

* Returns JSON of specific Book:
```python
/book_catalog/<int:bookcatalog_id>/list/<int:book_id>/json
```
* Returns JSON of Books in specific catalog:
```python
/book_catalog/<int:bookcatalog_id>/list/json
```