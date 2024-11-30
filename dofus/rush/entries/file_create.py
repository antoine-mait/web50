import os

# Define the directory where the files are located
directory = r'D:\Coding\CS50\Web_programming\dofus\rush\entries'

# Function to create the next unused HTML file
def create_unused_html_file(directory, numbers):
    # Get a list of existing HTML files in the directory
    existing_files = [f for f in os.listdir(directory) if f.endswith('.html')]
    
    # Extract numbers from the filenames
    numbers = []
    for file in existing_files:
        try:
            # Extract the number from the file name (assuming format '001_name.html')
            num = int(file.split('_')[0])  # This splits by '_', takes the first part, and converts to int
            numbers.append(num)
        except ValueError:
            pass  # If there's no number in the filename, skip it

    # Find the next available number
    next_number = 1
    if numbers:
        next_number = max(numbers) + 1

    # Generate the filename
    filename = f"{next_number:03d}_unused.html"

    # Create the empty HTML file
    with open(os.path.join(directory, filename), 'w') as f:
        f.write('')
    
    print(f"Created file: {filename}")

# Initialize loop variables
i = 0
limit = 10

# Loop to create files until the limit is reached
while i < limit:
    create_unused_html_file(directory, i + 1)  # Pass i + 1 to make the file number start at 1
    i += 1
else:
    print("All files created.")