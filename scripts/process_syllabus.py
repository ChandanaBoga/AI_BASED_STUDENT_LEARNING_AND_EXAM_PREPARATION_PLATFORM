from docling.document_converter import DocumentConverter
import os
import json

def process_syllabus():
    # Setup directories
    raw_dir = os.path.join("..", "database", "raw")
    indexed_dir = os.path.join("..", "database", "indexed")
    
    if not os.path.exists(indexed_dir):
        os.makedirs(indexed_dir)
        
    converter = DocumentConverter()
    
    # Process all PDFs in the raw directory
    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            if file.endswith(".pdf"):
                source_path = os.path.join(root, file)
                # Create relative path for output to maintain structure
                rel_path = os.path.relpath(root, raw_dir)
                output_folder = os.path.join(indexed_dir, rel_path)
                
                if not os.path.exists(output_folder):
                    os.makedirs(output_folder)
                    
                output_file = os.path.join(output_folder, file.replace(".pdf", ".md"))
                
                print(f"Processing {source_path}...")
                try:
                    result = converter.convert(source_path)
                    markdown_content = result.document.export_to_markdown()
                    
                    with open(output_file, "w", encoding="utf-8") as f:
                        f.write(markdown_content)
                    print(f"Successfully converted to {output_file}")
                except Exception as e:
                    print(f"Error processing {file}: {e}")

if __name__ == "__main__":
    process_syllabus()
