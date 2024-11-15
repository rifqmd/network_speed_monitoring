# Program to read the entire file using read() function
file = open("../data/soal_chart_bokeh.txt", "r")
content = file.read()
print(content)
file.close()