import pandas as pd
import matplotlib.pyplot as plt

# Read the data file
filename = 'SampleData.xlsx'  # or 'example.xlsx'
if filename.endswith('.csv'):
    data = pd.read_csv(filename)
else:
    data = pd.read_excel(filename)

# Detect the columns with numerical data
numerical_columns = []
for column in data.columns:
    if data[column].dtype in ['int64', 'float64']:
        numerical_columns.append(column)

# Create a bar chart and a pie chart for each numerical column
for column in numerical_columns:
    values = data[column]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

    # Create the bar chart
    ax1.bar(range(len(values)), values)
    ax1.set_title(f'{column} Bar Chart')
    ax1.set_xlabel('Index')
    ax1.set_ylabel(column)

    # Create the pie chart
    value_counts = values.value_counts()
    ax2.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%')
    ax2.set_title(f'{column} Pie Chart')

    plt.show()