from datetime import datetime

today = datetime.now().strftime("%Y%m%d")

with open("readme.md", "r") as f:
    readme = f.read()

readme = readme.replace("{{TODAY}}", today)

with open("readme.md", "w") as f:
    f.write(readme)