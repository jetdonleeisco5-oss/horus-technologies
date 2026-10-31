# Question 1: Library Book Inventory Management

# Step 1: Create initial list of book titles
books = ["The Alchemist", "1984", "Moby Dick", "Pride and Prejudice"]
print("Initial inventory:", books)

# Step 2: Add two new books using append()
books.append("To Kill a Mockingbird")
books.append("The Great Gatsby")
print("After acquisitions:", books)

# Step 3: Remove damaged book using remove()
books.remove("Moby Dick")
print("After removing damaged book:", books)

# Step 4: Sort alphabetically and display using sort()
books.sort()
print("Final sorted book list:", books)