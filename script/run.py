from scrap import main as scrap_main
from gemini import main as gemini_main
from notion import main as notion_main

if __name__ == "__main__":
    print(f"\n\n{"-"*50}")
    scrap_main()
    
    print(f"\n\n{"-"*50}")
    gemini_main()
    
    print(f"\n\n{"-"*50}")
    notion_main()
    
    print("All scripts have been executed")