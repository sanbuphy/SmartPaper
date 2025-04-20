from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [
        line.strip()
        for line in f
        if line.strip()
        and not line.strip().startswith("#")
        and not line.strip().startswith("--index-url")
    ]

setup(
    name="SmartPaper",
    version="0.1.0",
    description="智能论文处理工具",
    long_description="SmartPaper - 智能论文处理工具",
    long_description_content_type="text/markdown",
    author="SmartPaper开发团队",
    author_email="example@example.com",
    url="https://github.com/sanbuphy/SmartPaper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=requirements,
)
