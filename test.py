from TheUltimateModel.handle_image_query import retrieve_images_by_text
import matplotlib.pyplot as plt

images  = retrieve_images_by_text("thyroid")
def display_images(image_similarity_list):
    plt.figure(figsize=(15, 5))  # Adjust the figure size as needed
    
    for i, (img, similarity) in enumerate(image_similarity_list):
        plt.subplot(1, len(image_similarity_list), i + 1)
        plt.imshow(img)
        plt.title(f"Similarity: {similarity:.2f}")
        plt.axis('off')
    
    plt.show()

display_images(images)