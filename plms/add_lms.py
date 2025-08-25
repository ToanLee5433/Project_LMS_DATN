content = open("plms/settings.py", "r").read()
new_content = content.replace('    "users",\n]', '    "users",\n    "lms",\n]')
open("plms/settings.py", "w").write(new_content)
print("Added lms to INSTALLED_APPS")
