from setuptools import setup, find_packages

setup(
    name='codescout',
    version='0.1',
    author='Vincent Fortin',
    author_email='vincent.fortin@gmail.com',
    description='Permet de creer des codes scouts',
    long_description="Cette première version de la librairie codescout permet d'encoder des messages à l'aide du code soleil et du code musical. Développé en préparation du Camporee de la Montérégie 2024. (C) Vincent Fortin 2024. [vincent.fortin@gmail.com](mailto:vincent.fortin@gmail.com)",
    long_description_content_type='text/markdown',
    url='https://github.com/vinfort/codescout',
    packages=find_packages(),  # Automatically find all packages in the project
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache-2.0',
        'Programming Language :: Python :: 3',
    ],
    python_requires='>=3.6',
    install_requires=[
        # List of dependencies required by your package
        'PIL>=5.1.1',
    ],
)
