import csv

def create_csv(csv_text, question):

    
    filename = f"./generated_tables/{question[:10]}.csv"
    # Split the text into lines
    start_index = csv_text.find("```") 
    
    end_index = csv_text[start_index+1:].find("```")
    end_index += start_index
    if start_index <0 and end_index <0 : 
        csv_text = csv_text
    else :
        
        csv_text = csv_text[start_index  : end_index]
        print(start_index ,end_index)

    lines = csv_text.strip().split('\n')

    print(csv_text)


    # Write the CSV file
    with open(filename, 'w', newline='') as file:
        file.write(csv_text)
    print("CSV file created successfully!")

    return filename
   