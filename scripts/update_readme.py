from datetime import datetime

today = datetime.now().strftime("%Y%m%d")

with open("README.md", "r") as f:
    readme = f.read()

readme = readme.replace("{{TODAY}}", today)

with open("README.md", "w") as f:
    f.write(readme)