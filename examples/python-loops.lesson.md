---
lessond_version: "1.0"
title: "Python Loops: for and while"
language: "Python"
difficulty: "beginner"
topics: ["loops", "iteration", "control-flow"]
prerequisites: ["Python variables", "Python conditions"]
objectives:
  - Write a for loop to iterate over a list
  - Use while loops with a condition
  - Avoid infinite loops
created: "2025-01-01"
---

## Learning Objectives
- Understand the difference between `for` and `while` loops
- Iterate over sequences and ranges

## Prerequisites
Make sure you know how to create variables and write `if` statements before continuing.

## Content

### The `for` loop

Use `for` when you know in advance how many times to iterate.

```python
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print(fruit)
```

Use `range()` to iterate a fixed number of times:

```python
for i in range(5):
    print(i)  # prints 0 through 4
```

### The `while` loop

Use `while` when you want to keep looping until a condition becomes false.

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

Always make sure the condition eventually becomes false, or you will create an **infinite loop**.

## Exercises

1. Write a `for` loop that prints the numbers 1 to 10.
2. Use a `while` loop to sum numbers until the running total exceeds 100.
3. Loop over a list of names and print a greeting for each one.

## Further Reading

- [Python docs — for statements](https://docs.python.org/3/tutorial/controlflow.html#for-statements)
- [Python docs — while statements](https://docs.python.org/3/reference/compound_stmts.html#the-while-statement)
