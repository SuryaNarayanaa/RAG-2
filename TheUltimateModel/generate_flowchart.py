from graphviz import Source
def generate_flow_chart(code ,question):
    graph_code = f'''{code}'''


    index = graph_code.find("}")
    
    
    
    # Include the length of the delimiter to include it in the first part
    index += len("}")
    
    # Split the string into two parts
    first_part = graph_code[:index]
    second_part = graph_code[index:]
    print(first_part)
    
    # Create a source object
    src = Source(first_part)
    save_path = f'./generated_flowchart/{question[:10]}'


    print(graph_code)

    # Render as PNG or SVG
    src.render(save_path, format='png') 

    return save_path 

