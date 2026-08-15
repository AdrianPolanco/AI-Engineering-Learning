code = """
console.log('Hello, World!');
console.log('This is a sample script generated from Python.');"""

with open("script.js", "w") as js_file:
    js_file.write(code)