import re
# The string to be searched
text = "abc123"

pattern = r"(\d+)"
# Searching the text for the pattern
match = re.search(pattern, text)
# Checking if a match is found
if match:
 # Retrieving the first captured group
 captured_group = match.group(1)
 print("Captured Group:", captured_group)
else:
 print("No match found.")