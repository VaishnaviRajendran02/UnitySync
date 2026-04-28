import pandas as pd
needs = pd.read_excel('Need.csv.xlsx')
volunteers = pd.read_excel('volunteers.csv.xlsx')
print("Needs columns:", list(needs.columns))
print("Volunteers columns:", list(volunteers.columns))
print("\nNeeds head:")
print(needs.head(2))
print("\nVolunteers head:")
print(volunteers.head(2))
