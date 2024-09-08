from graphviz import Source
from .searching import format_output


from langchain_community.llms import Ollama
# Paths
MODEL = "mistral"  # Use the Mistral model
model = Ollama(model=MODEL)
def generate_flow_chart(code ,question):
    graph_code = code


    index = graph_code.find("}")
    
    
    
    # Include the length of the delimiter to include it in the first part
    index += len("}")
    
    # Split the string into two parts
    first_part = graph_code[:index].replace("```", "")
    second_part = graph_code[index:]

    
    # Create a source objectfir
    src = Source(first_part)
    save_path = f'./generated_flowchart/{question[:10]}'

    print("FIRST PART : \n" , first_part)

    # Render as PNG or SVG
   
    src.render(save_path, format='png')
    return save_path

    # except Exception as e:
        
        
    #     prompt_text = f"""Consider you are a Graphviz debugger. Assume ypu are only given with the CODE and the ERROR, debug the CODE with maintaining the context of the CODE.
    #                     Your job is only to return the debugged code, and return nothing else

                        
    #                     NOTE : ONLY GENERATE THE CODE
    #                     NOTE : ONLY GENERATE THE CODE
                        
    #                     here is the code :
    #                       CODE : {first_part}
    #                     here is the error : 
    #                       ERROR : {e}"""+"""

    #                     here is the example graphvi syntax :
    #                       SYNTAX : Here’s the general structure:
                    
                    
    #                 digraph {
    #                     StartNode
    #                     ProcessNode
    #                     DecisionNode
    #                     EndNode
                        
    #                     StartNode -> ProcessNode
    #                     ProcessNode -> DecisionNode
    #                     DecisionNode -> EndNode
    #                     DecisionNode -> ProcessNode
    #                 }
    #                 Replace StartNode, ProcessNode, DecisionNode, and EndNode with appropriate node names based on the context.
    #                 Dont use the these name again in the code 
    #                     "StartNode
    #                     ProcessNode
    #                     DecisionNode
    #                     EndNode"



    #                     NOTE : ONLY GENERATE THE CODE



    #                     NOTE : ONLY GENERATE THE CODE
    #                     NOTE : ONLY GENERATE THE CODE"""
        
        
    #     # Generate a response using the Mistral model
    #     response = model(prompt_text)
    #     generate_flow_chart(response , question)
    
    


