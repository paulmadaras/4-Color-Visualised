# 4-Color Theorem Visualization and Implementation

## Introduction
This project brings to life the 4-Color Theorem, which states that any planar map can be colored with at most four colors such that no two adjacent regions share the same color. Using an interactive interface, users can draw shapes, compute adjacency relationships, and visualize the solution through a coloring algorithm.

## Project Objectives
- Provide an intuitive interface for drawing shapes representing a map.
- Compute adjacency relationships between shapes.
- Use **Mace4** to generate a coloring solution satisfying the 4-Color Theorem.
- Display the colored map to the user.

## Technologies Used
- **Python**: For GUI and computational logic.
- **Pygame**: To create an interactive drawing interface.
- **Mace4**: For logical reasoning and solving 4
- **Mace4**: For logical reasoning and solving the 4-coloring constraints.

## Technologies Used: Installation Guide

### 1. Installing Python and Pygame
- Download and install Python from [Python.org](https://www.python.org/).
- Install Pygame by running the following command:
  ```bash
  pip install pygame
### 2. Installing Mace4
Ensure Windows Subsystem for Linux (WSL) is installed on your system.
Install Mace4 by using the appropriate package manager commands or compile it from source.
Verify the installation by running:
bash
Copy code
mace4 --version
Methodology
### 1. 4-Color Theorem Rules in Mace4
Neighbors’ shapes must be of different colors.
Shapes can only have four distinct color indices (0, 1, 2, 3).
Shapes must be distinct, and no shape can overlap with another.
### 2. 4-Color Generation
### 2.1 Map Generation
Users draw shapes on a grid by creating black lines.
The system identifies shapes by detecting enclosed areas separated by black lines.
### 2.2 Translating the Input into Mathematics
An adjacency matrix is created to identify neighboring shapes.
The adjacency matrix is then converted to a Mace4-compatible format for constraint solving.
### 2.3 Integration with Python
Python automates the process of updating Mace4 files, writing new files, and running them in a subprocess.
The output from Mace4 is parsed to extract the color indices for each shape.
### 3. Graphical User Interface (GUI)
Users can draw shapes on a grid using black lines.
Shapes can be saved, triggering the computation of the solution.
Once the solution is computed, the user can view the colorized map.
### Future Enhancements
Improve neighbor detection algorithms to handle edge cases more accurately.
Optimize performance for larger grids.
Add undo/redo functionality to the GUI.
Improve the drawing and placement of blocks to handle gaps more effectively.
### Conclusion
This project provides an interactive and computational representation of the 4-Color Theorem. While effective in most cases, further refinement is needed to address specific edge cases in neighbor detection.

### Code Implementation
### 1. 4-Color Generation Code
### 1.1 Part 1: The Generation of the Grid
Python code sets up the grid and detects shapes drawn by the user.
### 1.2 Part 2: Updating the Mace4 File with the Starting Values
Mace4 files are dynamically generated with updated neighbor relations and constraints.
### 1.3 Part 3: Running Mace4
Python’s subprocess module executes Mace4 to solve the 4-color problem.
### 1.4 Part 4: Mace4 Output Parsing
The output from Mace4 is parsed to extract the color indices for each shape.
### 2. GUI Implementation
The GUI is implemented using Pygame and supports:
Drawing shapes on a grid.
Saving and colorizing shapes.
Viewing the result in real time.
### Quick Technical Guide for Running Your Project
### 1. Prerequisites
Python and Pygame must be installed on your system.
Mace4 must be installed and accessible via WSL.
### 2. Running the Application
Run the Python script to launch the GUI.
Draw shapes and press the Save button to start the computation.
View the colorized map in the same window.
### 3. Troubleshooting
Ensure that Mace4 is correctly installed and accessible.
Check for errors in the generation of the adjacency matrix.
Review the console output for detailed error messages.
